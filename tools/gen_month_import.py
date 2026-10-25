"""Generate the 30-day channel pack: import-ready .md + one image per post.

Output:
  docs/social/channel/month_posts_import.md   (importer format: date line,
      single newlines, Markdown, per-post <inline> buttons)
  docs/social/channel/images/day_01.png ... day_30.png  (1280x720 cards)

Dates: 08.10.2026 -> 06.11.2026, 19:00 daily. Re-run to regenerate; the script
self-validates with the bot's real parser (30 messages, 0 errors, buttons kept
per post).
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

BOT = "https://t.me/FastSchedulerBot"
SUPPORT = "https://t.me/FastSchedulerSupport_bot"

# (image title, [markdown lines...], [button markup lines...])
POSTS: list = [
("Welcome Aboard",
 ["📍 **Welcome to the official Fast Scheduler channel!**",
  "**Fast Scheduler** (@FastSchedulerBot) schedules your Telegram posts, repeats them on autopilot and shows per-post stats — all from one chat.",
  "**Start here:** connect your channel (Day 2 guide), tap `#guide` for the index, support answers fast.",
  "#navigation #pinned"],
 ['<inline>🚀 Open Fast Scheduler<link="https://t.me/FastSchedulerBot" style="success">',
  '<inline>📖 Quick-start guide<link="https://t.me/FastSchedulerBot" style="primary">']),
("Quick Start",
 ["📖 **Connect your channel in 3 steps**",
  "**1.** Channel Settings → Administrators → add `@FastSchedulerBot` (Post Messages permission).",
  "**2.** Open the bot and send your public link (`@yourchannel`), an invite link, or **forward any message** from the channel.",
  "**3.** The bot verifies you're an admin — done! Send `/schedule` for your first post.",
  "Free plan: 1 channel, 100 pending posts, 1 recurring post.",
  "#guide #quickstart"],
 ['<inline>🚀 Connect my channel<link="https://t.me/FastSchedulerBot" style="success">']),
("First Post",
 ["🗓 **Schedule your first post in 30 seconds**",
  "Send `/schedule` → send text/photo/video → send date and time (e.g. `tomorrow at 19:00`) → confirm. The bot delivers on time, even while you sleep.",
  "Wrong time? Edit the queued post any time before it sends.",
  "#guide"],
 ['<inline>🗓 Try /schedule<link="https://t.me/FastSchedulerBot" style="primary">']),
("Inline Buttons",
 ["✨ **Buttons under posts — copy-paste this**",
  "`<inline>Buy now<link=\"https://site.com\">`",
  "`<inline>Support<link=\"https://t.me/FastSchedulerSupport_bot\" style=\"success\">`",
  "`style=` is optional: `primary`, `success`, `danger`. `--` = same row, `//` or new line = new row.",
  "Broken markup? The bot warns you **before** scheduling — nothing breaks silently.",
  "#features #inline_buttons"],
 ['<inline>📖 Button guide<link="https://t.me/FastSchedulerBot" style="primary">']),
("Recurring",
 ["🔁 **Post it once. Repeat forever.**",
  "`/recurring` repeats any post **daily, weekly, monthly or yearly**. Morning digest at 09:00, Monday promo, monthly report — set once, forget it.",
  "#features #recurring"],
 ['<inline>🔁 Set up recurring<link="https://t.me/FastSchedulerBot" style="success">']),
("Calendar",
 ["📅 **See the whole month at a glance**",
  "`/calendar` shows every scheduled post on a calendar. Spot gaps, avoid pile-ups, keep your rhythm steady. Tap a day to see what's queued.",
  "#features"],
 ['<inline>📅 Open calendar<link="https://t.me/FastSchedulerBot" style="primary">']),
("Posting Rhythm",
 ["💡 **Burnout-proof posting rhythm**",
  "Post at **09:00 / 13:00 / 20:00** instead of dumping everything at midnight. Same 3 posts, 3x the reads — spacing beats bursts.",
  "Write in one sitting on Sunday, schedule the week, done.",
  "#tips #growth"],
 ['<inline>🗓 Plan my week<link="https://t.me/FastSchedulerBot" style="success">']),
("Stats",
 ["📊 **Know what worked**",
  "`/stats` shows views, comments and reactions per post and per channel. Double down on what your audience reads — guess less, grow faster.",
  "#features"],
 ['<inline>📊 Check my stats<link="https://t.me/FastSchedulerBot" style="primary">']),
("Edit Queue",
 ["✏️ **Typo in a scheduled post? Fix it in seconds.**",
  "Open your message list, pick the queued post, edit text, swap media or change the time — no delete-and-redo. The schedule stays intact.",
  "#features"],
 ['<inline>✏️ Open my queue<link="https://t.me/FastSchedulerBot" style="primary">']),
("Media Storage",
 ["💾 **Your reusable media library**",
  "Photos, videos and files you send to the bot can live in **media storage** — reuse them across posts instead of re-uploading.",
  "Premium raises the limits (video up to 50 MB).",
  "#features"],
 ['<inline>💾 Open storage<link="https://t.me/FastSchedulerBot" style="primary">']),
("Import",
 ["📥 **Moving from elsewhere? Don't retype.**",
  "`/import` pulls in posts from a backup/export file — including bulk dates prepared in the SetDate bot. Your whole content plan, queued in minutes.",
  "#features #import"],
 ['<inline>📥 Import now<link="https://t.me/FastSchedulerBot" style="success">']),
("Timezones",
 ["🌍 **Your audience's evening, not yours**",
  "`/timezone` sets your timezone (per account and per channel) — the bot converts everything for you.",
  "International audience? Anchor posts to your biggest cluster's 19:00–22:00 prime time.",
  "#guide"],
 ['<inline>🌍 Set timezone<link="https://t.me/FastSchedulerBot" style="primary">']),
("Formatting",
 ["💡 **4 rules for readable posts**",
  "**1. Air** — 3–4 short lines per paragraph, no walls of text.",
  "**2. Monospace** — wrap codes with backticks: `PROMO2026`.",
  "**3. Spoilers** — ||hidden|| for quizzes and teasers.",
  "**4. Spacing is safe** — the bot keeps your line breaks exactly as sent.",
  "#tips #content"],
 []),
("Engagement Hack",
 ["🎯 **One question per discussion post**",
  "Posts with a question get comments. Comments get reach. End your next post with **one** specific question and reply to every comment within the hour.",
  "#tips #growth"],
 ['<inline>🗓 Schedule it<link="https://t.me/FastSchedulerBot" style="success">']),
("Help Checklist",
 ["🛟 **Something off? Two-minute checklist**",
  "1. Is `@FastSchedulerBot` still admin with posting rights?",
  "2. Is the queued post's time in the future (your timezone)?",
  "3. Check the message list — failed posts explain what happened.",
  "Still stuck? Human support responds fast.",
  "#faq"],
 ['<inline>💬 Contact support<link="https://t.me/FastSchedulerSupport_bot" style="success">',
  '<inline>❓ Read FAQ<link="https://t.me/FastSchedulerBot" style="primary">']),
("Sender Bots",
 ["🤖 **Posts signed by YOUR bot, not ours**",
  "`/addbot` connects your own Telegram bot (via @BotFather token) as the sender for a channel. Readers see your brand, hidden channels stay truly private.",
  "#features"],
 ['<inline>🤖 Connect sender bot<link="https://t.me/FastSchedulerBot" style="primary">']),
("Premium",
 ["💎 **Free vs Premium, honestly**",
  "**Free:** 1 channel, up to 100 pending posts, 1 recurring post.",
  "**Premium:** 3 channels, unlimited scheduled + recurring, bigger media storage, full export.",
  "Run one serious channel? Free is enough. Run the rhythm for real? Premium pays for itself in a week.",
  "#premium"],
 ['<inline>💎 See Premium plans<link="https://t.me/FastSchedulerBot" style="success">']),
("Referral",
 ["🎁 **Get Premium free — invite a friend**",
  "`/referral` gives you a personal link: every friend who joins earns you **3 free Premium days**. No caps, no fine print — just share.",
  "#premium"],
 ['<inline>🎁 Get my link<link="https://t.me/FastSchedulerBot" style="success">']),
("Search",
 ["🔍 **Find any scheduled post instantly**",
  "`/search` digs through your queue by text. Dozens of scheduled posts and need the promo from next Thursday? Two seconds, no scrolling.",
  "#features"],
 ['<inline>🔍 Search queue<link="https://t.me/FastSchedulerBot" style="primary">']),
("Backup",
 ["📦 **Your content pipeline is an asset — back it up**",
  "`/export` downloads your scheduled content; Premium unlocks full backups (.fsback) incl. password-protected and scheduled copies.",
  "#features"],
 ['<inline>📦 Export now<link="https://t.me/FastSchedulerBot" style="primary">']),
("Language",
 ["🌐 **Bot speaks your language**",
  "`/language` switches between English, Russian and more — anytime, instantly. Mixed team? Everyone works in their own language on the same channels.",
  "#guide"],
 ['<inline>🌐 Change language<link="https://t.me/FastSchedulerBot" style="primary">']),
("Update 2.4.7",
 ["🚀 **Fast Scheduler v2.4.7 is live**",
  "✅ **Traffic Sources panel** — admins see exactly which links bring users.",
  "✅ **Translation audit** — zero missing keys, dead strings removed.",
  "✅ **Safer start flow** — deep links never break, tracking never blocks.",
  "Update = just keep using the bot. Enjoy!",
  "#updates"],
 ['<inline>🚀 Open the bot<link="https://t.me/FastSchedulerBot" style="success">']),
("Consistency",
 ["📈 **The algorithm is a schedule**",
  "Channels that post daily at 09:00 train subscribers to show up at 09:00 — visible in view-rate stability within two weeks.",
  "Pick a cadence you can hold for 6 months, then let `/recurring` hold it for you through bad weeks.",
  "#tips #growth"],
 []),
("Polls",
 ["📊 **Polls = cheapest engagement there is**",
  "Schedule a weekly poll (best post of the week? next topic?). Image polls work too — attach a photo when creating. Results double as content ideas.",
  "#tips #content"],
 ['<inline>🗓 Schedule a poll<link="https://t.me/FastSchedulerBot" style="success">']),
("Safety",
 ["🔒 **\"Is it safe?\" — yes, and here's why**",
  "• Only needs channel-admin rights to publish — never sees personal chats.",
  "• Tokens stored encrypted; revoke/rotate anytime via @BotFather.",
  "• Backups can be password-protected.",
  "#faq"],
 ['<inline>🔒 Start safely<link="https://t.me/FastSchedulerBot" style="primary">']),
("Multi-Channel",
 ["📢 **Run 3 channels from one chat**",
  "Premium connects up to 3 channels (and 3 sender bots), each with its own schedule, timezone and stats. One morning routine, three audiences served.",
  "#features"],
 ['<inline>📢 Manage channels<link="https://t.me/FastSchedulerBot" style="primary">']),
("Launch Checklist",
 ["✅ **New channel? Publish THESE before inviting anyone**",
  "1. Pinned intro (what / when / who). 2. Your single best post.",
  "3. A consistency proof (\"Every weekday at 9:00\"). 4. Something with comments. 5. One more genuinely useful post.",
  "Then invite. Visitors deciding in 5 seconds will stay.",
  "#tips #growth"],
 []),
("Bulk Dates",
 ["📆 **Plan dates in bulk, import in seconds**",
  "Need 50 dates for a campaign? The SetDate bot builds them in bulk — import the file here and every slot becomes a scheduled post.",
  "#features"],
 ['<inline>📥 How import works<link="https://t.me/FastSchedulerBot" style="success">']),
("Month Review",
 ["🔄 **End-of-month 10-minute review**",
  "Open `/stats`: top-3 posts by views → make more of that. Bottom-3 → drop the format. Adjust next month's `/recurring` slots to your actual best hours.",
  "#tips"],
 ['<inline>📊 Review my month<link="https://t.me/FastSchedulerBot" style="primary">']),
("Share the Love",
 ["💜 **Running on Fast Scheduler? Tell someone.**",
  "If the bot saves you an hour a week, the highest compliment is a forward: share this channel with one channel-owner friend.",
  "Questions, ideas, bugs → support reads everything.",
  "#navigation"],
 ['<inline>🚀 Open Fast Scheduler<link="https://t.me/FastSchedulerBot" style="success"> -- <inline>💬 Support<link="https://t.me/FastSchedulerSupport_bot" style="primary">']),
]

START = date(2026, 10, 8)
SEND_TIME = "19:00"


def build_md() -> str:
    blocks = []
    for i, (title, lines, buttons) in enumerate(POSTS):
        day = START + timedelta(days=i)
        head = day.strftime("%d.%m.%Y") + " " + SEND_TIME
        blocks.append("\n".join([head] + lines + buttons))
    return "\n\n".join(blocks) + "\n"


def make_image(day: int, title: str, path: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1280, 720
    top = (11, 30, 58)
    bottom = (18, 59, 109)
    img = Image.new("RGB", (W, H), top)
    px = img.load()
    for y in range(H):
        t = y / H
        for x in range(W):
            px[x, y] = tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 14, H], fill=(255, 193, 7))
    d.rectangle([W - 14, 0, W, H], fill=(255, 193, 7))

    def font(name: str, size: int):
        for p in (f"C:/Windows/Fonts/{name}.ttf",
                  f"/usr/share/fonts/truetype/dejavu/{name}.ttf"):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
        return ImageFont.load_default()

    f_brand = font("arial", 44)
    f_day = font("arialbd", 150)
    f_title = font("arialbd", 92)
    f_foot = font("arial", 40)
    d.text((90, 60), "FAST SCHEDULER", font=f_brand, fill=(255, 193, 7))
    d.text((90, 130), f"DAY {day:02d}", font=f_day, fill=(255, 255, 255))
    words, lines, cur = title.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= 16:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    y = 360
    for ln in lines[:2]:
        d.text((90, y), ln, font=f_title, fill=(255, 255, 255))
        y += 110
    d.text((90, H - 100), "t.me/FastSchedulerBot", font=f_foot, fill=(160, 190, 220))
    img.save(path)


def main() -> None:
    out_dir = ROOT / "docs" / "social" / "channel"
    img_dir = out_dir / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    md = build_md()
    (out_dir / "month_posts_import.md").write_text(md, encoding="utf-8")

    for i, (title, _lines, _btns) in enumerate(POSTS, 1):
        make_image(i, title, img_dir / f"day_{i:02d}.png")

    # Self-validation with the bot's real parser.
    from src.services.parsers import parse_scheduled_messages
    from src.core.helpers import inline_buttons_issues, parse_inline_buttons_spans
    from src.services.parsers import format_markdown_to_html
    messages, errors = parse_scheduled_messages(md, True)
    assert not errors, errors[:5]
    assert len(messages) == 30, len(messages)
    total_btns = 0
    for m in messages:
        assert not inline_buttons_issues(m["content"]), m["content"][:80]
        raw = m["content"]
        if "<inline>" in raw:
            cleaned, rows, _ = parse_inline_buttons_spans(raw)
            assert rows, raw[:80]
            total_btns += sum(len(r) for r in rows)
        format_markdown_to_html(raw.replace("<inline>", ""))
    print(f"OK: 30 posts, {total_btns} buttons, images in {img_dir}")


if __name__ == "__main__":
    main()
