# -*- coding: utf-8 -*-
"""Blog articles, part 11 — the sender-bot-first setup rewrite.

Editorial rules are the same as the other blog_articles*.py batches: real
mechanics with real numbers, no marketing rounding. Every figure below is taken
from the code that implements it: 5 automatic checks per day
(src/services/admin_link_recheck.py), 15 permissions and the 7-day request
cooldown (src/channels/admins.py), 24-hour transfer TTL (same file), and the
default 3-day stand-in window with a 1-hour..30-day clamp
(src/services/main_bot_fallback.py).
"""

BLOG_ARTICLES_M = []


def _a(i, **kw):
    kw['id'] = i
    BLOG_ARTICLES_M.append(kw)


# ============================================================ UPDATES =====

_a('news-sender-bot-first-setup',
   category='tools',
   title='Sender Bot First, and a Real RBAC for Co-Admins',
   description=(
       'The setup no longer asks you to make the main bot a channel administrator. Connect your '
       'sender bot, add it from a green button, wait ten seconds, set the channel\'s time zone. Plus: '
       'co-admins join with the bot\'s @username, and 15 granular permissions.'
   ),
   date='2026-10-25',
   content=(
       "<p>Two things have been wrong with the setup for a while, and both came from the same "
       "assumption: that the main bot had to be a channel administrator. It never publishes, it does "
       "not hold the channel's settings, and its only job in the old flow was to verify your rights so "
       "it could hand the channel to a sender bot. That is a detour, not a feature — and it broke for "
       "everyone whose channel did not list <code>@FastSchedulerBot</code> as an administrator but did "
       "list their own bot.</p>"

       "<p>This release removes the detour. The setup now starts with the bot that actually does the "
       "work, and the main bot is optional. Everything else — one sender bot per channel, posts from "
       "your bot's name, per-channel limits — is unchanged.</p>"

       "<h3>What the first run looks like now</h3>"
       "<p><b>1. Connect a sender bot.</b> After <code>/start</code> the tutorial asks for one thing: "
       "your own bot. <b>Create bot</b> opens @BotFather with a name already prepared; <b>I Have a "
       "Token</b> accepts a token you already own. The token is verified with Telegram and the bot "
       "answers with a green <b>Open @your_bot</b> button.</p>"

       "<p><b>2. Add it to the channel from inside itself.</b> The sender bot opens on an \"I'm live\" "
       "screen instead of an empty dashboard. The first row is a green <b>Add bot to a channel</b> "
       "button that opens Telegram's own channel picker with the bot pre-selected as an administrator "
       "and <b>Post Messages</b> already ticked. After you confirm, the bot re-checks by itself ten "
       "seconds later and continues — no button hunt. Forwarding a post, sending <code>@username</code> "
       "or a <code>t.me</code> link, and adding the bot from a private channel's settings all still "
       "work.</p>"

       "<p><b>3. Set the zone for that channel.</b> A city, your current time, a shared location or a "
       "pick from the list. The zone is stored for that channel only; your account default is filled "
       "in only if you never set one, so channels you configured earlier keep exactly the zone they "
       "had.</p>"

       "<h3>The five-a-day recheck</h3>"
       "<p>That automatic ten-second check is capped at five taps per day per account, because each one "
       "is a real Telegram API call and a button is easy to hammer. The sixth tap still opens the "
       "channel picker — it just stops watching, and the screen says so. <b>Check Again</b> afterwards "
       "is unlimited and always was.</p>"

       "<h3>Adding another channel picks the bot first</h3>"
       "<p><b>Add New Channel</b> no longer starts with a channel link. It lists your idle sender bots; "
       "pick one and it opens with the connect flow already running, or create/connect a bot right "
       "there. A channel connected without a sender bot still stays locked — that part of the design was "
       "right.</p>"

       "<h3>Co-admins can now let themselves in</h3>"
       "<p>A channel only gets one sender bot, which used to mean a newly appointed channel "
       "administrator had to wait for the owner to add them here. Now, if the channel is already "
       "managed, any Telegram administrator can send that sender bot's <b>@username</b> (or its "
       "<b>token</b>) to the bot as a normal message. The bot asks Telegram, <i>through that sender "
       "bot</i>, whether the sender is an administrator of its channel. If yes, it grants the default "
       "permissions, notifies the owner with the person's name, and gives them a green button into the "
       "sender bot.</p>"

       "<p>The verification is rate-limited per account per hour, refused accounts (removed by the "
       "owner) cannot re-attach themselves, and a channel the owner marked as <b>Hide channel from "
       "strangers</b> is spoken about as <i>this channel</i> — no title, no username, no link, not even "
       "to the person joining.</p>"

       "<h3>Fifteen permissions, not a vague \"manage\" switch</h3>"
       "<p>Admin access is now a documented matrix instead of a set of grouped toggles: schedule, "
       "recurring, message list, preview, edit, change channel, delete, search, statistics, "
       "leaderboard, export, import, backup, hide channel, and change permissions. A new admin starts "
       "with seven of them on — scheduling, recurring, list, preview, edit, search and statistics — "
       "and everything that can remove or move content stays off until the owner grants it.</p>"

       "<p>Every check happens server-side when a button is pressed, not when the keyboard was drawn, so "
       "a permission taken away cannot be used from an old message. Requests are limited to one per "
       "permission per person per channel per week, revocations are stored with who and when (only the "
       "owner can restore), and Telegram-side removals revoke bot access automatically on the next "
       "sync. Ownership transfer still needs the typed phrase, the final button and the target's "
       "acceptance within 24 hours.</p>"

       "<h3>When your sender bot breaks</h3>"
       "<p>A new safety net exists, and it is deliberately narrow: if a send fails with an "
       "authentication or permission error (revoked token, bot removed from the channel, missing Post "
       "Messages), the main bot delivers that one post so a scheduled message is not silently lost, "
       "then asks once whether to keep standing in for up to <b>3 days</b>. It never starts on its own, "
       "it never runs for content errors, the window is clamped between an hour and a month, toggling "
       "it off and on cannot extend the deadline, and a \"no\" is remembered. This is the one thing the "
       "main bot needs Post Messages for — everything else it does is conversation.</p>"

       "<h3>What did not change</h3>"
       "<p>Every URL on this site, the Free and Premium limits, one sender bot per channel, per-channel "
       "quotas shared by admins, and the fact that your posts appear from your own bot. If you already "
       "have a working setup, nothing has to be reconnected — the new screens simply explain the same "
       "state more honestly.</p>"

       "<p>The help center has a full rewrite for this: <a href=\"../../help/a/sender_bot_setup.html\">the "
       "new setup</a>, <a href=\"../../help/a/admins.html\">Admins &amp; Access</a>, <a "
       "href=\"../../help/a/admins_attach.html\">joining a channel that already has a bot</a> and <a "
       "href=\"../../help/a/main_bot_stand_in.html\">the stand-in rules</a>.</p>"
   ),
   faq=[
       {'q': 'Do I have to remove the main bot from my channel?',
        'a': 'No. Keeping it as an administrator is optional and only used for the stand-in and support '
             'notices. Removing it changes nothing about publishing, which runs through your sender '
             'bot.'},
       {'q': 'Will existing channels need to be reconnected?',
        'a': 'No. Existing links keep working; the new flow only changes what a first-time setup asks '
             'for and how a channel is added later.'},
       {'q': 'Can a co-admin now see my other channels?',
        'a': 'No. Admin records are scoped to one channel, and every screen is filtered by that scope. '
             'Hidden channels are never named to non-owners, including co-admins.'},
   ])
