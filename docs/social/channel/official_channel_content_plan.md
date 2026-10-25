# Content Plan & Navigation for the Official Fast Scheduler Channel

> Source file upgraded and moved here from `Downloads/official_fast_schedule_channel_posts.md`.
> Every guide below was verified against the real bot code and translation strings.
> A full list of fixed mistakes is at the bottom (§9 Fix log).

## 📌 1. Navigation system (hashtag categories)

Every post carries its hashtags so subscribers can tap to filter:

* `#navigation` — pinned post, key guides, index
* `#guide` — step-by-step setup and usage tutorials
* `#features` — feature breakdowns (inline buttons, recurring, calendar, stats…)
* `#updates` — release notes (current version: **v2.4.7**)
* `#tips` — formatting and channel-growth hacks
* `#faq` — questions and troubleshooting
* `#premium` — Premium plans and referral program

---

## 📌 2. Pinned message (main navigation hub)

📍 **Welcome to the official Fast Scheduler channel!**

**Fast Scheduler** (@FastSchedulerBot) schedules your Telegram channel posts, repeats them on autopilot with `/recurring`, and shows per-post stats — all from one chat.

🔍 **Quick navigation:**

• `#guide` — connect your channel in about a minute
• `#features` — inline buttons, recurring posts, calendar, stats
• `#tips` — formatting that keeps posts crisp
• `#faq` — post didn't send? start here
• `#updates` — what's new in each release

🚀 **Links:**
Launch bot: https://t.me/FastSchedulerBot
Support: https://t.me/FastSchedulerSupport_bot

`#navigation #pinned`

---

## 📌 3. Post 1 — Quick start: connect your channel

📖 **Connect Fast Scheduler to your channel in about a minute**

**Step 1.** In your channel: `Channel Settings` → `Administrators` → `Add Admin` → `@FastSchedulerBot` (needs **Post Messages** permission).
**Step 2.** Open @FastSchedulerBot and send it one of these:
• your public link (`@yourchannel` or `https://t.me/yourchannel`), or
• a private invite link, or
• **any forwarded message** from the channel.
**Step 3.** The bot checks you are a channel admin and connects it. Done — now send `/schedule`!

💡 *Free plan covers 1 channel, up to 100 pending posts and 1 recurring post. Need more? See `#premium`.*

`#guide #quickstart`

---

## 📌 4. Post 2 — Inline buttons (real syntax)

✨ **Clickable buttons under your posts — the exact syntax**

Fast Scheduler turns markup inside your post text into real Telegram buttons:

```
<inline>Buy now<link="https://site.com">
<inline>Support<link="https://t.me/FastSchedulerSupport_bot" style="success">
```

• `style=` is optional: `primary`, `success` or `danger` (colored buttons).
• Put `--` **between** two buttons to keep them side by side.
• Put `//` (or a line break) between buttons to start a **new row**.
• Broken markup is never deleted silently — the bot warns you before scheduling.

Try it: schedule a test post to yourself first, then to the channel.

`#features #inline_buttons`

---

## 📌 5. Post 3 — Recurring posts + bulk import

🔁 **Stop reposting the same thing manually — use `/recurring`**

Daily digest at 09:00? Weekly promo every Monday? `/recurring` in @FastSchedulerBot repeats any post **daily, weekly, monthly or yearly** — set it once and forget it.

📥 **Moving a content plan over?** Import it instead of retyping:
• from a backup/export file via `/import`,
• or bulk dates from the SetDate bot, then import here.

`#features #recurring #import`

---

## 📌 6. Post 4 — Formatting cheatsheet

💡 **4 rules for readable Telegram posts**

1️⃣ **Air.** No walls of text — 3–4 short lines per paragraph max on mobile.
2️⃣ **Monospace** for codes and links: wrap with backticks `` `text` ``.
3️⃣ **Spoilers** with `||text||` — great for quizzes and teasers.
4️⃣ **Spacing is safe.** Fast Scheduler keeps your line breaks and styles exactly as you sent them.

`#tips #content`

---

## 📌 7. Post 5 — FAQ

❓ **Frequently asked questions**

**Is the bot safe? Does it touch my personal account?**
Yes, it's safe. It only needs channel-admin rights to publish. It never sees your personal chats.

**What timezone are posts sent in?**
Yours. Set it with `/timezone` (per account and per channel) and change language with `/language`.

**A post didn't go out. What now?**
Check that @FastSchedulerBot is still a channel admin with posting rights, then look at your message list — failed posts show what happened.

Still stuck? → https://t.me/FastSchedulerSupport_bot

`#faq #help`

---

## 📌 8. Release template + current changelog (v2.4.7)

🚀 **Fast Scheduler v2.4.7 is live**

**What's new:**
✅ **Traffic Sources panel** — share `?start=threads` style links and see exactly which source and post brought each user, right in the admin panel.
✅ **Translation audit** — all missing keys added, dead keys removed, zero gaps.
✅ **Faster, safer start flow** with source attribution that never breaks deep links.

Update template for future releases: version number, 3–5 bullets, one link to try it.

`#updates`

---

## 📌 9. Fix log (what was wrong in the original draft)

1. **Bot name** — "Fast Schedule" → "Fast Scheduler" everywhere (including title and all posts).
2. **Post 1 flow was fictional** — the bot does NOT "auto-detect your channel when you send your first post". Real flow: add as admin → send link/forward → admin check → `/schedule`. Rewritten.
3. **Button syntax was wrong** — `Text - URL` with `|` separator does not exist. Real syntax is `<inline>Text<link="url">` with `style="primary|success|danger"`, `--` / `//` layout (verified in `src/core/helpers.py`). Rewritten with copy-paste example.
4. **Bulk Upload post described a feature that doesn't exist** — no "forward 5–10 posts + set 2/day interval" flow in the code. Replaced with verified `/recurring` + `/import` (incl. SetDate import).
5. **FAQ pointed to `/settings`** — no such command. Correct: `/timezone` and `/language`.
6. **Changelog said v1.2 and was cut off mid-sentence** — current version is **v2.4.7**; completed with real shipped features.
7. **"15 seconds" setup claim** — softened to "about a minute" (three real steps incl. admin check).
8. **CTR "+30%" claim** — unverifiable; removed the number, kept the benefit wording.

## 📌 10. Publishing the 30-day pack (import-ready files)

Files in this folder:

* `month_posts_import.md` — 30 posts, real dates **08.10.2026 → 06.11.2026, 19:00 daily**, importer format (date line + single newlines + Markdown + per-post buttons).
* `images/day_01.png … day_30.png` — 1280×720 cover per post, in matching order.
* `month_posts_30_days.md` — human-readable version (do NOT import this one; blank lines inside posts would split them).

Publish flow (5 minutes):

1. Send `/import` to @FastSchedulerBot and upload `month_posts_import.md`.
2. Choose **Sequential** when asked for photo mode.
3. Send the 30 images **in order** (`day_01.png` … `day_30.png`) — each pairs with its post.
4. Confirm — all 30 posts schedule at 19:00 daily, each with its own text, photo and buttons.

Regenerate any time: `python tools/gen_month_import.py` (also self-validates with the real parser).

## 📌 11. Button syntax reference (for post authors)

```
<inline>Label<link="https://example.com">
<inline>Green button<link="https://example.com" style="success">
<inline>Blue button<link="https://example.com" style="primary">
<inline>Red button<link="https://example.com" style="danger">
<inline>A<link="https://a.com"> -- <inline>B<link="https://b.com">
<inline>Row 1<link="https://a.com"> // <inline>Row 2<link="https://b.com">
```

Rules: max ~8 buttons, button text ~64 chars, full `https://` URLs, `callback=` variant exists for bot actions (not needed for channel posts).
