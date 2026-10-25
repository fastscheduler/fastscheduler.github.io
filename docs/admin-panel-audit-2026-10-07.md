# Admin panel audit — 2026-10-07

Scope: admin panel, broadcast/ads, deep links, data views, downloads/exports, cross-cutting, RBAC/admins flows.
This document is an audit report only; no fixes are implied by the presence of a finding.

> Note (2026-10-07 coordinator pass): the supplied text begins mid-finding (tail of the DB-size finding, here tracked as H9). Findings H1–H8 header text was not included in the supplied material; only the findings below were triaged and fixed.

`src/callbacks/admin/panel.py:132-153` sums legacy JSON paths. The migrated store is `bot.db`/`stats.db`, while System Health reads those actual files. The Stats and System Health screens can show contradictory sizes, including 0 KB.

### H10 — Admin CSV exports use the wrong scheduled-job schema

`src/callbacks/export.py:1233-1238` reads `status`, `run_at`, `next_run`, and `uses`, but scheduled records use fields such as `datetime`, `channel_id`, and `content`, while recurring records use `channel` and `cron`. Export columns are therefore blank or misleading.

### H11 — Translation export omits admin translations

`src/callbacks/export.py:1192-1204` globs `translations/*.json` and misses `translations/admin/*.json`. A “translations backup” cannot restore the admin panel’s own language data.

### H12 — Russian admin panel localization is incomplete

`translations/admin/ru.json` contains only a small subset of admin keys. Most admin keys fall back to English; the existing key audit counted hundreds of RU fallbacks. `src/admin/handlers.py:648-650` also contains hardcoded English UI text. Two shared import keys (`import_quota_exceeded`, `import_too_many_messages`) are absent from all language files and can render literally.
**Status:** ✅ FIXED (2026-10-07) — button-builder footer moved to `broadcast.buttons_footer` (EN) / `broadcast_buttons_footer` (RU) plus RU `done_broadcast_btn`; files: src/admin/handlers.py:764, translations/admin/en.json:581, translations/admin/ru.json:143-144.

### H13 — Bulk actions are high-impact with weak transaction/confirmation boundaries

`src/callbacks/admin/bulk.py` can block entire Premium/free cohorts, grant Premium to all, and export users. The operations depend on in-memory iteration and broad mutation without a durable job record, resumable checkpoint, or post-operation reconciliation. A timeout can leave a partially changed cohort with no reliable completion report.

**Status:** ✅ FIXED (2026-10-07) — durable JSON job record with cohort snapshot created before mutation, checkpoint every 25 users, completed/failed/skipped reconciliation + explicit cohort-size confirmation (resume on interrupt); src/callbacks/admin/bulk.py:36-260, src/callbacks/admin/main.py:287-299.

### H14 — Blocked/revoked channel admins retain unguarded paths

Callback presses are checked in `src/buttons.py`, but text-driven conversations, sender-bot handlers, connect flows, and in-flight sessions do not consistently enforce the blocked state. Revoked records can remain in `user_channels`; self-heal may recreate access. Frozen channels are enforced at send time rather than at management time.
**Status:** ✅ FIXED (2026-10-07) — revoked gate added in buttons.py chadm_ dispatch (src/buttons.py:680) and at _recheck_or_deny entry (src/callbacks/channel_admins.py:248), frozen denies extended to grant/deny/toggle paths; files: src/callbacks/channel_admins.py:1138,1215,1241,1299,1311.

### H15 — Disconnect cleanup leaves stale RBAC state

Owner disconnect removes some channel-admin and transfer data but leaves permission requests, revoked markers, and limits (`src/callbacks/channels.py:1096-1101`). Reconnecting a channel can inherit old revocations/cooldowns, while dead channels accumulate orphaned state.
**Status:** ✅ FIXED (2026-10-07) — owner disconnect wipes admins/revoked/requests+cooldowns/transfers/limits via clear_channel_rbac_state with orphan purge (src/callbacks/channels.py:1142-1151,1226-1235); fresh-state helper at src/channels/admins.py:333.

### H16 — Ownership transfer can revert or corrupt state

`sync_channel_admins` creator-wins behavior can silently revert bot-side ownership changes; transfer acceptance does not consistently revalidate the current owner, migrate connections/jobs, or protect against duplicate pending transfers. Transient Telegram failures can also consume a valid pending request.
**Status:** ✅ FIXED (2026-10-07) — duplicates rejected at makeowner/confirm/create (src/callbacks/channel_admins.py:940,955; src/channels/admins.py:942), owner revalidated + connections/jobs migrated at accept (src/channels/admins.py:1048), transient failures keep the pending request (src/callbacks/channel_admins.py:1005).

### H17 — Admin export secrets persist in process memory and have weak expiry handling

`src/admin/export_center.py:299-406` stores password and packed export bytes in `context.user_data` until a short TTL or unpack action. Cleanup is best-effort, sends can fail silently, and failed/expired export state has no audit event. The design also relies on the per-chat context rather than a bounded, encrypted temporary store.

**Status:** ✅ FIXED (2026-10-07) — bounded LRU store (20 entries/24MB) with TTL on access + periodic sweeper, try/finally cleanup in all paths, export created/unpacked/expired/failed audits via log_admin_action, send failures surfaced; src/admin/export_center.py:30-200/300-560, src/callbacks/admin/exports.py:63-135.

## Medium findings

- **M1 — Voice broadcasts combine caption entities and HTML parse mode** (`src/admin/handlers.py:247-257`), causing Telegram rejection for that media type.
- **M2 — Poll/video-note broadcasts count follow-up messages incorrectly** and may leave orphaned text after deletion.
- **M3 — Blocked users are excluded from sent and failed counts**, so the displayed audience total cannot be reconciled.
**Status:** ✅ FIXED (2026-10-07) — `_broadcast_send` counts blocked users as `skipped` and returns `(sent, failed, skipped)`; all summaries render sent/failed/skipped-blocked so totals reconcile. Files: `src/admin/handlers.py:61,101,487`, `src/callbacks/admin/panel.py:497,508,545,556`, `translations/admin/en.json:66`.
- **M4 — Feedback dashboard buckets omit `closed`;** `all` differs from open+replied+spam (`src/admin/helpers.py`, `src/callbacks/admin/feedback.py`).
- **M5 — Token Health is not a live health check.** `src/callbacks/admin/analytics.py`/helpers inspect stored metadata but do not consistently call the live token verifier; decrypt failures can be mislabeled as revoked.
**Status:** ✅ FIXED (2026-10-07) — fleet collector live-verifies each bot via `_check_bot_token_valid` (5 concurrent max, ~10 min cache); decrypt failures render as unknown/key-issue, never revoked. Files: `src/admin/helpers.py:722,727,763,816`, `src/callbacks/admin/token.py:36,43`, `src/callbacks/admin/analytics.py:157`, `translations/admin/en.json:407`.
- **M6 — Sender-bot fleet view reads a removed `subscription` field**, so connected bots can appear Free even when the subscription service says otherwise.
- **M7 — Deep-link builder emits inconsistent action names and unauthenticated payloads.** Several catalog routes are silent no-ops; `sign/verify_deep_link` are not used; long-lived `from_bot_`/`ats_` tokens have no expiry.
**Status:** ✅ FIXED (2026-10-07) — builder generates payloads via `build_link()`/`get_all_targets()` with `parse()` round-trip validation; `from_bot_` attribution expires after 24h and `ats_` sessions after 1h (single-use pop retained), both graceful. Files: `src/callbacks/admin/panel.py:273,285,312`, `src/services/tracking.py:46,63,88`, `src/handlers/commands.py:358`, `src/services/models.py:1315,1318`.
- **M8 — No admin deep-link route exists for channel-admin flows.** Co-admins must navigate manually, and feature links can land in broken RBAC gates.
- **M9 — Per-admin statistics mix user/channel attribution with channel-wide reactions/leaderboards**, producing misleading profiles and undercounting on `int`/`str` ID or username normalization differences.
**Status:** ✅ FIXED (2026-10-07) — index/user/channel IDs normalized to `str` + migration-aware channel match; reactions labeled channel-wide via `stats_channel_wide_tag`. Files: src/core/botdata.py:716-868, src/callbacks/channel_admins.py:140-175/563-578, src/services/stats.py:279/776/822/1070-1082/1136, src/statistics_manager.py:332-340/412-413/519-531, src/channels/admins.py:597-602.
- **M10 — Permission changes lack a complete durable audit trail.** Some revoke paths omit `revoked_by`; an audit viewer can fail or omit important transitions.
**Status:** ✅ FIXED (2026-10-07) — all revoke paths record revoked_by+revoked_at (src/channels/admins.py:428), viewer tolerates legacy entries (src/channels/admins.py:1351; src/admin/helpers.py:705).
- **M11 — Permission-request notifications use the requester’s language and missing permission labels.** Russian or mixed-language recipients may see English/raw keys.
**Status:** ✅ FIXED (2026-10-07) — owner DM/buttons now render in the owner's language with EN-fallback perm labels (never raw keys). Files: src/callbacks/channel_admins.py:107-175 (_perm_label/_same_channel), :1325-1345 (_submit_request).
- **M12 — “Allow unblock requests” edits the wrong record and no complete unblock-request workflow exists.** Unblock also resets defaults rather than restoring prior permissions.
**Status:** ✅ FIXED (2026-10-07) — toggle edits the channel-level flag consulted by requests (src/callbacks/channel_admins.py:1276; src/channels/admins.py:396), manage-perm request→approve/deny→notify restores snapshot permissions (src/callbacks/channel_admins.py:1138; src/channels/admins.py:1331).
- **M13 — Admin view mode is a broad privilege switch.** It changes the admin’s normal interaction context and can expose ordinary-user flows without a clear scoped read-only boundary.
- **M14 — Admin panel and dashboard snapshots are not read under one lock.** Concurrent writes can make totals disagree between screens.

**Status:** ✅ FIXED (2026-10-07) — new collect_panel_snapshot() reads under one BOT_DATA_LOCK acquisition, shared by dashboard + system-health collectors (numbers unchanged); src/admin/helpers.py:41-175.
- **M15 — Long-running bulk broadcast/export/log operations have no bounded concurrency or resumable progress record.** Flood waits and worker restarts can produce partial results.
**Status:** ✅ FIXED (2026-10-07) — `_broadcast_send` fans out in `Semaphore(10)` chunks with FloodWait backoff kept, and persists a `broadcast_progress` record (sent/failed/skipped + done/total) to a new durable domain; stale `sending` jobs are marked failed on restore. Files: `src/admin/handlers.py:427,435`, `src/admin/broadcast_data.py:237,274,301`, `src/core/botdata.py:628`, `src/admin/scheduled.py:97,157`.
- **M16 — Several error handlers use `except Exception: pass`.** Telegram send failures, failed notifications, deletion failures, and export failures disappear from the admin’s view and from operational metrics.

**Status:** ✅ FIXED (2026-10-07) — failure lines added to admin summaries + log_suppressed() with context for broadcast/recurring-notify/backup/export/delete-giveup paths; pure UI cleanups untouched; src/admin/handlers.py:413-435/1040-1070, src/callbacks/admin/issues.py:108-230, src/services/periodic.py:616-680, src/callbacks/admin/analytics.py:239-270.

## Low findings and UX/maintenance issues

- Scheduled/recurring labels on the top panel historically omit count arguments, while the combined total includes them.
- Admin user lists often fall back to IDs because profile/cache data is not consistently populated.
- Transfer expiry and panel block/unblock changes notify nobody; dead inline buttons remain visible.
**Status:** ✅ FIXED (2026-10-07) — audited all buttons on touched renderers (broadcast footer + chadm profile/list); every `callback_data` has a handler branch, none removed. Files: tests/test_admin_audit_fixes_2026_10_07.py (test_admin_touched_buttons_all_wired).
**Status:** ✅ FIXED (2026-10-07) — transfer-expiry notifies owner+target via sweep (src/services/periodic.py:866; src/callbacks/channel_admins.py:1445; translations/en.json:5727-5728), block/unblock push on revoke/restore, missing keys added (translations/en.json:5656,5709).
- Permission notifications use raw channel IDs instead of channel titles.
**Status:** ✅ FIXED (2026-10-07) — pushes resolve titles with ID fallback (src/callbacks/channel_admins.py:175), request intro + remove confirm now titled (src/callbacks/channel_admins.py:891,1279).
- The English transfer phrase does not interpolate the actual channel/user while Russian does, creating different confirmation semantics.
**Status:** ✅ FIXED (2026-10-07) — EN phrase now interpolates {channel}/{username} exactly like RU (translations/en.json:5714; translations/ru.json:224).
- The owner’s language is used for some management menus instead of the acting admin’s language.
**Status:** ✅ FIXED (2026-10-07) — management menus render in the acting admin's language (t(user_id)), pushes in each recipient's language (src/callbacks/channel_admins.py:1332,1410,1465).
- Legacy dead modules and duplicate broadcast implementations substantially increase regression risk and make feature ownership unclear.
- Existing callback tests wrap handler calls in broad `try/except` blocks and can pass while the handler raises or renders nothing, creating false confidence.
**Status:** ✅ FIXED (2026-10-07) — new strict suite asserts on rendered text/markup with no swallowing; `test_chadm_profile_callback` tightened. Files: tests/test_admin_audit_fixes_2026_10_07.py, tests/unit/test_callbacks_channel_admins.py.

## Verified working areas

The audit also found working or mostly working components that should be preserved during fixes:

- Admin callback entry points consistently check `ADMIN_IDS` in the main panel modules.
- Channel-admin request/approve/deny mechanics and transfer handshake have passing simulation coverage in the existing reports.
- Telegram admin-sync code preserves records on transient API failures instead of immediately revoking them.
- Owner disconnect performs a channel-admin wipe for the primary RBAC store.
- Password-protected admin export packaging uses the existing backup encryption envelope; the remaining risks are scope, memory cleanup, and failure visibility.

## Priority remediation order

1. Lock down support-admin callbacks, token storage, backup scope/integrity, payment idempotency, and destructive restore semantics.
2. Replace permission aliases with canonical RBAC enforcement at every final action; fix blocked/frozen/revoked state handling and disconnect cleanup.
3. Choose one broadcast/ad implementation and delete or quarantine the dead one; implement persistent one-shot/recurring scheduling, buttons, parser parity, deletion retries, and resumable sends.
4. Repair revenue/Premium/date/stat/export schemas from a single source of truth and add reconciliation checks.
5. Complete admin translations and eliminate raw-key/hardcoded-English paths.
6. Add integration tests that exercise every page/button, restart recovery, Telegram API failures, duplicate callbacks, concurrent mutations, and cross-admin ownership journeys.

## Evidence index

Detailed evidence and earlier focused traces are retained in:

- `docs/bugs/admin-panel/01-broadcast-compose.md`
- `docs/bugs/admin-panel/02-ads-system.md`
- `docs/bugs/admin-panel/03-deep-links.md`
- `docs/bugs/admin-panel/04-admin-data-views.md`
- `docs/bugs/admin-panel/05-downloads-exports.md`
- `docs/bugs/admin-panel/06-cross-cutting.md`
- `docs/bugs/admins/01-permission-model.md`
- `docs/bugs/admins/02-permission-changes.md`
- `docs/bugs/admins/03-ownership-transfer.md`
- `docs/bugs/admins/05-per-admin-stats.md`
- `docs/bugs/admins/06-blocking.md`
- `docs/bugs/admins/07-notifications.md`
- `docs/bugs/admins/08-integration-journeys.md`

This document is an audit report only; no fixes are implied by the presence of a finding.
Filter files
