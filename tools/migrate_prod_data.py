#!/usr/bin/env python3
"""One-shot production data migration for the current release.

Run this ONCE on the production host after deploying the new code and BEFORE
starting the bots again. It is idempotent: running it twice changes nothing the
second time.

What it does
------------
1. Backs up the live data directory (SQLite snapshot + files) unless told not to.
2. Migrates every store to the current at-rest encryption format (AES-GCM) —
   the same serialized migration the bots run at startup, exposed here so it can
   be done deliberately, with a backup, and verified.
3. Fixes weekly recurring messages that were created with the old weekday
   numbering. APScheduler numbers weekdays Monday=0 … Sunday=6, but the old
   creation flow used Monday=1 … Sunday=0, so every weekly post fired one day
   late. Stored cron day_of_week values are remapped (old 0..6 -> new) and the
   human-readable schedule text (which was saved as "Weekly on  at 09:00") is
   regenerated in the owner's language.
4. Verifies the result: SQLite integrity, every domain/value decrypts and parses,
   every recurring cron is valid, and every stored message still has its owner
   and channel. Verification runs on the real files after the write; a failure
   exits non-zero and leaves the backup in place.

Usage
-----
    # 1. stop all three bots first (run.py, SetDate, Support Bot)
    python tools/migrate_prod_data.py                 # dry run, changes nothing
    python tools/migrate_prod_data.py --apply         # create backup + migrate
    python tools/migrate_prod_data.py --apply --skip-backup   # if you backed up yourself

Options
-------
    --data-dir PATH   migrate a copy instead of the configured DATA_DIR
    --scope data      only migrate the data directory (used by the test suite);
                      the default "project" also covers SetDate, Support Bot and
                      the legacy JSON stores
    --rescan          re-scan every file instead of trusting the migration marker
    --force           proceed even if the database looks like a bot is writing to it

Exit codes
----------
    0  success (or a dry run with no error)
    2  precondition failed (missing encryption key, database in use, ...)
    1  migration or verification failed
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Marker persisted in bot_data.migrations once the weekday remap has run.
WEEKLY_MARKER = 'release_2026_10_weekly_cron_v1'
# Revocations produced by the old deleted-account heuristic (getChat answered
# "chat not found" for users the bot had never messaged) are false positives.
RBAC_REPAIR_MARKER = 'release_2026_10_rbac_deleted_revoke_v1'

# Old creation flow -> APScheduler numbering: (old - 1) % 7.
# monday 1->0, tuesday 2->1, ..., saturday 6->5, sunday 0->6.
_DAY_KEYS = ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')

_CRON_RE = re.compile(r'^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$')
_NUMERIC_DOW_RE = re.compile(r'^[0-6]$')


try:
    # Localized schedule text contains non-ASCII characters; a cp1252 console
    # would otherwise crash the report (not the migration).
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


def log(message: str) -> None:
    print(f"[migrate] {message}", flush=True)


class PreconditionError(RuntimeError):
    """Raised when it is not safe to migrate (exit code 2)."""


# ---------------------------------------------------------------------------
# Backup
# ---------------------------------------------------------------------------

def _sqlite_snapshot(src_path: Path, dest_path: Path) -> None:
    """Consistent copy of a live SQLite database (safe with WAL)."""
    source = sqlite3.connect(f"file:{src_path}?mode=ro", uri=True)
    try:
        target = sqlite3.connect(str(dest_path))
        try:
            source.backup(target)
        finally:
            target.close()
    finally:
        source.close()


def backup_data_dir(data_dir: Path, dest: Path) -> dict:
    """Copy the data directory into ``dest``. Returns a small summary."""
    dest.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / 'bot.db'
    if db_path.exists():
        _sqlite_snapshot(db_path, dest / 'bot.db')
    copied = 0
    for path in data_dir.rglob('*'):
        if not path.is_file():
            continue
        if path.name.startswith('bot.db'):
            continue
        if path.suffix in {'.lock', '.tmp'}:
            continue
        target = dest / path.relative_to(data_dir)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(path, target)
            copied += 1
        except OSError as exc:
            log(f"warning: could not back up {path.name}: {exc}")
    return {'dir': str(dest), 'db': bool(db_path.exists()), 'files': copied}


def preflight_unreadable(data_dir: Path, scope: str) -> tuple[list[str], list[str]]:
    """List stores that cannot be decrypted, split into blocking and diagnosic.

    Diagnostic logs (``*.log``) may legitimately hold lines encrypted under a
    retired key; the migration leaves them alone. Any other store is user data,
    so it blocks the migration with its name instead of a bare decryption error.
    """
    from src.core.security import decode_persisted_text

    blocking: list[str] = []
    tolerated: list[str] = []

    roots = [data_dir]
    if scope == 'project':
        roots.extend([
            ROOT / 'SetDate',
            ROOT / 'Support Bot' / 'data',
            ROOT / 'src' / 'data',
        ])
    seen = set()
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob('*'):
            if not path.is_file() or path.suffix.lower() not in {'.json', '.jsonl', '.log'}:
                continue
            if path.name.endswith(('.fsback', '.fspback', '.lock', '.tmp')):
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            try:
                for line in path.read_text(encoding='utf-8-sig').splitlines():
                    if line.strip():
                        decode_persisted_text(line)
            except Exception:
                # Diagnostic stores (``*.log`` and anything under a logs/
                # directory, e.g. data/logs/bot_structured.json) may hold lines
                # encrypted under a retired key. The bots leave those untouched
                # at startup, so the migration must not refuse to run because of
                # them — only real user data blocks.
                _parts = [part.lower() for part in path.parts]
                _diagnostic = (
                    path.suffix.lower() == '.log'
                    or 'logs' in _parts
                    or 'log' in path.stem.lower()
                )
                target = tolerated if _diagnostic else blocking
                target.append(str(path.relative_to(ROOT) if ROOT in path.parents else path))

    db_path = data_dir / 'bot.db'
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            tables = {row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
            checks = {
                'domains': ('SELECT name AS label, data FROM domains',),
                'records': ('SELECT domain || "/" || key AS label, data FROM records',),
                'tokens': ('SELECT user_id AS label, data FROM tokens',),
                'rate_limits': ('SELECT id AS label, timestamps AS data FROM rate_limits',),
            }
            for table, (sql,) in checks.items():
                if table not in tables:
                    continue
                for row in conn.execute(sql).fetchall():
                    try:
                        json.loads(decode_persisted_text(row['data']))
                    except Exception:
                        blocking.append(f"{table}:{row['label']}")
        finally:
            conn.close()
    return blocking, tolerated


def _database_busy(data_dir: Path) -> bool:
    """Heuristic: a freshly written WAL means a bot is probably still running."""
    wal = data_dir / 'bot.db-wal'
    try:
        return wal.exists() and (time.time() - wal.stat().st_mtime) < 120
    except OSError:
        return False


# ---------------------------------------------------------------------------
# Recurring-message repair
# ---------------------------------------------------------------------------

def _cron_fields(msg: dict) -> list[str] | None:
    match = _CRON_RE.match(str(msg.get('cron') or '').strip())
    return list(match.groups()) if match else None


def plan_weekly_fix(rec: dict, translate) -> list[dict]:
    """Describe the changes needed for stored recurring messages.

    Returns a list of ``{job_id, user_id, old_cron, new_cron, old_schedule,
    new_schedule}`` entries. Pure function: nothing is mutated.
    """
    planned: list[dict] = []
    for job_id, msg in (rec or {}).items():
        if not isinstance(msg, dict):
            continue
        fields = _cron_fields(msg)
        if not fields:
            continue
        minute, hour, day, month, dow = fields
        weekly_shape = day == '*' and month == '*' and _NUMERIC_DOW_RE.match(dow) is not None
        if not weekly_shape:
            continue
        new_cron = None
        if _NUMERIC_DOW_RE.match(dow):
            # Always remap: values were written with the old numbering.
            new_cron = f"{minute} {hour} {day} {month} {(int(dow) - 1) % 7}"
        schedule = str(msg.get('schedule') or '')
        # The buggy flow stored a weekly description with an empty weekday,
        # which always contains a double space ("Weekly on  at 09:00").
        broken_schedule = not schedule.strip() or re.search(r'\s{2,}', schedule) is not None
        new_schedule = None
        if broken_schedule:
            new_day = int((int(dow) - 1) % 7)
            try:
                day_label = translate(str(msg.get('user_id') or '0'), _DAY_KEYS[new_day], default=_DAY_KEYS[new_day].capitalize())
            except Exception:
                day_label = _DAY_KEYS[new_day].capitalize()
            try:
                new_schedule = translate(
                    str(msg.get('user_id') or '0'), 'weekly_schedule',
                    day=day_label, time=f"{int(hour):02d}:{int(minute):02d}",
                )
            except Exception:
                new_schedule = f"Weekly on {day_label} at {int(hour):02d}:{int(minute):02d}"
        if new_cron or new_schedule:
            planned.append({
                'job_id': job_id,
                'user_id': msg.get('user_id'),
                'old_cron': msg.get('cron'),
                'new_cron': new_cron or msg.get('cron'),
                'old_schedule': schedule,
                'new_schedule': new_schedule if new_schedule is not None else schedule,
            })
    return planned


def apply_weekly_fix(rec: dict, planned: list[dict]) -> int:
    changed = 0
    for entry in planned:
        msg = rec.get(entry['job_id'])
        if not isinstance(msg, dict):
            continue
        if entry['new_cron'] != entry['old_cron']:
            msg['cron'] = entry['new_cron']
        if entry['new_schedule'] != entry['old_schedule']:
            msg['schedule'] = entry['new_schedule']
        changed += 1
    return changed


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def plan_rbac_deleted_repair(bot_data) -> list:
    """Find admin revocations that the buggy deleted-account heuristic wrote.

    Only ``reason == 'deleted'`` entries are considered: those were created when
    ``Bot.get_chat(uid)`` raised "chat not found", which Telegram answers for any
    user the calling bot has never talked to. Every one of them detached the
    channel from a live admin (``revoke_channel_admin`` drops the channel from
    that user's connected list) and barred the auto-sync from re-adding them.
    """
    planned = []
    revoked_store = getattr(bot_data, 'channel_revoked', {}) or {}
    if not isinstance(revoked_store, dict):
        return planned
    for channel, users in revoked_store.items():
        if not isinstance(users, dict):
            continue
        for uid, entry in users.items():
            if isinstance(entry, dict) and str(entry.get('reason', '')).lower() == 'deleted':
                planned.append({
                    'channel': str(channel),
                    'user_id': str(uid),
                    'revoked_at': str(entry.get('revoked_at', '')),
                })
    return planned


def apply_rbac_deleted_repair(bot_data, planned: list) -> int:
    """Clear the false revocations and re-attach the channel to each user."""
    fixed = 0
    revoked_store = getattr(bot_data, 'channel_revoked', {}) or {}
    for item in planned:
        channel, uid = item['channel'], item['user_id']
        users = revoked_store.get(channel)
        if isinstance(users, dict):
            users.pop(uid, None)
            if not users:
                revoked_store.pop(channel, None)
        raw = bot_data.user_channels.get(uid)
        if raw is None:
            bot_data.user_channels[uid] = [channel]
        elif isinstance(raw, list):
            if channel not in [str(c) for c in raw]:
                raw.append(channel)
        elif isinstance(raw, str):
            if raw != channel:
                bot_data.user_channels[uid] = [raw, channel]
        elif isinstance(raw, dict):
            if channel not in [str(v) for v in raw.values()]:
                raw[str(len(raw))] = channel
        fixed += 1
    return fixed


def verify_store(data_dir: Path) -> dict:
    """Verify the on-disk store: integrity, decryption, parsing, cron validity."""
    from src.core.security import decode_persisted_text

    db_path = data_dir / 'bot.db'
    if not db_path.exists():
        raise RuntimeError(f"no database at {db_path}")

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        integrity = conn.execute('PRAGMA integrity_check').fetchone()[0]
        if str(integrity).lower() != 'ok':
            raise RuntimeError(f"SQLite integrity check failed: {integrity}")
        tables = {row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        domain_rows = 0
        if 'domains' in tables:
            for row in conn.execute('SELECT name, data FROM domains').fetchall():
                json.loads(decode_persisted_text(row['data']))
                domain_rows += 1
        record_rows = 0
        if 'records' in tables:
            for row in conn.execute('SELECT domain, key, data FROM records').fetchall():
                json.loads(decode_persisted_text(row['data']))
                record_rows += 1

        recurring = {}
        if 'domains' in tables:
            row = conn.execute(
                "SELECT data FROM domains WHERE name = 'recurring_messages'").fetchone()
            if row:
                parsed = json.loads(decode_persisted_text(row['data']))
                recurring = parsed if isinstance(parsed, dict) else {}
    finally:
        conn.close()

    from apscheduler.triggers.cron import CronTrigger

    problems = []
    for job_id, msg in recurring.items():
        if not isinstance(msg, dict):
            problems.append(f"{job_id}: not an object")
            continue
        if not msg.get('user_id'):
            problems.append(f"{job_id}: missing user_id")
        if not msg.get('channel_id'):
            problems.append(f"{job_id}: missing channel_id")
        fields = _cron_fields(msg)
        if not fields:
            problems.append(f"{job_id}: unparsable cron {msg.get('cron')!r}")
            continue
        try:
            CronTrigger(minute=fields[0], hour=fields[1], day=fields[2],
                        month=fields[3], day_of_week=fields[4])
        except Exception as exc:
            problems.append(f"{job_id}: invalid cron {msg.get('cron')!r} ({exc})")
    if problems:
        raise RuntimeError("verification found problems:\n  " + "\n  ".join(problems[:20]))

    return {
        'domains': domain_rows,
        'records': record_rows,
        'recurring': len(recurring),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Migrate production data for the current release (idempotent).',
    )
    parser.add_argument('--apply', action='store_true',
                        help='write changes (default is a dry run)')
    parser.add_argument('--data-dir', default=None,
                        help='data directory to migrate (default: configured DATA_DIR)')
    parser.add_argument('--backup-dir', default=None,
                        help='where to put the pre-migration backup')
    parser.add_argument('--skip-backup', action='store_true',
                        help='do not create a backup (only if you already have one)')
    parser.add_argument('--scope', choices=('project', 'data'), default='project',
                        help='"project" migrates every store; "data" only the data directory')
    parser.add_argument('--rescan', action='store_true',
                        help='re-scan files even if the migration marker exists')
    parser.add_argument('--force', action='store_true',
                        help='proceed even if the database looks actively written')
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)

    import src.core.config as cfg

    if args.data_dir:
        cfg.DATA_DIR = Path(args.data_dir).expanduser().resolve()
        os.environ['DATA_DIR'] = str(cfg.DATA_DIR)

    data_dir = Path(cfg.DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)
    apply_changes = bool(args.apply)

    log(f"data directory: {data_dir}")
    log(f"mode: {'APPLY' if apply_changes else 'DRY RUN'} (scope={args.scope})")

    try:
        from src.core.security import _get_file_encryption_key

        if _get_file_encryption_key() is None:
            raise PreconditionError(
                'FILE_ENCRYPTION_KEY is not configured. At-rest migration cannot run '
                'without it; set it in .env exactly as on the bots.'
            )

        if apply_changes and not args.force and _database_busy(data_dir):
            raise PreconditionError(
                'bot.db-wal was written in the last 2 minutes, so a bot may still be '
                'running. Stop run.py, SetDate and Support Bot first (or pass --force).'
            )

        if apply_changes and not args.skip_backup:
            stamp = time.strftime('%Y%m%d-%H%M%S')
            backup_dir = Path(args.backup_dir) if args.backup_dir else (
                data_dir.parent / 'backups' / f'migrate-{stamp}')
            info = backup_data_dir(data_dir, backup_dir)
            log(f"backup written: {info['dir']} ({info['files']} files, db={info['db']})")

        # 0) Preflight: name the stores that would block the migration.
        blocking, tolerated = preflight_unreadable(data_dir, args.scope)
        if tolerated:
            log(f"note: {len(tolerated)} diagnostic log file(s) contain unreadable "
                f"lines and will be left untouched: {', '.join(tolerated[:5])}")
        if blocking:
            raise PreconditionError(
                "these stores cannot be decrypted with the configured key and would "
                "abort the bots at startup:\n  " + "\n  ".join(blocking[:20])
                + "\nRestore them from a backup, or remove/repair the damaged store, "
                  "then re-run this script."
            )

        # 1) At-rest encryption (serialized, resumable, fail-closed).
        from src.core.data_encryption import migrate_all_project_stores, migrate_data_stores
        from src.core.db import db as _db

        if apply_changes:
            if args.scope == 'project':
                enc = migrate_all_project_stores(force_scan=args.rescan)
            else:
                enc = migrate_data_stores([data_dir], db=_db, force_scan=args.rescan)
            log(f"at-rest encryption: {enc}")
        else:
            log('at-rest encryption: skipped in dry run (offline check only)')

        # 2) Weekly recurring repair.
        from src.core.botdata import bot_data
        from src.core.i18n import t

        marker = {}
        try:
            marker = bot_data.migrations.get(WEEKLY_MARKER) or {}
        except Exception:
            marker = {}

        rec = bot_data.recurring_messages if isinstance(bot_data.recurring_messages, dict) else {}
        log(f"recurring messages: {len(rec)}")

        planned = plan_weekly_fix(rec, t)
        if marker.get('done'):
            log(f"weekly cron remap already applied on {marker.get('at', 'an earlier run')}; "
                f"nothing to remap ({len(planned)} job(s) still look weekly)")
            planned = []
        else:
            log(f"weekly cron remap: {len(planned)} job(s) need updating")
            for entry in planned[:10]:
                log(f"  {entry['job_id']} (user {entry['user_id']}): "
                    f"{entry['old_cron']!r} -> {entry['new_cron']!r}; "
                    f"schedule {entry['old_schedule']!r} -> {entry['new_schedule']!r}")
            if len(planned) > 10:
                log(f"  … and {len(planned) - 10} more")

        changed = 0
        if apply_changes:
            if planned:
                changed = apply_weekly_fix(rec, planned)
            if not marker.get('done') or changed:
                bot_data.migrations[WEEKLY_MARKER] = {
                    'done': True,
                    'at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'jobs': changed,
                }
            # 3) RBAC: release admins detached by the old deleted-account guess.
            rbac_marker = {}
            try:
                rbac_marker = bot_data.migrations.get(RBAC_REPAIR_MARKER) or {}
            except Exception:
                rbac_marker = {}
            rbac_planned = plan_rbac_deleted_repair(bot_data)
            if rbac_marker.get('done'):
                log(f"rbac false-revoke repair already applied on "
                    f"{rbac_marker.get('at', 'an earlier run')} "
                    f"({len(rbac_planned)} suspect entr(ies) still present)")
            else:
                log(f"rbac false-revoke repair: {len(rbac_planned)} "
                    f"admin record(s) to release")
                for entry in rbac_planned[:10]:
                    log(f"  channel {entry['channel']}: user {entry['user_id']} "
                        f"(revoked at {entry['revoked_at'] or 'unknown'})")
                if len(rbac_planned) > 10:
                    log(f"  … and {len(rbac_planned) - 10} more")
            rbac_fixed = 0
            if not rbac_marker.get('done'):
                rbac_fixed = apply_rbac_deleted_repair(bot_data, rbac_planned)
                bot_data.migrations[RBAC_REPAIR_MARKER] = {
                    'done': True,
                    'at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'released': rbac_fixed,
                }
                log(f"rbac false-revoke repair: {rbac_fixed} admin(s) reconnected")

            bot_data.save_all()
            log(f"weekly cron remap: {changed} job(s) updated and saved")

            # Close our handle so verification reads the flushed files.
            try:
                _db._get_conn().close()
            except Exception:
                pass

            result = verify_store(data_dir)
            log(f"verification ok: {result}")
        else:
            log('dry run: no data was written')

        log('done')
        return 0
    except PreconditionError as exc:
        log(f"PRECONDITION FAILED: {exc}")
        return 2
    except Exception as exc:  # noqa: BLE001 - the operator needs the reason
        log(f"FAILED: {type(exc).__name__}: {exc}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
