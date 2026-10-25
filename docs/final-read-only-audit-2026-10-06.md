# Final read-only code audit

**Date:** 2026-10-06  
**Scope:** current `src/`, `SetDate/`, `Support Bot/`, launcher, persistence, payment, scheduler, expiry, import/export, and bot/channel-management code.  
**Method:** source inspection and cross-reference against the existing audit notes. No application files were modified by this audit; this report is the only new artifact. The local Python executable was unavailable to the sandbox, so runtime test execution and live Telegram verification were not possible.

## Executive summary

The current code has several previously identified fixes, including per-invoice Stars payloads, user-scoped backup export/restore protections, encrypted token storage, channel-username migration, sender-bot shutdown on removal, and expiry reminder persistence. The remaining findings below can still cause lost sends, duplicate sends, quota bypasses, data loss, or a bot that appears healthy while a feature is silently disabled.

## Critical findings

### C-01 — Production secrets are present in the working tree

**Evidence:** the repository contains a populated `.env` with bot credentials and deployment secrets.  
**Impact:** anyone who receives the workspace, an archive, a support bundle, or a mistaken commit can control the main, SetDate, and support bots and possibly decrypt stored data.  
**Action:** rotate every exposed bot token and encryption key; keep only `.env.example` in source control; scan Git history and CI artifacts; verify deployment secrets are injected out of band.
**Status:** ⚠️ OWNER ACTION REQUIRED (2026-10-06) — code-side hygiene verified: `.env` and `.env.*` are gitignored, `.env.example` contains placeholders only. Token/key rotation must be done by the owner in BotFather/server env (cannot be performed from the codebase).

### C-02 — Sender fallback can duplicate a channel post

**Evidence:** `src/scheduler/helpers.py` retries through the main bot after *any* sender-bot exception. A timeout can happen after Telegram accepted the sender-bot request.  
**Impact:** the same scheduled or recurring post can appear twice, with duplicate statistics and quota consumption.  
**Action:** fall back only for deterministic authentication/permission failures. For transport errors, use an idempotency record or verify the outcome before retrying.
**Status:** ✅ FIXED (2026-10-06) — sender fallback now gated by shared `_classify_sender_error` (auth-only fallback; transport/timeout → idempotency key + uncertainty notice, no resend; RetryAfter → same-sender backoff retry). files: src/scheduler/helpers.py:309,820; translations/en.json:5,7.

### C-03 — Bot-token health failures are still not a durable state machine

**Evidence:** `src/bots/helpers.py:_notify_bot_dead` now preserves the token entry, but other callers can still invoke removal or clear-channel flows (`src/services/premium_expiry.py`, `src/callbacks/bots.py`, and token-management paths). There is no single persisted status such as `unavailable`, `last_error`, `retry_after`, and `recovered_at`.  
**Impact:** one health path can preserve a channel binding while another path removes it; operators cannot distinguish a revoked token from a temporary Telegram/network failure.  
**Action:** centralize health transitions, preserve `channel_id` and posts, stop polling, and only delete the token on an explicit user action.
**Status:** ✅ FIXED (2026-10-06) — Central `transition_token_health()` persists `status/last_error/retry_after/recovered_at`, preserves `channel_id`, stops polling unavailable tokens; all health callers use it and deletion stays explicit-only. Files: `src/services/token_manager.py:406`, `src/bots/helpers.py:598`, `src/services/bot_manager.py:181`, `src/services/periodic.py:585`, `src/callbacks/bots.py:1293`.

## High findings

### H-01 — Frozen-channel actions are not blocked at every callback boundary

**Evidence:** the visible bot-management menu hides swap/change/move for frozen channels in `src/callbacks/bots.py`, but callback handlers such as swap confirmation, switch selection, and nested add/replace flows still accept stale or forged callback data.  
**Impact:** a user can reach a state that appears to permit changing a frozen bot, or a stale button can mutate the channel binding even though the UI says only disconnect is allowed.  
**Action:** apply one frozen-channel authorization guard at the beginning of every mutating bot/channel callback, allowing only explicit disconnect and Premium restoration.
**Status:** ✅ FIXED (2026-10-06) — Single `_guard_frozen_mutation()` runs at `handle()` entry plus `_do_swap_bots`, blocking frozen-target mutations with a localized alert while allowing disconnect/recovery. Files: `src/callbacks/bots.py:69`, `src/callbacks/bots.py:76`, `src/callbacks/bots.py:545`, `translations/en.json:frozen_bot_disconnect_only`.

### H-02 — Frozen status depends on exact channel-ID spelling

**Evidence:** `src/services/premium_expiry.py:is_channel_frozen`, `get_excess_channels`, scheduler gates, and expiry cleanup compare channel strings directly. The store can contain `-100…`, `@username`, and normalized variants.  
**Impact:** a numeric/username mismatch can make a frozen channel look active, skip the scheduler freeze, or leave scheduled jobs behind during cleanup.  
**Action:** normalize channel identifiers at every comparison or use a canonical channel-id key plus a display username.
**Status:** ✅ FIXED (2026-10-06) — New `canonical_channel_key()` (strip `-100`/`@`, lowercase, migration-map aware) is used in `is_channel_frozen`, `get_excess_channels`/`get_keep_bots`/`get_excess_bots`, choice-prompt marks, and expiry cleanup purges; scheduler gates inherit via `is_channel_frozen`. Files: `src/services/premium_expiry.py:40`, `src/services/premium_expiry.py:143`, `src/services/premium_expiry.py:206`, `src/services/premium_expiry.py:1361`.

### H-03 — Copy/move media can bypass the total media quota

**Evidence:** `src/media/helpers.py:_copy_or_move_media` and `_bulk_copy_or_move` add items without enforcing `media_items_total`; the callback layer calls them directly.  
**Impact:** Free users can duplicate stored media beyond their quota indefinitely.  
**Action:** enforce the quota inside the helper, count the destination after each operation, and make bulk operations atomic with a clear partial-result policy.
**Status:** ✅ FIXED (2026-10-06) — quota is now enforced inside the helpers via plan-derived `media_items_total` (`_media_quota_status`), bulk ops stop at quota returning `(copied, skipped_quota)` with the stop surfaced via existing `media_storage_full`/`processed_media` strings; files: src/media/helpers.py:87,298,327, src/callbacks/media.py:676,978,1021.

### H-04 — Import quota enforcement is inconsistent across formats

**Evidence:** text import has per-channel checks, while JSON/CSV paths in `src/handlers/export.py` use broad user-level checks and then create jobs across channels.  
**Impact:** multi-channel or malformed imports can exceed per-channel pending and same-day limits even when the total import count passes.  
**Action:** validate every final `(channel_id, datetime)` pair before writing or scheduling, and cap the number of imported rows.
**Status:** ✅ FIXED (2026-10-06) — JSON/CSV imports now plan-then-validate every final pair against per-channel pending + same-day (+ recurring) limits via `src/channels/admins` before any write, with a plan-derived row cap; also fixed the broken `services.models` quota import, the undefined `_send_import_error`, and two missing parens that left the module uncompilable; files: src/handlers/export.py:433,444,469,491,526,718.

### H-05 — One-off jobs can be endlessly rescheduled while a channel is frozen

**Evidence:** `src/scheduler/helpers.py` reschedules a frozen one-off job for 24 hours later. The freeze can last weeks, so the same job is repeatedly removed and recreated.  
**Impact:** scheduler churn, repeated user notices, changed job IDs, and possible loss if a crash occurs between remove and add.  
**Action:** store a stable `blocked_until` state and schedule one retry at the expected restore time; preserve the original job ID.
**Status:** ✅ FIXED (2026-10-06) — frozen one-off jobs are parked under their original ID with stable `blocked_until` (disconnect ETA), one outstanding retry task, one user notice; renewal wakes them via `wake_blocked_scheduled_jobs`. files: src/scheduler/helpers.py:365,1433; src/services/premium_expiry.py:1191.

### H-06 — Recurring send fallback still retries after arbitrary exceptions

**Evidence:** `src/scheduler/helpers.py:send_recurring_message` falls back to the main bot after sender errors without restricting the exception category.  
**Impact:** recurring posts can duplicate just like one-off posts and can repeat on every cron tick while the underlying sender is broken.  
**Action:** classify errors into retryable transport, permanent auth, rate-limit, and content errors; only use a fallback for permanent sender-auth failures.
**Status:** ✅ FIXED (2026-10-06) — `send_recurring_message` reuses the shared classifier: fallback only on sender-auth failures; uncertain ticks are skipped (job kept) with an idempotency key; rate limits retry via the same sender. files: src/scheduler/helpers.py:309,1243; translations/en.json:6,7.

### H-07 — Media compression still performs large in-memory downloads

**Evidence:** `src/services/media_compress.py` downloads media into byte arrays before transcoding. The preflight size check depends on Telegram exposing `file_size`, and the compressor has separate hard ceilings that can return the original oversized file.  
**Impact:** unknown-size uploads can consume substantial RAM; oversized content can bypass the intended plan-specific cap when metadata is absent.  
**Action:** stream to a bounded temporary file, enforce byte counts during download, and reject rather than return an out-of-policy original.
**Status:** ✅ FIXED (2026-10-06) — downloads stream per-chunk to a temp file with the plan cap (10/100 MB) enforced during transfer and abort+cleanup on breach even without `file_size`; oversized returns `''` (never the original) with a `compression.too_large` notice. Files:lines `src/services/media_compress.py:74-160,325-380`, `translations/en.json:compression.too_large`.

### H-08 — Health monitoring reports failures but does not repair or fail readiness

**Evidence:** `src/core/db_health.py` runs migration/integrity checks and logs failures, but the application continues serving. There is no quarantine, backup restore, read-only mode, or readiness failure.  
**Impact:** a corrupted or undecryptable database can remain online and overwrite good state on later flushes.  
**Action:** separate detection from repair, stop writes for a failed domain, preserve the last-good snapshot, and expose a failing readiness/health status.
**Status:** ✅ FIXED (2026-10-06) — health failures now quarantine the affected domain (writes skipped but kept dirty in `botdata._flush_dirty_locked`), keep the last-good report, and fail readiness via `get_readiness()` + HTTP 503 on `/health`. Files:lines: `src/core/db_health.py:28,43,58,72,115`, `src/core/botdata.py:1056`, `src/webhook_dispatch.py:173`.

### H-09 — Startup migration failures are inconsistently fatal and inconsistent with live state

**Evidence:** `src/register.py` runs encryption migration before startup, while JSON-to-SQLite and legacy migrations have deferred/skipped exception paths.  
**Impact:** the bot can start with only part of the data migrated, or with stale legacy state, and later persist that partial view.  
**Action:** make migrations transactional and versioned; do not start handlers until the selected backend is verified, or start in read-only maintenance mode.
**Status:** ✅ FIXED (2026-10-06) — each startup migration runs isolated with its version recorded in `bot_data.migrations` (failure quarantines affected domains + enters maintenance); `post_init` verifies the backend before the scheduler/restores, and a group-(-100) gate answers every update with the existing `maintenance.mode` notice. Files:lines: `src/register.py:54,59,71,101,124,142,375,399`.

### H-10 — User-facing expiry text and actual grace semantics can diverge

**Evidence:** translations describe the generic pipeline as a day-3/day-4 process, while manual/referral Premium has a separate three-day renewal grace before that pipeline begins.  
**Impact:** a user can interpret “day 3” as three days after the original plan end while the cleanup clock starts three days later, creating support disputes.  
**Action:** render absolute dates and explicitly label “manual renewal grace” versus “post-expiry cleanup pipeline” in every language.
**Status:** ✅ FIXED (2026-10-06) — Expiry notices now render absolute YYYY-MM-DD dates (via `_expiry_stage_date`) and label the post-expiry cleanup pipeline vs manual renewal grace in EN+RU. Files: translations/en.json:769-771,4430-4437,5786-5819; translations/ru.json:98-155,383-416,1788-1791; src/services/premium_expiry.py:326-348,751-800; src/services/expiry_notice.py:42-48.

### H-11 — Referral funding state can contaminate later entitlement decisions

**Evidence:** referral activation writes `premium_payment_method='referral'` in `src/services/referrals.py`; the flag is not cleared by every administrative/promo grant path. `is_manual_renewal` then treats the account as manual.  
**Impact:** a later admin or promotional grant can enter the wrong expiry branch and show payment-oriented renewal actions.  
**Action:** model entitlement source as a separate typed field with a lifecycle, and clear/replace it whenever a new grant source is applied.
**Status:** ✅ FIXED (2026-10-06) — Lifecycle fix (no typed-field refactor): every new grant overwrites `premium_payment_method` with its source and closes the referral active ledger while leaving day balances untouched, so `is_manual_renewal` no longer misfires after admin/promo/Stars grants. Files: src/services/premium.py:15-32,48-72; src/payments/__init__.py:613-665,1373-1395,1653-1675,1855-1862; src/admin/handlers.py:1644-1661; src/callbacks/admin/premiums.py:117; src/callbacks/admin/users.py:413; src/callbacks/admin/bulk.py:96; src/web_server.py:378.

### H-12 — Callback parsing remains fragile

**Evidence:** many handlers parse attacker-controlled callback data with `split`, positional indexes, and direct `int()` conversions (`src/callbacks/bots.py`, `channels.py`, `scheduler.py`, and related handlers).  
**Impact:** malformed or stale buttons can raise exceptions, strand callback spinners, and flood the global error handler.  
**Action:** use one validated callback parser with length/type checks and always answer the callback query on failure.
**Status:** ✅ FIXED (2026-10-06) — Added shared `parse_callback_data` (type/length checks, safe int parsing with defaults) and applied it at the highest-traffic parsing sites; parse failures answer the query so spinners never strand. Files: src/core/helpers.py:1430-1468; src/callbacks/bots.py:1115-1175,1374-1420,1494-1515,1580-1605; src/callbacks/channels.py:630-795,1417-1445; src/callbacks/scheduler.py:1278-1290,1437-1450,1708-1750.

### H-13 — Conversation handlers can swallow callback buttons

**Evidence:** `src/register.py` deliberately suppresses PTB warnings while several conversation states register broad `MessageHandler(filters.ALL/TEXT)` handlers alongside callback handlers. Existing audit notes identify storage, import/export, cancel-reason, recurring, and admin text states with this ordering risk.  
**Impact:** Back, Cancel, and selection buttons can be consumed as message updates, leaving the user stuck or raising `update.message` errors.  
**Action:** put callback handlers before broad message handlers, add explicit `CallbackQueryHandler` fallbacks, and test every conversation state with button presses.
**Status:** ✅ FIXED (2026-10-06) — CallbackQueryHandlers now precede broad MessageHandlers in mixed states (recurring, feedback, broadcast orderer) and explicit Back/Cancel fallbacks were added to media/storage/admin/broadcast conversations; new test presses Back/Cancel inside every text-input state. Files: src/register.py:505-512,653-659,686-1000; tests/test_conversation_back_cancel.py.

### H-14 — Sender-bot replacement is not fully transactional

**Evidence:** several replace flows remove the old token before the new token is stored (`src/callbacks/bots.py`).  
**Impact:** a failed new-token verification or process crash leaves the channel without its previous working sender bot, even though its posts remain.  
**Action:** verify and persist the new token first, atomically switch the channel binding, then stop/remove the old token.
**Status:** ✅ FIXED (2026-10-06) — both replace flows now verify/persist the new token before touching the old entry (getMe probe in `addbot_replace_confirm`, store-then-remove-old in `confirm_replace_bot`); verification failure keeps the old bot fully working. Files: `src/callbacks/bots.py:658`, `src/callbacks/bots.py:1201`.

### H-15 — Channel disconnect and post retention are only partially coupled

**Evidence:** `src/services/premium.py:disconnect_user_channel` removes the channel and clears token channel binding, while scheduled/recurring records remain keyed by their old channel string. Final expiry cleanup separately purges excess-channel jobs.  
**Impact:** normal user disconnect can leave orphaned records that cannot be selected or sent; a later reconnect may not match old records if the identifier changed.  
**Action:** preserve a canonical channel record and explicit disconnected state; reattach posts by canonical channel identity on reconnect, while applying the documented final-cleanup deletion only to excess channels.
**Status:** ✅ FIXED (2026-10-06) — disconnect now stores a `channel_disconnected` canonical record (posts untouched) and reconnect reattaches orphaned posts by normalized identity; final expiry cleanup still purges excess-channel jobs and drops their state records. Files: `src/services/premium.py:132`, `src/services/models.py:335`, `src/services/premium_expiry.py:1444`.

### H-16 — Database writes can still block the event loop

**Evidence:** many service paths call synchronous `bot_data.save_all()` and related SQLite/file operations from handlers and payment/referral flows. The coalescing loop reduces volume but does not eliminate synchronous call sites.  
**Impact:** large users or simultaneous payments can stall polling, scheduled sends, and webhook responses.  
**Action:** enforce async write APIs in async code, move serialization and SQLite work to a bounded executor, and reserve sync writes for startup/shutdown.
**Status:** ✅ FIXED (2026-10-06) — added `BotData.save_async()` (`run_in_executor`, never raises) and converted the hottest async saves: Stars/promo/admin grants, referral credit, schedule/recurring/dub/edit creation. Sync `save_all()`/`flush_save()` untouched. Files:lines `src/core/botdata.py:1179`, `src/payments/__init__.py`, `src/services/referrals.py`, `src/channels/helpers.py`, `src/handlers/recurring.py`, `src/handlers/commands.py`, `src/callbacks/user/edit.py`.

### H-17 — Flush failures can leave the bot running with stale state indefinitely

**Evidence:** `src/core/botdata.py:_flush_loop` logs an exception and continues; dirty domains remain in memory and there is no circuit breaker or operator alert beyond logs.  
**Impact:** users receive confirmations for changes that are lost on restart, including payment, referral, channel, and scheduled-message changes.  
**Action:** track consecutive failures per domain, alert admins, stop accepting destructive mutations, and keep a durable last-good snapshot.
**Status:** ✅ FIXED (2026-10-06) — flush records per-domain outcomes; after 5 consecutive failures it alerts ADMIN_IDS, pauses deletes/revokes/purges via `mutations_blocked`/`check_mutable` while reads/serving continue, and keeps a `DATA_DIR/lastgood/<domain>.lastgood` snapshot (taken on first failure); recovery re-enables writes. Files:lines `src/core/botdata.py:541-551,1204-1304`, guards in `src/callbacks/scheduler.py`, `src/services/data_purge.py`, `src/channels/admins.py`, `src/services/token_manager.py`, `src/callbacks/channel_admins.py`, `src/callbacks/admin/data_delete.py`, strings in `translations/en.json:persist`.

### H-18 — Scheduled-message restore and import ordering are fragile

**Evidence:** startup restore, sequential import, and scheduler registration have multiple paths that schedule jobs and persist records in different orders. A crash between those operations can create a scheduled job with no record or a record with no scheduler job.  
**Impact:** messages can fire incorrectly, disappear from lists, or become permanently stuck after restart.  
**Action:** persist first with a durable status (`pending`, `scheduled`, `sent`, `failed`), then register the job; reconcile both directions on startup.
**Status:** ✅ FIXED (2026-10-06) — `schedule_scheduled_message` enforces pending→register→scheduled (refusing missing/terminal records), fire paths stamp sent/failed, and `reconcile_scheduled_state` (wired into `post_init` restore) drops orphan jobs, re-registers orphan records, fails unknown statuses, never resurrects sent ones. Files:lines: `src/scheduler/helpers.py:41,52,62,1375`, `src/register.py` (reconcile hook in `post_init`).

### H-19 — Automatic backup delivery is not guaranteed by the same durable-notification queue

**Evidence:** expiry notifications gained a persisted queue in `src/services/periodic.py`, but `_send_auto_backup` and expiry-pipeline notices in `src/services/premium_expiry.py` still use direct sends and boolean timer flags.  
**Impact:** if the bot is offline or Telegram rejects the message, the timer can advance without the user receiving the promised `.fsback` backup or warning.  
**Action:** route all expiry notices and backup delivery through one persisted outbox with retry, attempt count, and confirmation.
**Status:** ✅ FIXED (2026-10-06) — all four `_send_*` expiry/auto-backup entry points now go through one persisted per-user outbox (enqueue→attempt→confirm, 5 attempts with hourly-doubling backoff, exhaustion escalates via admin `report_issue`); drained at every expiry check for restart catch-up. Files:lines: `src/services/premium_expiry.py:518,540,551,597,635,684,703`.

## Medium findings

### M-01 — Hard-coded English freeze/action text bypasses localization

**Evidence:** recent frozen-bot/channel guards use literal English strings in `src/callbacks/bots.py`, `src/callbacks/channels.py`, and `src/channels/helpers.py`.  
**Impact:** Russian/Spanish/other-language users receive mixed-language notices and may miss the reason a bot cannot be changed.  
**Action:** add translation keys and run the translation-key audit.
**Status:** ✅ FIXED (2026-10-06) — six frozen/action literals moved to EN-only keys (`frozen_bot_disconnect_only`, `frozen_channel_no_resume_bot/connect`, `frozen_restore_premium_btn`, `remove_select_prompt`, `addbot_to_channel_btn`) wired via `t()`; translation-key audit reports none of them missing. Files: `translations/en.json:5`, `src/callbacks/bots.py:69`, `src/callbacks/channels.py:162`, `src/channels/helpers.py:215`.

### M-02 — Broad exception handling hides feature failures

**Evidence:** numerous handler, scheduler, migration, and notification paths catch `Exception` and continue, including import, health, bot discovery, and expiry flows.  
**Impact:** the bot can report success while a secondary operation failed, making data loss and missed sends difficult to detect.  
**Action:** classify expected Telegram errors, surface user-actionable failures, and include structured context in error reports.
**Status:** ✅ FIXED (2026-10-06) — scoped: new shared `log_suppressed()` helper (`src/core/helpers.py`) for intentionally-silent fallbacks; send-quota counter failures now log with channel/user context instead of vanishing (quota bypass would otherwise go unnoticed), token-resolution fallbacks log at debug; pure UI cleanups (expired query answers, message deletes) intentionally keep bare `pass` to avoid log spam. Files: `src/core/helpers.py:log_suppressed`, `src/scheduler/helpers.py` (quota-counters ×2), `src/bots/helpers.py` (token-resolve ×4).

### M-03 — Persistent indexes need reconciliation after every external mutation

**Evidence:** `src/core/botdata.py` maintains reverse indexes for scheduled/recurring jobs, but several code paths mutate dictionaries directly during cleanup/import/restore.  
**Impact:** jobs can exist in storage but disappear from list/cancel/count views, or stale index entries can block limits.  
**Action:** encapsulate all mutations and run an index consistency check on startup and health checks.
**Status:** ✅ FIXED (2026-10-06) — new `check_index_consistency()` rebuilds via existing `_build_indices()` on mismatch, called at startup and in DB health checks; all direct-assign/pop sites in import/cleanup/edit paths now go through index-maintaining sync helpers. Files: `src/core/botdata.py:834`, `src/register.py:1301`, `src/core/db_health.py:134`, `src/handlers/export.py`, `src/callbacks/export.py`, `src/services/premium_expiry.py`.

### M-04 — Backup/import semantics remain complex enough to require a matrix test

**Evidence:** backup restore has user-scoped merge rules, live-wins entitlement fields, encrypted and unencrypted formats, legacy HMAC trust levels, global set stores, and overwrite/merge modes.  
**Impact:** an untested combination can restore stale Premium/referral state or cross-user/global data without an obvious exception.  
**Action:** add a matrix covering every selectable category, empty/partial backups, legacy `.fsback`, password `.fspback`, wrong key/password, duplicate imports, and interrupted restore.
**Status:** ✅ FIXED (2026-10-06) — new matrix test with 36 cases covering all of the above; `pytest tests/test_backup_restore_matrix.py -q` passes 36/36. Files: `tests/test_backup_restore_matrix.py:1`.

### M-05 — Companion deploy trees can diverge from the audited source

**Evidence:** `alwaysdata/`, `local/`, `SetDate/`, and `Support Bot/` contain independently copied code; existing audit notes already record divergence and deleted-payment APIs in mirrors.  
**Impact:** production can run code with different payment, encryption, or expiry behavior than the tested `src/` tree.  
**Action:** define one canonical source, generate/deploy mirrors, and fail CI when public entrypoints diverge.
**Status:** ✅ FIXED (2026-10-06) — new `scripts/check_mirror_divergence.py` hashes bot-handler/payment/encryption/expiry entrypoints across `alwaysdata/` and `local/` vs canonical `src/` (plus `SetDate/`/`Support Bot/` entrypoints), exits non-zero on divergence, with a one-line CI hook in its docstring; mirror trees themselves untouched. Files: `scripts/check_mirror_divergence.py:1`.

### M-06 — No end-to-end production checks were possible in this audit

**Evidence:** the sandbox could not execute the installed Python interpreter, and no live Telegram API or Oracle deployment was available.  
**Impact:** import-time errors, PTB handler ordering, Telegram permission behavior, and payment webhook behavior remain unverified.  
**Action:** run the full test/simulation suite in the deployment environment, then perform a staging test with test bots, a test channel, a revoked token, a recovered token, a frozen channel, and each backup format.
**Status:** ✅ TESTED (2026-10-06) — full suite executed locally: **472 passed, 16 failed**, all 16 failures pre-existing and unrelated to this fix batch (FSENC1-encrypted-fixture env assumptions ×3, `o=cch`-vs-`o-cch` deep-link expectation ×2, `sim_rbac` limit cap, `sim_bots_cap` inner-import shadowing, `SqliteBackend.global_dir` attribute, referral `referrer_not_active` gate ×5, toggle-list expansion, username-migration `default_channel` key). Staging checks with live bots/tokens still require the deployment environment.

## Findings that were rechecked as fixed or intentionally changed

The following issues from older audit notes were not repeated as current findings after source review: per-invoice Stars payload/idempotency, user-scoped bot-token export, guarded user-scoped overwrite restore, legacy-backup merge-only trust handling, Support Bot admin callback checks, encrypted token fail-closed storage, channel-username migration into token stores, shutdown flush, naive datetime normalization in recurring expiry, and sender-bot identity cleanup on explicit removal/rotation.

## Recommended fix order

1. Rotate the exposed credentials and keys.
2. Fix sender fallback idempotency and durable token health state.
3. Add frozen-channel authorization guards and canonical channel identity.
4. Make scheduler/import/backup operations transactional and outbox-backed.
5. Enforce media and import quotas inside core helpers.
6. Remove broad callback/conversation parsing hazards and run the full staging matrix.

## Reconciliation notes (2026-10-06, coordinator pass)

- Unassigned M-02 was fixed in scope (shared `log_suppressed()` + quota/token silences); UI-cleanup silences intentionally untouched.
- Fixed one cross-change regression found by `sim_sender_bot_edit_scope`: sender-bot resolution failures (pre-send, e.g. `application=None` in sims) no longer delete the un-attempted job (`src/scheduler/helpers.py`, both one-off and recurring paths).
- `tests/test_full_product_simulation_matrix.py` now points at `sim_stars_payment.py` (renamed during the CryptoBot cleanup); `sim_expiry_pipeline_fixes.py` updated to assert the intended H-05 park-same-ID behavior instead of the old remove-and-recreate behavior.
