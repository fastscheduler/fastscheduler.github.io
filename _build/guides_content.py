# -*- coding: utf-8 -*-
"""Long-form help guides written against the shipped bot code.

Every statement here is checked against the handlers/keyboards that actually
run (src/keyboards.py, src/handlers/schedule_conv.py, src/callbacks/channels.py,
src/core/helpers.py) and against the plan limits in src/core/plans.py.

Node shape matches ``seo_articles.py`` so ``tools/build_guides.py`` can render
the same page chrome as the generated Help Center.
"""

GUIDES = []


def _g(i, **kw):
    kw['id'] = i
    GUIDES.append(kw)


# ------------------------------------------------------------------ START ----
_g('guide_overview',
   category='start',
   title='Fast Scheduler: The Complete Guide to Every Menu and Button',
   description=('A full walkthrough of the Fast Scheduler Telegram bot: the three-step tutorial, '
                'what the main menu buttons open, why the menu moves to your sender bot, and how '
                'to publish your first post.'),
   content=(
       "<p><b>Fast Scheduler</b> is a Telegram bot (<code>@FastSchedulerBot</code>) that schedules "
       "posts for your Telegram channels and publishes them automatically, in your channel's own "
       "time zone, through a sender bot that you own. This page is the map: the tutorial, every "
       "menu, what each button opens, and the shortest path from an empty chat to a published "
       "post.</p>"

       "<h3>Two bots do the work</h3>"
       "<ul>"
       "<li><b>The main bot</b> — <code>@FastSchedulerBot</code>. It holds your account, your "
       "channel list, your billing and the Help Center. You talk to it in a private chat.</li>"
       "<li><b>Your sender bot</b> — a bot you create in <code>@BotFather</code>. It is the bot "
       "that actually posts, so the post appears under <i>your</i> bot's name and photo. Every "
       "connected channel needs one; scheduling stays locked until it is connected.</li>"
       "</ul>"
       "<p>A separate companion, <b>SetDate</b> (<code>@SetDate_bot</code>), builds whole batches "
       "of dated posts and hands them back to Fast Scheduler in one import. It is optional and "
       "explained in <a href=\"setdate.html\">SetDate Integration</a>.</p>"

       "<h3>The first-run tutorial, step by step</h3>"
       "<p>On your first <code>/start</code> the bot offers a short tutorial (under two minutes) "
       "with three steps. It is not decoration — it creates the exact state later steps depend on.</p>"
       "<p><b>Step 1/3 — Connect your channel.</b> Before you start, you must be an administrator "
       "of the channel and <code>@FastSchedulerBot</code> must be an administrator too, with at "
       "least <b>Post Messages</b>. Then send the channel link (<code>https://t.me/yourchannel</code>) "
       "or forward any message from the channel. Both work for public and private channels. If the "
       "bot answers <i>“bot is not an admin”</i>, add it under Channel Info → Administrators → Add "
       "Admin and send the link again. Details: <a href=\"connect_channel.html\">Connecting a "
       "Channel</a>.</p>"
       "<p><b>Step 2/3 — Set your time zone.</b> Every date you type is read in this zone. Send a "
       "city name (<code>London</code>, <code>New York</code>, <code>Tokyo</code>), your current "
       "time (<code>15:30</code>) so the bot can infer the offset, or a location for automatic "
       "detection; or pick from the list. Skipping this step keeps UTC, which is the usual reason a "
       "post goes out at the wrong hour. Details: <a href=\"timezone.html\">Time Zone</a>.</p>"
       "<p><b>Step 3/3 — Connect a sender bot.</b> Tap <b>Create bot</b> (opens "
       "<code>@BotFather</code>) and copy the token it gives you, or paste a token you already "
       "have. Add that bot as an administrator of the same channel with <b>Post Messages</b>, then "
       "tap <b>Check Again</b>. Details: <a href=\"connect_bot.html\">Connecting a Bot</a>.</p>"
       "<p><b>Skipping.</b> <b>Skip tutorial</b> exists on every step and asks for confirmation "
       "before it ends the tour — nothing is deleted, the bot simply drops you on the normal "
       "start screen with <b>Connect Channel</b> and <b>Help</b>. You can run the steps later from "
       "the menu; the tutorial is guidance, not a gate.</p>"
       "<p>When all three steps succeed the bot confirms that the channel's management now lives "
       "in your sender bot.</p>"

       "<h3>Why the menu moves after setup</h3>"
       "<p>This surprises everyone on day one. Once a channel is managed by a sender bot, the main "
       "bot becomes a <b>hub</b>: it keeps channels, bots, help and billing, and it does not show "
       "scheduling tools, because those belong to the bot that posts. Open your sender bot to "
       "schedule. The main bot's first menu then reads roughly:</p>"
       "<ul>"
       "<li><b>Connected Channel(s)</b> and <b>Bots</b> — your inventory.</li>"
       "<li><b>Referral Program</b> and <b>Language</b>.</li>"
       "<li><b>Help</b>, plus <b>Data</b> once you have something to import or export.</li>"
       "<li><b>Premium</b> — plan, limits and payment.</li>"
       "</ul>"

       "<h3>The full menu inside your sender bot</h3>"
       "<p><b>Page 1</b></p>"
       "<ul>"
       "<li><b>Schedule a Message</b> — the one-time scheduling flow. This is the button you will "
       "use most. See <a href=\"guide_schedule_format.html\">the schedule format</a>.</li>"
       "<li><b>Recurring Message</b> — daily, chosen weekdays, or a monthly date, repeated forever "
       "until paused or deleted. See <a href=\"recurring.html\">Recurring Messages</a>.</li>"
       "<li><b>Connected Channel</b> — channel card: time zone, signature, unlink, and the stats "
       "shortcut.</li>"
       "<li><b>Bots</b> — your sender bots: token, target channel, replace, remove. See "
       "<a href=\"bot_manage.html\">Manage Sender Bots</a>.</li>"
       "<li><b>Message List</b> — every queued post for this channel, with preview, edit, "
       "duplicate and delete. See <a href=\"message_list.html\">Message List</a>.</li>"
       "<li><b>Media Storage</b> — saved photos, files and (Premium) videos, reusable from the "
       "scheduling flow. See <a href=\"media_storage.html\">Media Storage</a>.</li>"
       "<li><b>Premium</b> — limits, plans, Stars payment, promo codes.</li>"
       "<li><b>Next</b> — page 2.</li>"
       "</ul>"
       "<p><b>Page 2</b></p>"
       "<ul>"
       "<li><b>Search</b> — keyword search across scheduled and recurring messages. See "
       "<a href=\"search.html\">Search</a>.</li>"
       "<li><b>Statistics</b> — sends, limits used, and per-channel numbers. See "
       "<a href=\"statistics.html\">Statistics Dashboard</a>.</li>"
       "<li><b>Calendar</b> — the month view with one row per day. See "
       "<a href=\"calendar.html\">Calendar View</a>.</li>"
       "<li><b>Referral Program</b> — invite link and earned Premium days. See "
       "<a href=\"referral.html\">Referrals</a>.</li>"
       "<li><b>Data</b> — the import/export hub. See <a href=\"import.html\">Import</a> and "
       "<a href=\"export.html\">Export</a>.</li>"
       "<li><b>Help</b> — the same articles you are reading, inside Telegram.</li>"
       "<li><b>Settings</b> — sender-bot-only: hide the channel from strangers, manage channel "
       "admins, and open channel statistics. See "
       "<a href=\"sender_bot_management.html\">Sender Bot Management</a>.</li>"
       "<li><b>Admin panel</b> — only for the bot's operators.</li>"
       "</ul>"

       "<h3>Your first post, in six taps</h3>"
       "<ol>"
       "<li>Open your sender bot → <b>Schedule a Message</b>.</li>"
       "<li>If you have several channels, pick one; with one channel this step is skipped.</li>"
       "<li>Send the date and time — <code>25.12.2026 10:00</code> works. Full list of accepted "
       "formats: <a href=\"guide_schedule_format.html\">Schedule Format</a>.</li>"
       "<li>Send the text.</li>"
       "<li>Choose how to attach media, or skip it. See <a href=\"guide_media_modes.html\">Media "
       "Modes</a>.</li>"
       "<li>Check the preview, then confirm. The bot replies with the job ID and the send time.</li>"
       "</ol>"
       "<p>Everything stays editable from <b>Message List</b> until the second it is sent. To "
       "schedule several posts in one go, put a blank line between blocks — or upload a "
       "<code>.txt</code> file: <a href=\"guide_batch_file.html\">Bulk Scheduling from a File</a>.</p>"

       "<h3>The four mistakes people make in week one</h3>"
       "<ul>"
       "<li><b>Looking for scheduling in the main bot.</b> After setup it lives in your sender bot "
       "(or inside <b>Bots</b> in the main bot, through the bot you connected).</li>"
       "<li><b>Leaving the time zone unset.</b> Times are channel-local; UTC silently shifts "
       "everything by your offset.</li>"
       "<li><b>Forgetting the sender bot's admin rights.</b> Both bots must be channel admins, with "
       "Post Messages at minimum.</li>"
       "<li><b>Sending two identical blocks by accident.</b> The bot schedules both. How to find and "
       "remove one: <a href=\"guide_fix_duplicates.html\">Duplicates and Mistakes</a>.</li>"
       "</ul>"
       "<p>Free plan at the time of writing: 1 channel, 1 sender bot, 1 recurring message, 100 "
       "pending scheduled messages and 100 sends per channel per month. Premium raises channels and "
       "bots to 3, makes sends and recurring messages unlimited, and adds backups, leaderboards, "
       "multi-date scheduling and larger uploads. The authoritative list is "
       "<a href=\"limits.html\">Limits</a>.</p>"
   ),
   faq=[
       {'q': 'Where do I schedule messages after connecting a sender bot?',
        'a': ('Open your sender bot — scheduling tools move there once a channel is managed. In the '
              'main bot you can still reach the channel through <b>Bots</b>, but the feature menu '
              'you want (Schedule, Recurring, Message List, Storage) belongs to the bot that posts.'),
        'links': ['connect_bot', 'bot_manage']},
       {'q': 'Can I skip the tutorial and set things up later?',
        'a': ('Yes. <b>Skip tutorial</b> appears on each step and asks for confirmation. Nothing is '
              'lost: use <b>Connect Channel</b> and <b>Bots</b> from the menu when you are ready, and '
              'the Help Center stays available.'),
        'links': ['getting_started', 'connect_channel']},
       {'q': 'How long does setup take?',
        'a': ('Usually five to ten minutes: connecting the channel about two minutes, creating and '
              'connecting the sender bot three to five, and the first scheduled post one to two.'),
        'links': ['getting_started']},
       {'q': 'Which permissions does the bot need?',
        'a': ('Post Messages is the minimum for both the main bot and your sender bot. Add Delete '
              'Messages if you want the bot to be able to remove posts, and Edit Messages if you '
              'plan to use post editing.'),
        'links': ['channel_permissions', 'connect_channel']},
       {'q': 'Do I need to understand the SetDate bot to start?',
        'a': ('No. Fast Scheduler alone schedules single posts and multi-block batches from one '
              'message or a .txt file. SetDate is only for generating large calendars of dated posts '
              'and importing them in one click.'),
        'links': ['setdate', 'guide_batch_file']},
       {'q': 'What is the difference between the main bot and my sender bot?',
        'a': ('The main bot is the account hub: channels, bots, language, referrals, Premium and '
              'support. The sender bot is the publisher: it posts under your own bot identity and '
              'hosts the full scheduling menu for its channel.'),
        'links': ['bot_sender', 'glossary_sender']},
   ])

_g('guide_interface_map',
   category='start',
   title='Which Button Opens What: The Complete Interface Map',
   description=('Every button in Fast Scheduler and the screen it opens — main menu pages 1 and 2, '
                'the sender-bot hub, Management settings, and the Message List controls.'),
   content=(
       "<p>Fast Scheduler has two menus and a handful of sub-screens. This page lists what each "
       "button opens, so you can describe a problem precisely or jump straight to the right screen "
       "without hunting.</p>"

       "<h3>Main menu, page 1 (sender-bot context)</h3>"
       "<ul>"
       "<li><b>Schedule a Message</b> → the one-time scheduling conversation: channel → date and "
       "time → content → media mode → review → confirm.</li>"
       "<li><b>Recurring Message</b> → interval (daily / weekdays / monthly) → send time → content "
       "→ confirm.</li>"
       "<li><b>Connected Channel</b> → the channel card with time zone, signature, statistics "
       "shortcut and unlink.</li>"
       "<li><b>Bots</b> → sender-bot list: token, target channel, replace token, remove bot, and "
       "the verification state.</li>"
       "<li><b>Message List</b> → queued posts for the channel: preview, edit/replace, duplicate, "
       "delete, delete-by-ID, delete all.</li>"
       "<li><b>Media Storage</b> → storage boxes, their items, and the copy/move/download actions.</li>"
       "<li><b>Premium</b> → plan comparison, purchase with Telegram Stars, promo code, cancel or "
       "renew, current status.</li>"
       "<li><b>Next</b> → page 2.</li>"
       "</ul>"

       "<h3>Main menu, page 2</h3>"
       "<ul>"
       "<li><b>Search</b> → keyword prompt, then a result list; each result opens the same preview "
       "and edit/delete controls as Message List.</li>"
       "<li><b>Statistics</b> → channel overview, sends and limits, and (Premium) per-post "
       "leaderboards by views, comments and reactions.</li>"
       "<li><b>Calendar</b> → month grid; tap a day to see its posts. Scheduled and recurring "
       "messages both appear.</li>"
       "<li><b>Referral Program</b> → your invite link, reward balance, referral list and rules.</li>"
       "<li><b>Data</b> → import and export hub (hidden until you have a channel or messages, "
       "because an empty account has nothing to move).</li>"
       "<li><b>Help</b> → the in-bot Help Center, the same topics as this website.</li>"
       "<li><b>Settings</b> → sender-bot channel settings: hide/unhide the channel, manage channel "
       "admins, open stats.</li>"
       "<li><b>Admin panel</b> → operator-only; ordinary accounts never see it.</li>"
       "<li><b>Previous</b> → page 1.</li>"
       "</ul>"

       "<h3>The main-bot hub (after a channel is delegated)</h3>"
       "<ul>"
       "<li><b>Connected Channel(s)</b> — the same channel card, read-only for scheduling.</li>"
       "<li><b>Bots</b> — the sender bots tied to your account, including a link that opens each "
       "bot's chat.</li>"
       "<li><b>Referral Program</b>, <b>Language</b>, <b>Help</b>, <b>Data</b>, <b>Premium</b> — "
       "account-level screens, identical in both menus.</li>"
       "</ul>"

       "<h3>Inside Message List</h3>"
       "<ul>"
       "<li><b>Open a message</b> → preview with text, media, target channel, send time and "
       "buttons.</li>"
       "<li><b>Edit / Replace</b> → re-enter text, time, media or channel; the bot previews the new "
       "version before saving.</li>"
       "<li><b>Duplicate</b> → asks for the new date, then the channel, then creates the copy. "
       "<code>/dub &lt;message_id&gt;</code> does the same.</li>"
       "<li><b>Delete</b> (trash) → removes that one post after confirmation. Pending posts never "
       "send after deletion; deletion cannot be undone.</li>"
       "<li><b>Delete by ID</b> → same, when you know the ID (<code>s…</code> for scheduled, "
       "<code>r…</code> for recurring).</li>"
       "<li><b>Delete All</b> → removes every scheduled <i>and</i> recurring message for the "
       "channel after a confirmation that names the count.</li>"
       "</ul>"

       "<h3>Screen-by-screen shortcuts</h3>"
       "<p>Most screens also answer to a command, which is faster on desktop: <code>/schedule</code>, "
       "<code>/recurring</code>, <code>/list</code>, <code>/search</code>, <code>/calendar</code>, "
       "<code>/stats</code>, <code>/bots</code>, <code>/storage</code>, <code>/premium</code>, "
       "<code>/data</code>, <code>/backup</code>, <code>/import</code>, <code>/export</code>, "
       "<code>/timezone</code>, <code>/language</code>, <code>/help</code>, <code>/edit</code>, "
       "<code>/delete</code>, <code>/dub</code>, <code>/cancel</code>, <code>/skip</code>. The "
       "complete list with descriptions is in <a href=\"commands_list.html\">All Commands</a>.</p>"
       "<p><b>Feedback is not in this bot.</b> The <code>/feedback</code> command in Fast Scheduler "
       "does not open a form — it answers with a button that opens the separate Support Bot "
       "(<code>@FastSchedulerSupport_bot</code>), and tickets are filed there. Payment problems use "
       "<code>/paysupport</code>, which opens the same Support Bot on its payment intake. Details: "
       "<a href=\"feedback.html\">Feedback &amp; Support</a>.</p>"
   ),
   faq=[
       {'q': 'Why can’t I find Schedule in the main bot?',
        'a': ('Because the channel is managed by your sender bot, and scheduling belongs to the bot '
              'that publishes. Open the sender bot from <b>Bots</b> in the main bot, or directly in '
              'Telegram. The main bot keeps the account-level screens only.'),
        'links': ['bot_manage', 'bot_sender']},
       {'q': 'Where is the Feedback form?',
        'a': ('In the Support Bot, not in Fast Scheduler. Sending <code>/feedback</code> in Fast '
              'Scheduler shows a redirect button that opens <code>@FastSchedulerSupport_bot</code>; '
              'the category picker, ticket thread and status list all live there.'),
        'links': ['feedback', 'contact_support']},
       {'q': 'What does Delete All remove?',
        'a': ('Every scheduled <b>and</b> recurring message for that channel, after a confirmation '
              'that shows the exact count. It is permanent; deleting one post uses the trash icon or '
              'Delete by ID instead.'),
        'links': ['delete', 'schedule_delete']},
       {'q': 'Is there a command for every button?',
        'a': ('For the main screens, yes — see All Commands. Deep editing steps are button-driven, '
              'and <code>/cancel</code> always returns you to the menu if a flow is waiting for '
              'input.'),
        'links': ['commands_list', 'errors']},
   ])

# ------------------------------------------------------------- SCHEDULING ----
_g('guide_schedule_format',
   category='scheduling',
   title='Schedule Format: Dates, Text and Inline Buttons (Copy & Paste Examples)',
   description=('The exact text format Fast Scheduler parses: accepted date and time syntaxes, the '
                'blank-line rule for scheduling many posts at once, inline button markup, and the '
                'real limits.'),
   content=(
       "<p>Fast Scheduler reads a schedule the same way a person reads a to-do list: <b>a date line, "
       "then the post, then a blank line, then the next date line</b>. Nothing else is needed — no "
       "table, no CSV, no special syntax around the text.</p>"

       "<h3>One message, five posts</h3>"
       "<p>Paste this into the scheduling flow as a single message (the blank line between blocks is "
       "what separates them):</p>"
       "<pre><code>today 10:23\nTest 1 &lt;inline&gt;Button Text&lt;link=\"https://example.com\"&gt;\n"
       "\nTomorrow 7:24 PM\nJdjdjekrkrk\n\n12.12.2026 18:28\nHdjdjdkdkdkkr\n\n"
       "23-10-2027 15:34\nKskskdkkrkr\n\n14/04/2026 4:05 PM\nJDJDJDJRKJR</code></pre>"
       "<p>The bot creates five scheduled messages, each with its own date and content. The first "
       "one carries a button under the post. You can repeat this as often as you like: another "
       "message with more blocks, another day, the same channel or a different one. Nothing is "
       "counted per batch — only the number of <b>queued messages</b> matters for your plan.</p>"

       "<h3>Accepted date and time formats</h3>"
       "<ul>"
       "<li><code>DD.MM.YYYY HH:MM</code> — <code>25.12.2026 10:00</code></li>"
       "<li><code>YYYY-MM-DD HH:MM</code> — <code>2026-12-25 10:00</code></li>"
       "<li><code>DD.MM.YYYY h:mm AM/PM</code> — <code>25.12.2026 10:00 AM</code></li>"
       "<li><code>today HH:MM</code> and <code>tomorrow HH:MM</code> — <code>today 10:23</code>, "
       "<code>tomorrow 19:00</code></li>"
       "<li>A day-first date with slashes or dashes also works: <code>14/04/2026 4:05 PM</code>, "
       "<code>23-10-2027 15:34</code>.</li>"
       "<li><code>HH:MM</code> or <code>HH.MM</code> alone — today at that time; if the hour has "
       "already passed, the next day.</li>"
       "<li><code>12:00 PM</code> and <code>12;00</code> style times are accepted by the same parser "
       "used by SetDate, so a schedule built there keeps working after import.</li>"
       "</ul>"
       "<p>Times are interpreted in the <b>channel's time zone</b>, not the server's and not the "
       "phone's. Set it under <b>Connected Channel → Time Zone</b> or with <code>/timezone</code>. "
       "If a post lands an hour off, this is almost always why: see "
       "<a href=\"timezone.html\">Time Zone</a>.</p>"

       "<h3>The blank-line rule</h3>"
       "<ul>"
       "<li>One blank line ends the previous block. Without it, the next date line is treated as "
       "part of the post text.</li>"
       "<li>Inside a block you can use as many lines as you want — paragraphs, emoji, formatting.</li>"
       "<li>Order does not have to be chronological; the bot sorts by send time.</li>"
       "<li>A block without a date line is not a block: it needs its own date to be scheduled.</li>"
       "</ul>"

       "<h3>Inline buttons</h3>"
       "<p>Buttons are typed into the post text with angle-bracket markup. The button lines are "
       "removed from the published post and appear underneath it.</p>"
       "<pre><code>&lt;inline&gt;Button Text&lt;link=\"https://example.com\"&gt;</code></pre>"
       "<ul>"
       "<li><b>One per line</b> → one button per row.</li>"
       "<li><code>--</code> between two buttons → same row, side by side.</li>"
       "<li><code>//</code> between two buttons → forced new row.</li>"
       "<li><b>Colours</b>: add <code>style=\"success\"</code> (green), <code>style=\"primary\"</code> "
       "(blue) or <code>style=\"danger\"</code> (red) inside the tag. Unknown styles are ignored.</li>"
       "<li><b>Callback buttons</b>: <code>&lt;inline&gt;Action&lt;callback=\"data\"&gt;</code> — they "
       "answer the bot instead of opening a URL. Callback data is limited to 64 bytes and only works "
       "when the bot recognises it.</li>"
       "<li>Use full <code>https://</code> URLs, and keep labels short so they fit on a phone.</li>"
       "</ul>"
       "<p>Layout example:</p>"
       "<pre><code>&lt;inline&gt;Catalog&lt;link=\"https://shop.com\"&gt; -- &lt;inline&gt;Sale"
       "&lt;link=\"https://shop.com/sale\"&gt; // &lt;inline&gt;Reviews&lt;link=\"https://shop.com/reviews\"&gt;"
       " -- &lt;inline&gt;Support&lt;link=\"https://support.com\"&gt;</code></pre>"
       "<p>Result: two rows — <i>Catalog | Sale</i>, then <i>Reviews | Support</i>. More on formatting: "
       "<a href=\"formatting.html\">Formatting &amp; Inline Buttons</a>.</p>"

       "<h3>Scheduling from a .txt file</h3>"
       "<p>The same blank-line rule applies to a file. Send the document during scheduling (or use "
       "<code>/import</code>) and every block becomes one scheduled post. A file is usually the "
       "fastest way to load a month of content. Step by step: "
       "<a href=\"guide_batch_file.html\">Bulk Scheduling from a .txt File</a>.</p>"

       "<h3>The real limits</h3>"
       "<ul>"
       "<li><b>Telegram caps a single message at 4096 characters.</b> That caps each block, and it "
       "also caps the batch message itself — a very long batch has to be split across several "
       "messages or uploaded as a file, which has no such limit in practice.</li>"
       "<li><b>Free plan: 100 pending scheduled messages.</b> Premium has no pending cap. The exact "
       "count is in <a href=\"limit_scheduled.html\">Scheduled Limit</a> and "
       "<a href=\"limits.html\">Limits</a>.</li>"
       "<li>Media is attached <i>after</i> the text — one mode per batch, not per block. See "
       "<a href=\"guide_media_modes.html\">Media Modes</a>.</li>"
       "<li>Sending more than your plan allows does not silently drop posts: the bot stops and "
       "tells you which limit you hit.</li>"
       "</ul>"

       "<h3>When a block is rejected</h3>"
       "<p>Check, in this order: the date line is the first line of the block; a blank line separates "
       "it from the previous post; the year is four digits; the time has minutes; and the channel has "
       "a sender bot. If the bot warns about inline markup, one tag is incomplete — every "
       "<code>&lt;inline&gt;</code> needs both <code>&lt;link=\"…\"&gt;</code> and a closing "
       "<code>&gt;</code>. Cancelling with <code>/cancel</code> never schedules partial input.</p>"
   ),
   howto=[
       ('Write the date line',
        'Start each post with a date and time: DD.MM.YYYY HH:MM, YYYY-MM-DD HH:MM, '
        'today/tomorrow HH:MM, or HH:MM alone for today.'),
       ('Write the post',
        'On the following lines write the post text. Buttons go in the same block with '
        '<inline>Text<link="https://example.com"> markup.'),
       ('Separate the posts with a blank line',
        'One blank line ends a post. The next date line starts the next post, so five blocks '
        'become five scheduled messages.'),
       ('Send it to the bot',
        'Paste the whole schedule into the scheduling flow, or upload a .txt file with the same '
        'structure. The bot parses every block and shows the count.'),
       ('Choose media and confirm',
        'Pick the media mode for the batch (or skip media), review the preview, and confirm. '
        'The posts are queued and stay editable in Message List.'),
   ],
   faq=[
       {'q': 'Can I schedule several messages in one go?',
        'a': ('Yes. Send one block per post, separated by a blank line: a date line, the text, a '
              'blank line, the next date line. Five blocks become five scheduled messages, and you '
              'can do it again as many times as you like.'),
        'links': ['scheduling', 'guide_batch_file']},
       {'q': 'What separates two messages in a batch?',
        'a': ('A blank line. The date line alone does not start a new block — if the blank line is '
              'missing, that date is stored as part of the previous post text.'),
        'links': ['scheduling', 'tips_bulk']},
       {'q': 'Can I schedule from a file instead of typing?',
        'a': ('Yes — upload a .txt file with the same blank-line structure during scheduling, or use '
              '<code>/import</code>. Each block becomes one post, and a file avoids the 4096-character '
              'cap on a single Telegram message.'),
        'links': ['import', 'guide_batch_file']},
       {'q': 'How do I add a button under a post?',
        'a': ('Type <code>&lt;inline&gt;Button Text&lt;link="https://example.com"&gt;</code> on its '
              'own line in the post. Use <code>--</code> for buttons side by side and <code>//</code> '
              'for a new row. The markup is removed from the text and rendered as a button.'),
        'links': ['formatting', 'inline_buttons']},
       {'q': 'Are keyboard-button shortcuts like [Text](url) supported?',
        'a': ('No. <code>[text](url)</code> is a text hyperlink, not a button. Buttons require the '
              '<code>&lt;inline&gt;</code> markup; anything else produces ordinary link text.'),
        'links': ['formatting']},
       {'q': 'What time zone are the dates read in?',
        'a': ('The target channel\'s time zone. Set it under <b>Connected Channel → Time Zone</b> or '
              'with <code>/timezone</code>; otherwise the account time zone (UTC if never set) is used.'),
        'links': ['timezone', 'schedule_timezone']},
       {'q': 'Does the order of blocks matter?',
        'a': ('No. Put them in any order — the queue sorts by send time. Identical times are sent in '
              'the order they were created.'),
        'links': ['tips_queue']},
   ])

_g('guide_batch_file',
   category='import',
   title='Bulk Scheduling from a .txt File (Step by Step)',
   description=('Load a whole month of posts from one text file: the exact block structure, how to '
                'attach media to the batch, what the plan limits do to a large import, and how to '
                'fix a file the bot refuses.'),
   content=(
       "<p>Typing a month of posts into Telegram is slow, and one Telegram message is capped at 4096 "
       "characters. A <code>.txt</code> file removes both problems: write the schedule in any text "
       "editor, then hand the file to the bot once.</p>"

       "<h3>The file structure</h3>"
       "<p>A <code>.txt</code> file is a stack of blocks with the same rule as typed input: a date "
       "line, the post, a blank line. One file, any number of blocks.</p>"
       "<pre><code>12.12.2026 18:28\nFirst post text\n\n12.12.2026 21:00\n"
       "Second post &lt;inline&gt;Read more&lt;link=\"https://example.com\"&gt;\n\n"
       "13.12.2026 09:30\nThird post</code></pre>"
       "<ul>"
       "<li>Save as UTF-8 so emoji and non-Latin text survive.</li>"
       "<li>Windows line endings are fine; the parser normalises them.</li>"
       "<li>Keep the date line at the very start of its block, with no leading spaces.</li>"
       "<li>Buttons, formatting and links inside a block carry over unchanged.</li>"
       "</ul>"

       "<h3>Step by step</h3>"
       "<ol>"
       "<li>Open your sender bot (scheduling lives there once a channel is connected).</li>"
       "<li>Tap <b>Schedule a Message</b> — or <b>Data → Import</b> if you want the import flow "
       "directly.</li>"
       "<li>When the bot asks for the date or the content, send the <code>.txt</code> file as a "
       "document instead of typing.</li>"
       "<li>The bot parses every block and shows the count and times for review.</li>"
       "<li>Choose the media mode for the whole batch — normal, random, sequential, from storage, or "
       "none (<a href=\"guide_media_modes.html\">Media Modes</a>).</li>"
       "<li>Confirm. The queue now holds one post per block; open <b>Message List</b> to verify.</li>"
       "</ol>"
       "<p>The import formats page lists every accepted file type, including CSV and SetDate files: "
       "<a href=\"import_formats.html\">Supported Import Formats</a>.</p>"

       "<h3>Media with a file batch</h3>"
       "<p>A text file has no images inside it, so media is applied in one mode across the batch: "
       "the same file for every post (<b>Normal</b>), a random pick from your mix (<b>Random</b>), or "
       "in order (<b>Sequential</b>). To give individual posts their own picture, schedule those "
       "separately, or store the images first and attach them per post. Sizes: photos, files and "
       "documents up to 10 MB on Free and 100 MB on Premium; videos up to 25 MB on Free and 50 MB on "
       "Premium.</p>"

       "<h3>Large files and plan limits</h3>"
       "<ul>"
       "<li><b>Free plan holds 100 pending scheduled messages.</b> A file with more blocks than that "
       "hits the cap — the bot tells you rather than silently dropping the rest. Premium removes the "
       "pending cap.</li>"
       "<li>The monthly send limit still applies to how many posts actually go out: 100 per channel "
       "per month on Free, unlimited on Premium. See <a href=\"limit_daily.html\">Monthly Send "
       "Limit</a>.</li>"
       "<li>Each individual post still obeys Telegram's 4096-character message limit. Long articles "
       "should be split into several blocks, not one huge one.</li>"
       "</ul>"

       "<h3>If the bot rejects the file</h3>"
       "<ol>"
       "<li><b>“No messages found”</b> — the first line is not a date. Check the format "
       "(<a href=\"guide_schedule_format.html\">Schedule Format</a>) and that the file is plain text, "
       "not .docx.</li>"
       "<li><b>Some blocks import, others do not</b> — those blocks are missing their blank-line "
       "separator or their date line. Re-open the file and add one empty line between posts.</li>"
       "<li><b>A button warning appears</b> — an <code>&lt;inline&gt;</code> tag in the file is "
       "incomplete. Every button needs <code>&lt;inline&gt;Text&lt;link=\"https://…\"&gt;</code>.</li>"
       "<li><b>Nothing arrives</b> — the file may be larger than Telegram accepts for documents, or "
       "the upload timed out. Split it into two files; batching twice is harmless.</li>"
       "</ol>"

       "<h3>A realistic workflow</h3>"
       "<p>Write the month in a text editor with one blank line between posts, keep a line at the top "
       "of each block that reads like <code>03.11.2026 09:00</code>, set the channel time zone once, "
       "then load the file. Review the preview count against the number of blocks in the file — they "
       "should match exactly. If they do not, a blank line is missing somewhere. For generating a "
       "calendar of dates automatically, SetDate does the date maths for you: "
       "<a href=\"setdate.html\">SetDate Integration</a>.</p>"
   ),
   howto=[
       ('Write the blocks',
        'In any text editor, write one block per post: a date line, the post text, then a blank '
        'line. Save as UTF-8 .txt.'),
       ('Open the import or scheduling flow',
        'In your sender bot, open Schedule a Message, or Data → Import for the import flow.'),
       ('Send the file',
        'When the bot asks for the date or content, send the .txt document instead of typing.'),
       ('Review and choose media',
        'Check the block count and times, then choose the media mode for the whole batch.'),
       ('Confirm',
        'Confirm to queue one post per block; verify the result in Message List.'),
   ],
   faq=[
       {'q': 'Which file types can I import?',
        'a': ('<code>.txt</code> for message lists, <code>.csv</code> for spreadsheets with Date/Time '
              'and Content columns, <code>.json</code> for structured exports, SetDate schedule files, '
              'and <code>.fsback</code>/<code>.fspback</code> for full backups.'),
        'links': ['import_formats', 'import_data']},
       {'q': 'How many messages can one file contain?',
        'a': ('As many blocks as you write, bounded by your plan: 100 pending scheduled messages on '
              'Free, no pending cap on Premium. The 4096-character Telegram limit applies per post, '
              'not to the file.'),
        'links': ['limit_scheduled', 'limits']},
       {'q': 'Can each post in the file have a different image?',
        'a': ('Not from a plain text file — media is applied to the whole batch in one mode. For '
              'per-post images, schedule those posts individually or store the files in Media Storage '
              'and attach them per message.'),
        'links': ['guide_media_modes', 'media_storage']},
       {'q': 'Why did only part of my file get scheduled?',
        'a': ('Usually a missing blank line between two blocks, so the second date line became part '
              'of the first post. Compare the block count in the file with the preview count; a '
              'mismatch points at the missing separator.'),
        'links': ['guide_schedule_format', 'import_data']},
   ])

_g('guide_media_modes',
   category='scheduling',
   title='Media Modes: Normal, Random, Sequential and From Storage',
   description=('How Fast Scheduler attaches photos, videos, GIFs and documents to scheduled posts — '
                'what each media mode actually does, which to choose for which channel, and the real '
                'size limits.'),
   content=(
       "<p>Media is chosen <b>after</b> the post text, on a screen titled <b>Select Media Mode</b>, "
       "and it applies to every message in that batch. There is no per-message mode switch — the "
       "choice is a strategy for the batch, not a setting on one post.</p>"

       "<h3>The four modes</h3>"
       "<p><b>Normal.</b> The same file goes on every post in the batch. Use it for branding: a logo "
       "strip, a house style, a watermark, the same cover for a series. If one image must appear on "
       "twenty posts, this is the one tap that does it.</p>"
       "<p><b>Random.</b> Each post gets a random file from the mix you uploaded, and the mix can "
       "contain different types (photos, videos, documents). Use it when variety matters more than "
       "order — a quote channel with a pool of backgrounds, a shop with rotating product shots.</p>"
       "<p><b>Sequential.</b> Files are assigned in the order you sent them, repeating from the start "
       "when the batch is longer than the mix. Use it for anything where order carries meaning: a "
       "numbered tutorial, a story split across days, a carousel-like series.</p>"
       "<p><b>From Storage.</b> Reuses files you already saved in <b>Media Storage</b> instead of "
       "re-uploading them. It is the fastest option for recurring visuals — the same header for a "
       "daily digest, a standing promo card. Storage has its own plan limits; see "
       "<a href=\"media_storage.html\">Media Storage</a>.</p>"
       "<p><b>Skip / none.</b> Text-only posts. Choosing it does not delete anything you attached "
       "earlier in the same flow where the bot offers removal; it simply means no media is sent.</p>"

       "<h3>The text becomes the caption</h3>"
       "<p>When a post has media, the text you wrote is delivered as the media caption. Formatting, "
       "links, spoilers and inline buttons all work in captions exactly as they do in text posts. "
       "Captions wrap under the picture, so keep them short; if a post needs paragraphs, send the "
       "text separately from the image. More: <a href=\"formatting.html\">Formatting &amp; "
       "Inline Buttons</a>.</p>"

       "<h3>What can be attached</h3>"
       "<ul>"
       "<li>Photos (JPEG, PNG) and photo albums.</li>"
       "<li>Videos — MP4, MOV, AVI. Up to 25 MB each on Free, 50 MB on Premium.</li>"
       "<li>Animated GIFs.</li>"
       "<li>Documents of any type: PDF, DOC, XLS, ZIP, TXT.</li>"
       "<li>Voice messages (OGG) and audio (MP3), and stickers.</li>"
       "</ul>"
       "<p>Per-item size limits are 10 MB on Free and 100 MB on Premium for photos and documents. The "
       "full table, including 4K media, is in <a href=\"limits.html\">Limits</a> and "
       "<a href=\"limit_media.html\">Media Limit</a>.</p>"

       "<h3>Choosing a mode by situation</h3>"
       "<ul>"
       "<li><b>Brand visuals on every post</b> → Normal.</li>"
       "<li><b>A 30-day quote series with 10 backgrounds</b> → Random.</li>"
       "<li><b>A five-part tutorial, one image per part</b> → Sequential.</li>"
       "<li><b>Daily digest with the same header</b> → From Storage.</li>"
       "<li><b>Text-only announcements</b> → Skip.</li>"
       "</ul>"

       "<h3>After scheduling</h3>"
       "<p>Media is not frozen at creation: open the post from <b>Message List</b> and use "
       "<b>Edit</b> to replace the text, the media or the send time. Deleting media from a post never "
       "deletes it from storage. If a post goes out without its picture, the cause is usually size or "
       "format rather than the mode — <a href=\"troubleshoot_media.html\">Media Fails</a> lists the "
       "checks in order.</p>"
   ),
   faq=[
       {'q': 'Which media mode should I use?',
        'a': ('Normal for the same file on every post, Random for variety from a pool, Sequential when '
              'order matters, From Storage to reuse saved files without re-uploading, Skip for '
              'text-only.'),
        'links': ['schedule_media', 'media_modes']},
       {'q': 'Can each post in a batch get a different image?',
        'a': ('Random and Sequential give different images per post from the mix you uploaded. A '
              'specific image on a specific post means scheduling that post on its own.'),
        'links': ['schedule_album', 'scheduling']},
       {'q': 'Do videos work in every mode?',
        'a': ('Yes, and modes accept a mix of types. Size is the constraint: 25 MB per video on Free, '
              '50 MB on Premium, and videos can only be stored in Media Storage on Premium.'),
        'links': ['schedule_video', 'limit_media']},
       {'q': 'Can I change the media after scheduling?',
        'a': ('Yes. Open the post in Message List and edit it; the bot shows a new preview before '
              'saving. Removing media from a post does not remove it from storage.'),
        'links': ['edit', 'message_list']},
       {'q': 'Where does From Storage get its files?',
        'a': ('From your Media Storage boxes. You save files there once — photos, documents, and on '
              'Premium videos — then attach them during scheduling without uploading again.'),
        'links': ['media_storage', 'ms_from_storage_help']},
   ])

_g('guide_fix_duplicates',
   category='scheduling',
   title='Duplicates and Mistakes: Edit, Duplicate or Delete a Scheduled Post',
   description=('How duplicate posts happen, how to find them fast, the difference between editing, '
                'duplicating and deleting, and how to remove one post without wiping the queue.'),
   content=(
       "<p>Almost every duplicate has one of three causes: the same block was pasted twice, the "
       "confirm button was tapped twice and the second attempt created a second job, or a copy was "
       "made on purpose with <b>Duplicate</b> and never edited. Nothing about it is permanent — a "
       "queued post can always be found and removed before it sends.</p>"

       "<h3>Find it first</h3>"
       "<ul>"
       "<li><b>Message List</b> — every queued post for the channel, with its time and job ID. "
       "Duplicates sit next to each other when they share a send time.</li>"
       "<li><b>Search</b> — type a distinctive phrase from the post, or the job ID "
       "(<code>s…</code> for scheduled, <code>r…</code> for recurring). Search covers all channels at "
       "once. See <a href=\"search.html\">Search</a>.</li>"
       "<li><b>Calendar</b> — tap the day and look for two entries at the same hour. See "
       "<a href=\"calendar.html\">Calendar View</a>.</li>"
       "</ul>"

       "<h3>Delete exactly one post</h3>"
       "<ol>"
       "<li>Open <b>Message List</b> and find the duplicate.</li>"
       "<li>Tap its <b>trash</b> icon (or open it and choose Delete).</li>"
       "<li>Confirm. The job is removed from the queue and will not send.</li>"
       "</ol>"
       "<p>Alternatives: <b>Delete by ID</b> if you already copied the ID, or <code>/delete</code> "
       "followed by the ID. Deletion is permanent and cannot be undone — but it only touches the post "
       "you picked.</p>"
       "<p><b>Do not use Delete All for one duplicate.</b> That button clears every scheduled <i>and</i> "
       "recurring message for the channel after a confirmation naming the count. It is the right tool "
       "for resetting a channel's queue, not for tidying one mistake. See "
       "<a href=\"delete.html\">Delete Messages</a>.</p>"

       "<h3>Edit instead of delete-and-retype</h3>"
       "<p>If the post is in the right place at the wrong time, or the text has a typo, editing is "
       "faster and keeps the buttons and media attached. Open the post from Message List, choose "
       "<b>Edit</b> / <b>Replace</b>, send the corrected text or a new date, and confirm the preview. "
       "The same controls are on <code>/edit</code>. Details: "
       "<a href=\"edit.html\">Edit Messages</a>.</p>"

       "<h3>Duplicate on purpose</h3>"
       "<p><b>Duplicate</b> in the message view, or <code>/dub &lt;message_id&gt;</code>, creates an "
       "exact copy — text, media and buttons. The bot asks for the date of the copy, then the channel, "
       "then shows a confirmation. That is the intended way to run the same announcement twice, or to "
       "build a variant from an existing post. If the copy was accidental, delete it the same way as "
       "any other post.</p>"

       "<h3>Prevent the next one</h3>"
       "<ul>"
       "<li>Read the preview: it names the channel, the date and the content. Two identical previews "
       "in a row means two jobs.</li>"
       "<li>Do not press Confirm twice if the bot seems slow — the job list is the source of truth, "
       "not the speed of the reply.</li>"
       "<li>When pasting a batch, check that each block has its own date line and that the block "
       "count matches the preview count (<a href=\"guide_schedule_format.html\">Schedule "
       "Format</a>).</li>"
       "<li><b>Import</b> creates new jobs; it does not merge into existing ones. Importing the same "
       "backup twice duplicates everything, so check the queue after an import.</li>"
       "</ul>"
   ),
   faq=[
       {'q': 'How do I delete just one scheduled message?',
        'a': ('Open Message List, tap the trash icon on that post and confirm — or use Delete by ID or '
              '<code>/delete</code> with the job ID. Only that post is removed.'),
        'links': ['delete', 'schedule_delete']},
       {'q': 'What is the difference between Delete All and deleting one post?',
        'a': ('Delete All removes every scheduled and recurring message for the channel after a '
              'confirmation showing the count. Deleting one post removes only the one you selected.'),
        'links': ['delete', 'message_list']},
       {'q': 'How do I copy a post to another date?',
        'a': ('Use <b>Duplicate</b> in the message view or <code>/dub &lt;message_id&gt;</code>. The '
              'bot asks for the new date and channel, then creates the copy with media and buttons '
              'intact.'),
        'links': ['edit', 'message_list']},
       {'q': 'Can I undo a deletion?',
        'a': ('No. Deleting a queued post is permanent. If you need the text back, export the queue '
              'first with <code>/export</code>, or edit instead of delete when the mistake is small.'),
        'links': ['export', 'edit']},
       {'q': 'Why did the same post get scheduled twice?',
        'a': ('Usually the same block was entered twice, Confirm was pressed twice, or a copy was made '
              'with Duplicate. An import of the same file also creates a second set of jobs. The '
              'preview count after scheduling tells you how many were created.'),
        'links': ['guide_schedule_format', 'import_data']},
   ])
