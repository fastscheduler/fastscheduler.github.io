#!/usr/bin/env python3
"""Remove simulation artifacts that leaked into a real data directory.

A UI timing simulation used to seed 112 fake users (bots ``sb1``…``sb112``,
channels ``@ch1``…``@ch112``) and ~2,120 fake scheduled messages, then call the
REAL save path — writing them into the live ``data/`` directory because it set
``cfg.DATA_DIR`` after the storage layer had already been imported. The admin
panel then showed thousands of messages and fake users for a bot that had just
been started from zero.

The leak is fixed in ``tests/management/sim_timing.py`` and every ``run_all.py``
(see ``tests/_hermetic.py``). This tool removes what the leak already wrote.

Dry run by default; ``--apply`` performs the cleanup after taking a backup.

    python tools/clean_sim_data.py                 # show the plan
    python tools/clean_sim_data.py --apply         # clean + backup
    python tools/clean_sim_data.py --data-dir PATH # work on another copy
"""

import argparse
import json
import re
import shutil
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SIM_CHANNEL_RE = re.compile(r'^@ch(\d+)?$')
SIM_BOT_RE = re.compile(r'^sb\d+$')
SIM_JOB_RE = re.compile(r'^s\d+_\d+$')
# Diagnostic stores that the simulation seeded with the same fake ids.
RBAC_STORES = ('channel_admins', 'channel_revoked', 'channel_limits',
               'permission_requests', 'pending_transfers')


def log(message: str) -> None:
    print(message, flush=True)


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _decode(blob):
    from src.core.security import decode_persisted_text
    return json.loads(decode_persisted_text(blob))


def _domain(conn, name):
    row = conn.execute('SELECT data FROM domains WHERE name = ?', (name,)).fetchone()
    return _decode(row['data']) if row else {}


def _records(conn, domain):
    return {r['key']: _decode(r['data'])
            for r in conn.execute('SELECT key, data FROM records WHERE domain = ?', (domain,))}


def plan_cleanup(data_dir: Path) -> dict:
    """Return what would be removed. Pure read: never writes."""
    db_path = data_dir / 'bot.db'
    plan = {
        'db': str(db_path),
        'sim_users': [],
        'sim_channels': [],
        'jobs': [],
        'domains': {},          # domain -> keys to delete
        'rbac': {},             # store -> keys to delete
        'dirs': [],
        'legacy_tracking': [],
    }
    if not db_path.exists():
        return plan

    conn = _connect(db_path)
    try:
        all_users = _domain(conn, 'all_users')
        user_channels = _domain(conn, 'user_channels')
        user_settings = _domain(conn, 'user_settings')
        user_stats = _domain(conn, 'user_stats')
        scheduled = _records(conn, 'scheduled_messages')
        rc_records = _records(conn, 'user_channels')
        rs_records = _records(conn, 'user_settings')
        rst_records = _records(conn, 'user_stats')
    finally:
        conn.close()

    # A simulation channel is literally @ch<number>.
    sim_channels = set()
    for _src in (user_channels, rc_records):
        for value in _src.values():
            values = value if isinstance(value, list) else [value]
            for ch in values:
                if isinstance(ch, str) and SIM_CHANNEL_RE.match(ch):
                    sim_channels.add(ch)

    # A simulation user: every channel it knows is a sim channel, its bots are
    # named sb<N>, and the account never registered through /start.
    real_users = set(all_users or {}) | set(user_stats or {}) | set(rst_records or {})
    sim_users = set()
    for uid, value in list(user_channels.items()) + list(rc_records.items()):
        uid = str(uid)
        if uid in real_users:
            continue
        values = value if isinstance(value, list) else ([value] if value else [])
        if not values or not all(isinstance(ch, str) and SIM_CHANNEL_RE.match(ch) for ch in values):
            continue
        settings = user_settings.get(uid) or rs_records.get(uid) or {}
        conns = (settings.get('bot_connections') or {}) if isinstance(settings, dict) else {}
        usernames = [c.get('bot_username') for c in conns.values() if isinstance(c, dict)]
        if usernames and not all(isinstance(u, str) and SIM_BOT_RE.match(u) for u in usernames):
            continue
        sim_users.add(uid)

    jobs = [jid for jid, msg in scheduled.items()
            if SIM_JOB_RE.match(str(jid))
            and isinstance(msg, dict)
            and isinstance(msg.get('channel_id'), str)
            and SIM_CHANNEL_RE.match(msg['channel_id'])]

    plan['sim_channels'] = sorted(sim_channels)
    plan['sim_users'] = sorted(sim_users, key=lambda x: (len(x), x))
    plan['jobs'] = sorted(jobs)
    for domain, keys in (
        ('user_channels', [u for u in sim_users]),
        ('user_settings', [u for u in sim_users]),
        ('user_stats', [u for u in sim_users]),
        ('all_users', [u for u in sim_users]),
    ):
        if keys:
            plan['domains'][domain] = keys

    # RBAC state seeded under the same ids. Besides @ch<N> channels, older sim
    # runs left records whose "user ids" are placeholders like 'owner'/'admin2'
    # — no Telegram account can ever own those, so they are safe to drop.
    conn = _connect(db_path)
    try:
        for store in RBAC_STORES:
            try:
                values = _domain(conn, store)
            except Exception:
                continue
            hits = []
            for key, value in values.items():
                if not isinstance(key, str):
                    continue
                placeholder_ids = False
                # Only channel_admins is keyed by user id; channel_limits is
                # keyed by setting name, so its non-numeric keys are normal.
                if store == 'channel_admins' and isinstance(value, dict) and value:
                    placeholder_ids = all(
                        isinstance(uid, str) and not uid.isdigit()
                        for uid in value.keys()
                    )
                if SIM_CHANNEL_RE.match(key) or placeholder_ids:
                    hits.append(key)
            if hits:
                plan['rbac'][store] = sorted(hits)
    finally:
        conn.close()

    # Per-user filesystem dirs (tokens/profiles) created by the sim.
    database_dir = data_dir / 'database'
    if database_dir.is_dir():
        for child in sorted(database_dir.iterdir()):
            if child.is_dir() and child.name in sim_users:
                plan['dirs'].append(str(child))

    # Legacy tracking written outside the data dir by the old bug.
    legacy = ROOT / 'src' / 'data'
    if legacy.is_dir():
        plan['legacy_tracking'] = [str(p) for p in legacy.iterdir() if p.is_file()]

    return plan


def apply_cleanup(data_dir: Path, plan: dict) -> dict:
    """Execute the plan. Returns a summary with the backup location."""
    stamp = time.strftime('%Y%m%d-%H%M%S')
    backup = data_dir / 'backups' / f'sim-cleanup-{stamp}'
    backup.mkdir(parents=True, exist_ok=True)

    db_path = data_dir / 'bot.db'
    for suffix in ('', '-wal', '-shm'):
        src = Path(str(db_path) + suffix)
        if src.exists():
            shutil.copy2(src, backup / src.name)
    if plan['dirs']:
        for p in plan['dirs']:
            shutil.copytree(p, backup / 'database' / Path(p).name, dirs_exist_ok=True)
    if plan['legacy_tracking']:
        legacy_backup = backup / 'legacy_tracking'
        legacy_backup.mkdir(parents=True, exist_ok=True)
        for p in plan['legacy_tracking']:
            shutil.copy2(p, legacy_backup / Path(p).name)

    removed = {'jobs': 0, 'domains': 0, 'rbac': 0, 'dirs': 0, 'legacy': 0}
    conn = _connect(db_path)
    try:
        with conn:
            for jid in plan['jobs']:
                removed['jobs'] += conn.execute(
                    "DELETE FROM records WHERE domain = 'scheduled_messages' AND key = ?",
                    (jid,)).rowcount
            for domain, keys in plan['domains'].items():
                for key in keys:
                    removed['domains'] += conn.execute(
                        'DELETE FROM records WHERE domain = ? AND key = ?',
                        (domain, key)).rowcount
                    # Domains may also be stored as one blob.
                    row = conn.execute('SELECT data FROM domains WHERE name = ?',
                                       (domain,)).fetchone()
                    if row:
                        try:
                            blob = _decode(row['data'])
                        except Exception:
                            blob = None
                        if isinstance(blob, dict) and key in blob:
                            blob.pop(key, None)
                            conn.execute('UPDATE domains SET data = ? WHERE name = ?',
                                         (_encode(blob), domain))
                            removed['domains'] += 1
            for store, keys in plan['rbac'].items():
                row = conn.execute('SELECT data FROM domains WHERE name = ?', (store,)).fetchone()
                if not row:
                    continue
                try:
                    blob = _decode(row['data'])
                except Exception:
                    continue
                if not isinstance(blob, dict):
                    continue
                changed = False
                for key in keys:
                    if key in blob:
                        blob.pop(key, None)
                        changed = True
                if changed:
                    conn.execute('UPDATE domains SET data = ? WHERE name = ?',
                                 (_encode(blob), store))
                    removed['rbac'] += len(keys)
    finally:
        conn.close()

    for p in plan['dirs']:
        shutil.rmtree(p, ignore_errors=True)
        removed['dirs'] += 1
    for p in plan['legacy_tracking']:
        try:
            Path(p).unlink()
            removed['legacy'] += 1
        except OSError:
            pass

    return {'backup': str(backup), 'removed': removed}


def _encode(value) -> str:
    from src.core.security import encrypt_file_content
    return encrypt_file_content(json.dumps(value, ensure_ascii=False))


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', default=None,
                        help='data directory to clean (default: the bot data dir)')
    parser.add_argument('--apply', action='store_true',
                        help='perform the cleanup (default is a dry run)')
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)
    import src.core.config as cfg

    data_dir = Path(args.data_dir).expanduser().resolve() if args.data_dir else Path(cfg.DATA_DIR)
    log(f'data directory: {data_dir}')
    log(f"mode: {'APPLY' if args.apply else 'DRY RUN'}")

    try:
        from src.core.security import _get_file_encryption_key
        if _get_file_encryption_key() is None:
            raise RuntimeError('FILE_ENCRYPTION_KEY is not configured; cannot read the store')
    except Exception as exc:
        log(f'FAILED: {exc}')
        return 2

    plan = plan_cleanup(data_dir)
    log(f"fake users:        {len(plan['sim_users'])}")
    log(f"fake channels:     {len(plan['sim_channels'])}")
    log(f"fake jobs:         {len(plan['jobs'])}")
    for domain, keys in plan['domains'].items():
        log(f"  {domain:16s} {len(keys)} entr(ies)")
    for store, keys in plan['rbac'].items():
        log(f"  {store:16s} {len(keys)} channel entr(ies)")
    log(f"filesystem dirs:   {len(plan['dirs'])}")
    log(f"legacy tracking:   {len(plan['legacy_tracking'])} file(s)")
    for uid in plan['sim_users'][:10]:
        log(f'  - user {uid}')
    if len(plan['sim_users']) > 10:
        log(f'  … and {len(plan["sim_users"]) - 10} more')

    if not args.apply:
        log('dry run: nothing was written')
        return 0
    if not (plan['jobs'] or plan['sim_users'] or plan['rbac'] or plan['dirs']):
        log('nothing to clean')
        return 0

    result = apply_cleanup(data_dir, plan)
    log(f"backup: {result['backup']}")
    log(f"removed: {result['removed']}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
