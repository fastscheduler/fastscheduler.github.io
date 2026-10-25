# -*- coding: utf-8 -*-
"""English help content for the sender-bot-first setup and the RBAC rewrite.

Consumed by ``tools/apply_rbac_help_v2.py``. Keys are help article ids; the
applier merges these records into ``translations/en.json`` and then validates
that nothing stale ("main bot must be an administrator") survives.

Editorial rules for this file (same as the rest of the help center):
  * ``## Heading`` starts a section, ``•`` starts a bullet;
  * ``<b>``/``<code>``/``<code>`` markup is allowed, no other HTML;
  * ``[[article_id|Label]]`` renders an internal help link;
  * numbers must match the bot's own constants (permissions, 7-day request
    cooldown, 24-hour transfer TTL, 5 automatic checks per day, 3-day default
    stand-in window) — never a rounded marketing figure.
"""

CONTENT_EN = {}

# =============================================================== ADMINS ====

CONTENT_EN['admins'] = {
    'title': 'Admins & Access (RBAC)',
    'description': (
        'The complete guide to channel access: who counts as an admin, the two '
        'ways to get access, what each role can do, how the owner stays in '
        'control, and what nobody else can ever see.'
    ),
    'content': (
        'Admins are other Telegram accounts that work on your channel without owning it. '
        'Access is decided in two layers: <b>Telegram</b> says who may administer the channel, '
        'and <b>Fast Scheduler</b> decides what each of those people may do inside the bot. '
        'Both layers must agree — a Telegram administrator with no bot permissions can open the '
        'sender bot and see only the features granted to them.\n\n'

        '## The three roles\n'
        '• <b>Main Owner</b> — the account that set the channel up. Has every permission, cannot '
        'be limited, and is the only role that can change permissions, remove admins or transfer '
        'ownership. There is exactly one per channel.\n'
        '• <b>Admin</b> — a Telegram administrator of that channel who was added to the bot. '
        'Works with the 15 permissions listed in [[admins_permissions|Permissions & Requests]]; '
        'new admins start with scheduling, recurring messages, message list, preview, edit, '
        'search and statistics on, and everything else off.\n'
        '• <b>Revoked</b> — someone the owner removed. Their record is kept (with who removed '
        'them and when) so they cannot quietly re-add themselves; only the owner can restore them.\n\n'

        '## Two ways to become an admin\n'
        '1. <b>The owner adds them.</b> Open the channel\'s <b>sender bot</b> → <b>⚙️ Settings</b> → '
        '<b>👥 Admins</b>. The bot syncs Telegram\'s administrator list and creates a record with the '
        'default permissions. Nothing is shared between channels.\n'
        '2. <b>A co-admin proves channel rights.</b> If the channel already has a sender bot, any '
        'existing Telegram administrator can send that bot\'s <b>@username</b> or <b>token</b> to the '
        'bot. The bot asks Telegram, through that sender bot, whether the requester is an '
        'administrator of its channel; if yes, the default permissions are granted and the owner is '
        'notified. Full walkthrough: [[admins_attach|Join a Channel That Already Has a Bot]].\n\n'

        '## Where it lives, and why\n'
        'Admin management lives inside the <b>sender bot of that channel</b>, never in the main bot. '
        'A sender bot runs exactly one channel, so a permission record has exactly one scope. The '
        'main bot knows nothing about who helps you.\n\n'

        '## Scope: one channel, nothing else\n'
        'An admin record is bound to one channel id. An admin of channel A cannot see channel B — '
        'not in the channel list, the message list, the statistics, the media storage, the bots '
        'menu, the export menu or any notification. They cannot see the owner\'s other channels '
        'either, and they never receive the owner\'s payment or expiry messages.\n\n'

        '## Enforcement is server-side, at click time\n'
        'Every button, every typed step and every deep link re-checks the permission when it is '
        'used, not when the keyboard was drawn. If a permission is taken away while an old message '
        'is still on screen, pressing its button answers "you do not have permission" and offers '
        '<b>Request permission from the admin</b> — it never performs the action. Telegram keyboards '
        'are just JSON in an old chat message; they are never trusted as proof of anything.\n\n'

        '## Privacy: Hide channel from strangers\n'
        'When the owner enables <b>Hide channel from strangers</b>, every non-owner — including '
        'co-admins and anyone verifying their rights with an @username — sees the channel as '
        '<i>this channel</i>. No title, no @username, no <code>t.me</code> link, no numeric id, '
        'in confirmations, refusals, owner notifications or audit screens. The owner always sees '
        'the real name. This setting is itself a permission '
        '(<code>settings_hide_channel</code>), so an admin cannot turn it off to look around.\n\n'

        '## Audit trail\n'
        'Every grant, permission save, revoke, restore, self-attach and ownership transfer is '
        'written to the RBAC audit log with the actor, the target, the channel, the timestamp and a '
        'short reason. "Who gave this person delete rights?" has an answer.\n\n'

        '## Automatic revocation\n'
        'On every sync the bot re-reads the channel\'s administrator list. If an admin was removed in '
        'Telegram, lost <b>Post Messages</b>, or was blocked by the owner, their bot access is '
        'revoked automatically — no manual cleanup, and no window in which a removed person keeps '
        'working from an old keyboard.\n\n'

        '## What an admin can never do\n'
        '• Take ownership without the owner starting a transfer and the target accepting it.\n'
        '• See or use the owner\'s sender bot token, or add/remove/rename bots.\n'
        '• Reach another channel of the same owner.\n'
        '• Grant permissions (unless the owner granted <code>settings_change_permissions</code>).\n'
        '• Delete the channel, its data or its audit history.\n'
        '• Enable the main-bot stand-in for a channel they do not control (owner or the settings '
        'permission only). See [[main_bot_stand_in|Main-Bot Stand-In]].\n\n'

        '## Related\n'
        '[[admins_attach|Join a Channel That Already Has a Bot]], '
        '[[admins_permissions|Permissions & Requests]], '
        '[[admins_limits|How Admins Share Limits]], '
        '[[admins_transfer|Ownership Transfer]], '
        '[[sender_bot_setup|Sender Bot First: the New Setup]].'
    ),
    'children': ['admins_attach', 'admins_permissions', 'admins_limits', 'admins_transfer'],
    'faq': [
        {
            'q': 'Can an admin take over my channel?',
            'a': 'No. Ownership only moves when the current Main Owner starts a transfer, types the '
                 'confirmation phrase, and the target accepts it within 24 hours. An admin cannot '
                 'start that flow and cannot grant themselves the permission to do it.',
            'links': ['admins_transfer'],
        },
        {
            'q': 'Why does the main bot no longer need to be a channel administrator?',
            'a': 'Because it no longer touches the channel. Your sender bot publishes, and the main '
                 'bot only talks to you. The one exception is the optional stand-in: if you enable it '
                 'and your sender bot breaks, the main bot posts on your behalf for a bounded window, '
                 'and for that it needs Post Messages like any other bot.',
            'links': ['sender_bot_setup', 'main_bot_stand_in'],
        },
        {
            'q': 'An admin says the bot refuses them, but they are an administrator in Telegram.',
            'a': 'Check three things: that they opened the <b>sender bot</b> of that channel (not the '
                 'main bot), that their Telegram rights include <b>Post Messages</b>, and that they '
                 'were not revoked by the owner. A revoked admin stays blocked until the owner '
                 'restores them from Settings → Admins → Revoked.',
            'links': ['admins_permissions', 'bot_permissions'],
        },
        {
            'q': 'Can two people manage the same channel without sharing a login?',
            'a': 'Yes — that is exactly what admins are for. Each person connects their own Telegram '
                 'account, gets their own permissions, and every action is attributed to them in the '
                 'audit log. Nobody shares a token or a password.',
            'links': ['admins_attach', 'admins_limits'],
        },
        {
            'q': 'Do admins share the channel\'s message limits?',
            'a': 'Yes. Scheduled slots, monthly sends, recurring rules and media storage belong to the '
                 'channel, so every admin draws from the same quota. See [[admins_limits|How Admins '
                 'Share Limits]] for the counters that reset and the ones that do not.',
            'links': ['admins_limits', 'limits'],
        },
        {
            'q': 'How do I remove someone completely?',
            'a': 'Settings → Admins → their profile → Remove. Their access ends immediately and the '
                 'record moves to Revoked with the reason and timestamp. Queued posts stay with the '
                 'channel — they belong to the channel, not to the person who typed them.',
            'links': ['admins_permissions'],
        },
    ],
}

CONTENT_EN['admins_attach'] = {
    'title': 'Join a Channel That Already Has a Bot',
    'description': (
        'You are a channel administrator, the channel already has a sender bot, and the owner is '
        'away: how to prove your rights with the bot\'s @username or token and get access without '
        'touching a single button.'
    ),
    'content': (
        'A channel can only have one sender bot. If you are a newly added Telegram administrator and '
        'the channel is already managed here, you do not need the owner to do anything: prove your '
        'rights once and the bot grants you the default admin permissions itself.\n\n'

        '## What to send\n'
        'Send either of these as a normal message to the bot:\n'
        '• the sender bot\'s <b>@username</b> — for example <code>@My_Channel_Bot</code>; or\n'
        '• the sender bot\'s <b>token</b> — the <code>1234567890:ABCdef…</code> line from @BotFather.\n'
        'You can send it to the <b>main bot</b> or to the sender bot itself; both understand it. Do '
        'not press any menu button first — the message alone is the request.\n\n'

        '## What happens next\n'
        '1. The bot resolves the username (or calls <code>getMe</code> on the token) and finds which '
        'channel that sender bot serves.\n'
        '2. It asks Telegram, <i>through that sender bot</i>, what your status is in that channel.\n'
        '3. If Telegram reports <b>administrator</b> or <b>creator</b>, you are added with the '
        'default permissions: scheduling, recurring messages, message list, preview, edit, search '
        'and statistics — everything else stays off until the owner grants it.\n'
        '4. The owner receives a notification naming you (and naming the channel only if it is not '
        'hidden), so access is never silent.\n'
        '5. You get a green <b>Open @bot</b> button that drops you straight into the sender bot.\n\n'

        '## If it is refused\n'
        '• <b>"I couldn\'t confirm you as an administrator"</b> — Telegram does not list you as an '
        'administrator of that channel, or your account is not the one sending the message. Ask for '
        'the administrator role first, then retry.\n'
        '• <b>"Access was revoked"</b> — the owner removed you on purpose. Only the owner can restore '
        'you (Settings → Admins → Revoked).\n'
        '• <b>"That bot isn\'t connected to a channel yet"</b> — the sender bot exists but was never '
        'attached; ask the owner to connect it first.\n'
        '• <b>"Too many attempts"</b> — the verification endpoint is rate-limited to a handful of '
        'tries per hour per account, because it is probeable. Wait an hour; nothing is lost.\n\n'

        '## Privacy when the channel is hidden\n'
        'If the owner enabled <b>Hide channel from strangers</b>, the confirmation you receive says '
        '<i>this channel</i> and never shows the title, @username, link or numeric id. That is not a '
        'bug and not a sign of a wrong bot — it is the owner\'s setting, and it applies to admins '
        'too. Your access is still real; ask the owner for the link if you need it.\n\n'

        '## About the token\n'
        'Sending a bot token to the bot you are trying to join is how the verification reads your '
        'rights through that bot. It is used for the check and is not echoed back. Still treat a '
        'token like a password: send it only inside a private chat with the bot, never in a group, a '
        'comment thread or a screenshot. If you are not comfortable sending it, the @username is '
        'enough — the bot can resolve it from its own records.\n\n'

        '## Permissions you get, and changing them\n'
        'The defaults are intentionally conservative. Everything is listed in '
        '[[admins_permissions|Permissions & Requests]], and the owner can change each one '
        'individually. If you need more, use <b>Request permission from the admin</b> on any refusal '
        'screen instead of asking the owner in a private chat — the request carries the exact '
        'permission and lands in the owner\'s queue.\n\n'

        '## Related\n'
        '[[admins|Admins & Access]], [[sender_bot_setup|Sender Bot First: the New Setup]], '
        '[[channel_permissions|Channel Permissions]].'
    ),
    'children': None,
    'faq': [
        {
            'q': 'Do I need to know the owner\'s Telegram account?',
            'a': 'No. The bot resolves the channel from the sender bot itself and notifies the owner '
                 'on its own. You never have to find or message them.',
            'links': ['admins'],
        },
        {
            'q': 'Will the owner see that I joined?',
            'a': 'Yes, immediately — with your name, the bot you used, and the channel unless it is '
                 'hidden. Every attach is also written to the audit log.',
            'links': ['admins'],
        },
        {
            'q': 'Can I do this if I am not a Telegram administrator yet?',
            'a': 'No, and it is not a bug. The bot only mirrors rights Telegram already granted; it '
                 'does not create channel administrators. Ask an owner to promote you first.',
            'links': ['channel_permissions'],
        },
        {
            'q': 'The @username is right but the bot says it is not connected.',
            'a': 'That sender bot exists but has no channel attached yet. Ask the owner to finish its '
                 'setup — the bot cannot grant access to a channel it does not serve.',
            'links': ['sender_bot_setup'],
        },
    ],
}

CONTENT_EN['admins_permissions'] = {
    'title': 'Permissions & Requests',
    'description': (
        'Every grantable right, what it unlocks, the defaults a new admin gets, how changes are '
        'saved, how requests work (one per permission per week), and how revocation behaves.'
    ),
    'content': (
        'The Main Owner controls exactly what each admin can do. There are 15 independent '
        'permissions; nothing is bundled behind a vague "manage" switch, and nothing is granted '
        'implicitly.\n\n'

        '## The full list\n'
        '• <code>schedule</code> — create scheduled messages. <i>On by default.</i>\n'
        '• <code>recurring</code> — create recurring messages. <i>On by default.</i>\n'
        '• <code>message_list</code> — open the message list. <i>On by default.</i>\n'
        '• <code>message_preview</code> — preview a message before it goes out. <i>On by default.</i>\n'
        '• <code>message_edit</code> — edit a queued message. <i>On by default.</i>\n'
        '• <code>message_change</code> — move a message to another channel. <i>Off by default.</i>\n'
        '• <code>message_delete</code> — delete a queued message. <i>Off by default.</i>\n'
        '• <code>message_search</code> — search the channel\'s messages. <i>On by default.</i>\n'
        '• <code>stats_view</code> — view statistics for the channel. <i>On by default.</i>\n'
        '• <code>leaderboard_view</code> — view the channel leaderboard. <i>Off by default.</i>\n'
        '• <code>data_export</code> — export the channel\'s data. <i>Off by default.</i>\n'
        '• <code>data_import</code> — import messages into the channel. <i>Off by default.</i>\n'
        '• <code>data_backup</code> — create a backup of the channel. <i>Off by default.</i>\n'
        '• <code>settings_hide_channel</code> — turn "Hide channel from strangers" on or off. '
        '<i>Off by default.</i>\n'
        '• <code>settings_change_permissions</code> — change other admins\' permissions. '
        '<i>Off by default.</i>\n\n'

        '## Grouped in the interface, separate in the database\n'
        'The editor groups them to keep the keyboard readable — Messages (list, preview, edit, '
        'change, delete, search), Statistics (stats, leaderboard), Data (export, import, backup), '
        'Settings (hide channel, change permissions). Tapping a group opens its individual switches. '
        'Saving the group saves each switch exactly as shown; there is no hidden "group unlock".\n\n'

        '## Changing them\n'
        'Owner → <b>⚙️ Settings</b> → <b>👥 Admins</b> → pick the admin → toggle. Changes accumulate '
        'as a draft; <b>Save Changes</b> applies them and shows a summary of what changed. Leaving '
        'with unsaved toggles asks whether to save or discard, so a half-configured admin is never '
        'applied silently.\n\n'

        '## Effect is immediate\n'
        'Disabled features disappear from that admin\'s keyboard on the next screen. If they press an '
        'old button from chat history, the bot refuses with "you do not have permission" and offers '
        '<b>Request permission from the admin</b>. The check happens when the button is pressed, not '
        'when it was drawn.\n\n'

        '## Requests\n'
        'An admin who lacks a permission can request it, optionally with a one-line reason. The '
        'owner receives the request with <b>Grant</b> / <b>Deny</b> (and can reply when denying). '
        'Anti-spam: <b>one request per permission per user per channel per week</b>. A granted '
        'request is a normal permission change and appears in the audit log; a denied one does not '
        'block asking again after the cooldown.\n\n'

        '## Removing and restoring\n'
        'Removing an admin revokes access at once and stores the record in <b>Revoked</b> with the '
        'reason, the actor and the timestamp. A revoked person cannot re-attach themselves through '
        'the @username path — only the owner can restore them. Queued posts stay with the channel; '
        'deleting an admin never deletes content they created.\n\n'

        '## Automatic revocation from Telegram\n'
        'Rights Telegram takes away, the bot takes away: losing the administrator role or the '
        '<b>Post Messages</b> right revokes bot access on the next sync. The reverse is not '
        'automatic — becoming a Telegram administrator does not grant bot permissions; the owner or '
        'the self-attach flow does.\n\n'

        '## What cannot be granted\n'
        'Ownership, the owner\'s bot token, adding or renaming bots, other channels, payment and '
        'billing data, and the RBAC audit log are never delegable. If an admin needs something that '
        'is not in the list above, the answer is a different role, not a wider permission.\n\n'

        '## Related\n'
        '[[admins|Admins & Access]], [[admins_attach|Join a Channel That Already Has a Bot]], '
        '[[admins_transfer|Ownership Transfer]], [[bot_permissions|Bot Permissions]].'
    ),
    'children': None,
    'faq': [
        {
            'q': 'What exactly does a brand-new admin get?',
            'a': 'Seven permissions on: schedule, recurring, message list, preview, edit, search and '
                 'statistics. Everything else — move, delete, leaderboard, export, import, backup, '
                 'hide channel, change permissions — stays off until the owner grants it.',
            'links': ['admins'],
        },
        {
            'q': 'How often can an admin ask for a permission?',
            'a': 'Once per permission per week per channel. The cooldown is per permission, so asking '
                 'for export does not delay a later request for statistics.',
            'links': ['admins'],
        },
        {
            'q': 'Why did a granted permission stop working by itself?',
            'a': 'Either the admin lost the Telegram side (administrator role or Post Messages), or '
                 'the owner saved a new permission set. Both are recorded in the audit log with the '
                 'time and the actor.',
            'links': ['bot_permissions'],
        },
        {
            'q': 'Does "change permissions" let an admin promote themselves?',
            'a': 'No. <code>settings_change_permissions</code> lets them edit other admins\' switches, '
                 'but never their own record and never ownership. Only the Main Owner can edit the '
                 'owner record.',
            'links': ['admins_transfer'],
        },
        {
            'q': 'Can I give someone temporary access?',
            'a': 'Yes, in practice: grant the permissions, and remove them when the work is done. '
                 'Removal is immediate, and the restored-then-revoked history stays in the audit log.',
            'links': ['admins'],
        },
    ],
}

CONTENT_EN['admins_limits'] = {
    'title': 'How Admins Share Limits',
    'description': (
        'Limits belong to the channel, not to the person: how scheduled slots, monthly sends, '
        'recurring rules and media storage are shared between the owner and every admin.'
    ),
    'content': (
        'All message limits are <b>per channel</b>. Every admin of that channel draws from the same '
        'quota, which is the whole point: a channel cannot multiply its allowance by adding people.\n\n'

        '## What is shared\n'
        '• pending scheduled messages ({scheduled_free} on Free per channel);\n'
        '• sends per month ({monthly_sent_free} per channel on Free);\n'
        '• active recurring rules ({recurring_free} on Free);\n'
        '• the channel\'s media storage and its per-file size cap;\n'
        '• the channel\'s bot slots (one sender bot per channel).\n\n'

        '## What that means in practice\n'
        'If the channel\'s pending cap is 100 and one admin queues 90, the other admin has 10 left. '
        'The limit message does not care who filled the queue, and neither does the counter.\n\n'

        '## Monthly counter\n'
        'It counts messages actually <b>sent</b>, not created. Deleting a queued post does not refund '
        'a send; the counter resets on the 1st of the next month, or when Premium activates for the '
        'channel.\n\n'

        '## Premium\n'
        'Premium is bought per account, but its allowances apply to the channels that account owns. A '
        'co-admin does not bring their own Premium to someone else\'s channel — and cannot be charged '
        'for it either. If the channel needs more, the owner upgrades.\n\n'

        '## Planning with several people\n'
        'Keep the Message List open: it is the shared source of truth for what is queued. Delete by '
        'ID is the safe way to remove a specific post without touching anyone else\'s work. Two '
        'admins scheduling the same slot is allowed — the bot does not deduplicate, and both posts '
        'will be sent.\n\n'

        '## Related\n'
        '[[limits|Limits Overview]], [[admins_permissions|Permissions & Requests]], '
        '[[limit_scheduled|Scheduled Limit]].'
    ),
    'children': None,
    'faq': [
        {
            'q': 'Do admins each get their own monthly allowance?',
            'a': 'No. One channel, one allowance. Adding admins adds hands, not quota.',
            'links': ['limits'],
        },
        {
            'q': 'If an admin deletes a queued post, is the send refunded?',
            'a': 'No. The monthly counter tracks sends performed, not messages sitting in the queue. '
                 'Deleting before the send time removes the post and frees a queue slot, but the '
                 'counter only moves when something is actually delivered.',
            'links': ['admins_permissions'],
        },
    ],
}

CONTENT_EN['admins_transfer'] = {
    'title': 'Ownership Transfer',
    'description': (
        'Moving the Main Owner role safely: the typed confirmation phrase, the final button, the '
        'target\'s acceptance, the 24-hour expiry, and what happens to both accounts afterwards.'
    ),
    'content': (
        'Transferring ownership is deliberately hard to do by accident — and impossible to do alone.\n\n'

        '## Preconditions\n'
        '• The target must already be an <b>admin of the channel in the bot</b>. Add them first.\n'
        '• The target must still be a Telegram administrator with <b>Post Messages</b>; the bot '
        're-checks this at every step.\n'
        '• Only one transfer can be pending per channel. Cancel the current one before starting '
        'another.\n\n'

        '## The flow\n'
        '1. Owner opens the target admin\'s profile → <b>👑 Make Main Owner</b>.\n'
        '2. The bot asks the owner to type an exact confirmation phrase naming the channel and the '
        'target. A copy-paste of a different phrase is rejected.\n'
        '3. A final confirm button appears; no request exists before it is pressed.\n'
        '4. The target receives the request and must <b>accept</b> or <b>decline</b>.\n\n'

        '## While it is pending\n'
        'The current owner can cancel at any time. The request expires after <b>24 hours</b>, and an '
        'expired request changes nothing. During this window the current owner keeps full rights — '
        'there is no half-transferred state.\n\n'

        '## On acceptance\n'
        'The target becomes Main Owner. The previous owner stays as a <b>regular admin with full '
        'permissions</b> — they do not lose access, but they can no longer change permissions or '
        'start another transfer. Both sides are notified, and the change is written to the audit log.\n\n'

        '## If it goes wrong\n'
        'Before acceptance: cancel. After acceptance: the new owner can transfer it back with the '
        'same flow, which is why the typed phrase exists — it is a speed bump against a rushed '
        'handover, not a lock.\n\n'

        '## Why so many steps\n'
        'Ownership controls permissions, exports, backups and the stand-in decision. A single '
        'mis-tap that silently handed that to the wrong account would be unrecoverable without '
        'support, so the design pays for itself the first time someone fat-fingers a keyboard.\n\n'

        '## Related\n'
        '[[admins|Admins & Access]], [[admins_permissions|Permissions & Requests]], '
        '[[main_bot_stand_in|Main-Bot Stand-In]].'
    ),
    'children': None,
    'faq': [
        {
            'q': 'Does the old owner lose access?',
            'a': 'No. They become a regular admin with every permission on. They lose only the '
                 'owner-only powers: editing permissions, removing admins and starting transfers.',
            'links': ['admins'],
        },
        {
            'q': 'What if the target never answers?',
            'a': 'The request expires after 24 hours and nothing changes. Start a new one when both '
                 'people are online.',
            'links': ['admins_permissions'],
        },
        {
            'q': 'Can I transfer to someone who is not an admin yet?',
            'a': 'No. Add them as an admin first, let them open the sender bot once, then start the '
                 'transfer.',
            'links': ['admins_attach'],
        },
    ],
}

# ======================================================= SENDER-FIRST =====

CONTENT_EN['sender_bot_setup'] = {
    'title': 'Sender Bot First: the New Setup',
    'description': (
        'The rewritten first run: connect your own sender bot, add it to the channel from a green '
        'button, wait ten seconds, then set the channel\'s time zone — and why the main bot is now '
        'optional.'
    ),
    'content': (
        'The setup now starts with the bot that actually does the work: <b>your sender bot</b>. The '
        'main bot is no longer a channel administrator, and you never have to add it to the channel '
        'just to get started.\n\n'

        '## Why the order changed\n'
        'Making the main bot a channel admin was a detour: it does not publish, it does not hold the '
        'channel\'s settings, and its only job in the old flow was to verify rights so it could hand '
        'the channel to a sender bot. Now the sender bot verifies itself, in its own chat, and the '
        'main bot stays a chat with a menu.\n\n'

        '## Step 1 — connect a sender bot\n'
        'On the first <code>/start</code>, after the welcome screen, the bot asks for a sender bot and '
        'nothing else:\n'
        '• <b>➕ Create bot</b> opens @BotFather with a name already prepared;\n'
        '• <b>🔑 I Have a Token</b> accepts a token you already have.\n'
        'The token is verified with Telegram, stored, and the bot answers with a green <b>Open '
        '@your_bot</b> button. One sender bot serves exactly one channel.\n\n'

        '## Step 2 — add it to the channel from inside itself\n'
        'Open the sender bot and it shows the "I\'m live" screen. The first row is a green '
        '<b>➕ Add bot to a channel</b> button:\n'
        '1. Tap it. Telegram\'s own channel picker opens with the bot pre-selected as an '
        'administrator and <b>Post Messages</b> already ticked.\n'
        '2. Pick the channel and confirm.\n'
        '3. The bot re-checks by itself after <b>10 seconds</b> and continues to the time zone when '
        'the rights are there. You do not have to press anything.\n\n'

        '## The five-a-day rule\n'
        'That automatic re-check is capped at <b>5 taps per day</b> per account, because each one is '
        'a real Telegram API call and the button is easy to hammer. The 6th tap still opens the '
        'picker — it just stops auto-checking, and the screen says so. Use <b>🔄 Check Again</b> '
        'afterwards; manual checks are unlimited.\n\n'

        '## Other ways to connect\n'
        '• <b>Forward any post</b> from the channel to the sender bot.\n'
        '• Send the channel\'s <code>@username</code> or a <code>t.me</code> link.\n'
        '• <b>Private channel?</b> Add the sender bot as an administrator from the channel\'s own '
        'settings; the bot picks it up through Telegram\'s update, no link needed.\n'
        '• The channel already has a sender bot and you are a co-admin? Send that bot\'s '
        '<b>@username</b> or <b>token</b> — see [[admins_attach|Join a Channel That Already Has a Bot]].\n\n'

        '## Step 3 — the time zone belongs to the channel\n'
        'The last screen asks for a zone and accepts a city (<code>London</code>), your current time '
        '(<code>15:30</code>), a shared location, or a pick from the list. The zone is stored for '
        '<b>that channel only</b>. Your account default is filled in only if you never set one, so '
        'channels you configured earlier keep exactly the zone they had. Nothing is applied to all '
        'channels behind your back.\n\n'

        '## The main bot is optional — but it earns its place\n'
        'You can delete it from the channel list and everything keeps working; publishing, '
        'statistics, backups and admin management all live in the sender bot. The reasons to keep it '
        'as an administrator anyway:\n'
        '• <b>Stand-in during an outage.</b> If your sender bot\'s token is revoked or it loses '
        'rights, the main bot can deliver the scheduled post once and offer to keep posting for a '
        'bounded window (3 days by default). It needs <b>Post Messages</b> for that, and it never '
        'starts on its own. See [[main_bot_stand_in|Main-Bot Stand-In]].\n'
        '• <b>Support and expiry notices</b> arrive in the main bot chat.\n'
        '• <b>Recovery</b> — if you lose the sender bot entirely, the main bot is where you reconnect '
        'a new one.\n\n'

        '## Adding more channels later\n'
        '<b>➕ Add New Channel</b> in the main bot no longer asks for a channel link first. It lists '
        'your idle sender bots; pick one and it opens with the connect flow already running. No idle '
        'bot? Create or connect one right there. A channel connected without a sender bot stays '
        'locked, by design.\n\n'

        '## Troubleshooting\n'
        '• <b>"@bot is not an administrator yet"</b> — tap the green Add button and make sure Post '
        'Messages is ticked, then Check Again.\n'
        '• <b>Auto-check paused</b> — you used today\'s five. Tap Check Again after adding the bot.\n'
        '• <b>Wrong time zone</b> — change it per channel in the sender bot; it does not touch other '
        'channels.\n'
        '• <b>Channel already managed</b> — the bot names the existing sender bot and explains the '
        '@username/token route.\n\n'

        '## Related\n'
        '[[tutorial_walkthrough|The First-Run Tutorial]], '
        '[[admins_attach|Join a Channel That Already Has a Bot]], '
        '[[main_bot_stand_in|Main-Bot Stand-In]], [[bot_add|Add a Sender Bot]].'
    ),
    'children': None,
    'faq': [
        {
            'q': 'Do I still have to add @FastSchedulerBot to my channel?',
            'a': 'No. Publishing, scheduling, statistics and settings all run through your sender bot. '
                 'The main bot only needs Post Messages if you want the optional stand-in during an '
                 'outage.',
            'links': ['main_bot_stand_in'],
        },
        {
            'q': 'Why does the bot wait ten seconds instead of continuing instantly?',
            'a': 'Because Telegram delivers the "bot promoted to administrator" update on its own '
                 'schedule; a second is often not enough. Ten seconds is a compromise between a '
                 'silent wait and a screen that lies about the result.',
            'links': ['admins'],
        },
        {
            'q': 'What happens after the five automatic checks?',
            'a': 'The button still opens the channel picker, but the bot stops watching for the '
                 'promotion. Finish adding the bot, come back, and press Check Again — that path is '
                 'not limited.',
            'links': ['sender_bot_setup'],
        },
        {
            'q': 'Does the time zone I set change my other channels?',
            'a': 'No. It is saved for that channel only. The account default is written only if it is '
                 'still empty, so previously configured channels are never rewritten.',
            'links': ['timezone_set', 'admins_limits'],
        },
        {
            'q': 'Can I connect a channel without a sender bot?',
            'a': 'You can attach it in the main bot as an escape hatch, but scheduling stays locked: '
                 'posts go out through a bot, and every channel needs its own. See '
                 '[[bot_sender|Posting as Your Bot]].',
            'links': ['bot_sender'],
        },
    ],
}

CONTENT_EN['main_bot_stand_in'] = {
    'title': 'Main-Bot Stand-In',
    'description': (
        'When your sender bot breaks, the main bot can keep the queue alive for a bounded, opt-in '
        'window: what triggers it, what it posts, how long it lasts, and the guards against abuse.'
    ),
    'content': (
        'A sender bot can stop working at the worst moment: token revoked in @BotFather, removed from '
        'the channel, or Telegram refusing its rights. The stand-in is the safety net — and it is '
        'deliberately narrow.\n\n'

        '## What triggers it\n'
        'Only a <b>sender authentication or permission failure</b>: revoked or invalid token, bot '
        'removed from the channel, missing <b>Post Messages</b>. Content errors, timeouts, rate limits '
        'and channel-level restrictions never trigger it, because the main bot would hit exactly the '
        'same wall — resending those would only produce duplicates or a second failure.\n\n'

        '## What you see\n'
        '1. The post is delivered <b>once</b> by the main bot, so a scheduled message is not silently '
        'lost.\n'
        '2. Immediately afterwards the bot asks, once: keep posting from the main bot for up to N '
        'days while the sender bot is broken?\n'
        '3. <b>Yes</b> enables the stand-in for that channel for the current window. <b>No</b> records '
        'the refusal — the channel will not be asked again, and failed posts are reported as errors.\n\n'

        '## The window\n'
        'The default is <b>3 days</b> per activation. The operator can change the default and set a '
        'per-sender-bot override; the range is 1 hour to 30 days. When the window ends the stand-in '
        'stops by itself, the next failure is reported normally, and the message says the window is '
        'over. There is no "renews automatically".\n\n'

        '## Who can enable it\n'
        'The channel owner, or an admin holding <code>settings_change_permissions</code>. Nobody else '
        '— it is a channel-wide decision that changes who publishes, not a personal preference.\n\n'

        '## Guards against abuse\n'
        '• <b>Opt-in, never automatic.</b> Delivering the first lost post is a rescue; continuing is a '
        'choice.\n'
        '• <b>Toggle-off-then-on cannot extend the deadline.</b> Re-enabling inside the cooldown keeps '
        'the original expiry.\n'
        '• <b>One prompt per channel per cooldown window</b> — no notification spam while an owner is '
        'already fixing the bot.\n'
        '• <b>Bounded window</b>, clamped server-side, never "forever".\n'
        '• <b>Audited.</b> Enable, decline, revert and expiry are all written to the log with the '
        'actor.\n'
        '• <b>Global kill switch.</b> The operator can disable stand-ins for every channel at once, '
        'for example during an incident.\n\n'

        '## Ending it early\n'
        'The confirmation message carries <b>⛔ Stop the stand-in now</b>. You can also open the '
        'channel\'s settings screen: the active window is shown with the remaining time and the same '
        'button. Ending it does not delete anything — the queue simply goes back to failing loudly if '
        'the sender bot is still broken.\n\n'

        '## What it is not\n'
        'It is not a second scheduler, it does not post from your sender bot\'s name (posts appear '
        'from the main bot, and readers can tell), it does not fix the token, and it does not bypass '
        'your channel\'s permissions. It buys time to fix the real problem — nothing more.\n\n'

        '## For operators\n'
        'The <code>/fallback</code> command controls the feature: <code>/fallback</code> shows the '
        'current default, overrides and active stand-ins; <code>/fallback on|off</code> switches it '
        'globally; <code>/fallback days 72h</code> sets the default window; '
        '<code>/fallback @bot 12h</code> sets a per-bot override; <code>/fallback reset @bot</code> '
        'drops it; <code>/fallback revert all</code> stops every active stand-in. It is restricted to '
        'the bot\'s operators.\n\n'

        '## Related\n'
        '[[sender_bot_setup|Sender Bot First: the New Setup]], '
        '[[bot_permissions|Bot Permissions]], [[error_forbidden|"Bot Is Not an Admin" Errors]], '
        '[[admins|Admins & Access]].'
    ),
    'children': None,
    'faq': [
        {
            'q': 'Will readers know the main bot posted instead of my bot?',
            'a': 'Yes — the author of a Telegram message is the bot that sent it. That is the honest '
                 'trade-off: a post from a bot your readers do not follow, instead of no post at all.',
            'links': ['bot_sender'],
        },
        {
            'q': 'Does the stand-in start without me saying yes?',
            'a': 'Only the first rescue post is automatic, and that is what saves the scheduled '
                 'message. Everything after it waits for an explicit yes.',
            'links': ['sender_bot_setup'],
        },
        {
            'q': 'I tapped No — can I change my mind?',
            'a': 'Yes, by enabling it from the channel settings screen. The refusal only means the bot '
                 'stops asking on its own.',
            'links': ['admins'],
        },
        {
            'q': 'Why did it stop in the middle of an outage?',
            'a': 'The window ended. It is a fixed duration from the moment you enabled it, not a '
                 'countdown that pauses while you are busy. Fix the sender bot and the queue resumes.',
            'links': ['bot_permissions'],
        },
    ],
}

# ==================================================== FLOW-WIDE REWRITES ==

CONTENT_EN['onboarding_step1'] = {
    'title': 'Tutorial Step 1: Connect Your Sender Bot',
    'description': (
        'The first tutorial screen asks for one thing only — your own sender bot. What the two '
        'buttons do, what a token looks like, and what success looks like.'
    ),
    'content': (
        'The tutorial starts with the bot that will actually publish, not with a channel link. You do '
        'not need a channel yet, and you do not need to make @FastSchedulerBot an administrator '
        'anywhere.\n\n'

        '## The screen\n'
        'It explains that a sender bot is your own Telegram bot, then offers:\n'
        '• <b>➕ Create bot</b> — opens @BotFather with a name and username already prepared. '
        'Confirm in BotFather, copy the token it prints, come back.\n'
        '• <b>🔑 I Have a Token</b> — paste a token from a bot you already created.\n'
        '• <b>⏭ Skip tutorial</b> — asks for confirmation and ends the tutorial. You can connect a '
        'sender bot later from <b>🤖 Bots</b>.\n\n'

        '## What a token looks like\n'
        '<code>1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ</code> — one line, a number, a colon, then '
        'letters and digits. If the bot says the token is invalid, the copy was truncated; copy the '
        'whole line again.\n\n'

        '## What success looks like\n'
        'The bot verifies the token with Telegram and answers with <b>Token saved for @your_bot</b> '
        'plus a green <b>Open @your_bot</b> button. Tap it: the channel and the time zone are '
        'connected there, inside the sender bot. The tutorial on the main-bot side is finished at '
        'that point — there is no third step here to come back for.\n\n'

        '## If it fails\n'
        '• <b>Invalid token</b> — truncated copy, or a token that was already revoked.\n'
        '• <b>That is the main bot\'s token</b> — create your own bot; the shared bot cannot post as '
        'you.\n'
        '• <b>Limit reached</b> — the Free plan allows {bots_free} sender bot; see '
        '[[limit_bots|Sender Bot Limit]].\n'
        '• <b>Nothing happens</b> — make sure you are in a private chat with the bot, not a group.\n\n'

        '## Related\n'
        '[[sender_bot_setup|Sender Bot First: the New Setup]], [[bot_add|Add a Sender Bot]], '
        '[[onboarding_step2|Tutorial Step 2: Channel and Time Zone]].'
    ),
    'children': None,
}

CONTENT_EN['onboarding_step2'] = {
    'title': 'Tutorial Step 2: Channel and Time Zone (in the Sender Bot)',
    'description': (
        'The rest of the setup happens inside your sender bot: add it to the channel, let the '
        '10-second check finish, then set the zone for that channel only.'
    ),
    'content': (
        'Once the sender bot is connected, open it with the green button. It shows the "I\'m live" '
        'screen, because it has no channel yet.\n\n'

        '## Connect the channel\n'
        '1. Tap the green <b>➕ Add bot to a channel</b> row.\n'
        '2. Telegram opens its channel picker with the bot pre-selected as an administrator and '
        '<b>Post Messages</b> ticked. Choose the channel and confirm.\n'
        '3. The bot re-checks on its own after <b>10 seconds</b> (5 automatic checks per day) and '
        'continues automatically.\n'
        'Forwarding a post, sending <code>@username</code> or adding the bot from a private '
        'channel\'s settings works just as well.\n\n'

        '## Set the zone\n'
        'The link confirmation asks for the zone straight away: a city (<code>London</code>), the '
        'current time (<code>15:30</code>), a shared location, or a pick from the list. It is saved '
        'for <b>this channel</b>; your other channels keep theirs, and the account default is filled '
        'only if it was never set.\n\n'

        '## Done\n'
        'The last screen is <b>All set — your time zone</b> with a dashboard button. Scheduling, statistic, '
        'backups and admin management all live here from now on.\n\n'

        '## Related\n'
        '[[onboarding_step1|Tutorial Step 1: Connect Your Sender Bot]], '
        '[[sender_bot_setup|Sender Bot First: the New Setup]], [[timezone_set|Set a Time Zone]].'
    ),
    'children': None,
}

CONTENT_EN['onboarding_step3'] = {
    'title': 'After the Tutorial: Your Sender Bot Dashboard',
    'description': (
        'The tutorial ends when the sender bot is connected. This is the dashboard you land on, what '
        'each row does, and where the old "Step 3" content moved.'
    ),
    'content': (
        'The first-run tutorial is two steps now — sender bot, then channel and time zone inside it. '
        'There is no third on-screen step to hunt for; this article covers where the rest of the '
        'old flow went.\n\n'

        '## What you land on\n'
        'After the time zone is saved the sender bot shows the dashboard: <b>📅 Schedule</b>, '
        '<b>🔁 Recurring</b>, <b>📋 Messages</b>, <b>📊 Statistics</b>, <b>⚙️ Settings</b> (admins, '
        'backups, hide channel) and <b>🌐 Language</b>. Rows disappear for anyone without the '
        'matching permission, so a co-admin sees a shorter, honest menu.\n\n'

        '## Where old Step 3 went\n'
        'The old third step asked you to promote the sender bot in the channel and press Check Again. '
        'That is now part of the "Add bot to a channel" button inside the sender bot: the picker '
        'grants the rights, and the automatic 10-second check replaces the manual verification. If '
        'you added the bot by hand, the screen still offers <b>🔄 Check Again</b>.\n\n'

        '## Adding people\n'
        'Settings → <b>👥 Admins</b> is where co-admins are added, limited and removed. Read '
        '[[admins|Admins & Access]] before handing out delete or export rights; the defaults are '
        'deliberately conservative.\n\n'

        '## Related\n'
        '[[sender_bot_setup|Sender Bot First: the New Setup]], [[admins|Admins & Access]], '
        '[[start_schedule|Schedule Your First Post]].'
    ),
    'children': None,
}

CONTENT_EN['gs_step1'] = {
    'title': 'Step 1: Connect Your Sender Bot',
    'description': (
        'Start with the bot that publishes. Create it in @BotFather or paste an existing token, and '
        'open it from the green button that follows.'
    ),
    'content': (
        'Every channel is served by its own sender bot: a Telegram bot you own that posts under its '
        'own name. The setup therefore starts with it.\n\n'

        '## Why your own bot\n'
        '• Posts appear from <b>your bot\'s</b> name and photo, not from a shared bot.\n'
        '• No shared queue, so delivery does not wait behind other channels.\n'
        '• Statistics, leaderboards, backups and admin management live in that bot.\n'
        '• Inline buttons on posts work through your bot.\n\n'

        '## Do it\n'
        '1. <b>🤖 Bots</b> → <b>🔑 I Have a Token</b>, or <b>➕ Create bot</b> to be walked through '
        '@BotFather.\n'
        '2. Send the token as one message. The bot calls Telegram to verify it and shows the '
        'username.\n'
        '3. Tap the green <b>Open @your_bot</b> button. The channel and the time zone are connected '
        'inside that bot.\n\n'

        '## Next\n'
        '[[gs_step2|Step 2: Connect the Channel and Set the Time Zone]].'
    ),
    'children': None,
}

CONTENT_EN['gs_step2'] = {
    'title': 'Step 2: Connect the Channel and Set the Time Zone',
    'description': (
        'Inside the sender bot: add it to the channel from the green button, let the automatic check '
        'run, then set the zone for that channel.'
    ),
    'content': (
        'Open the sender bot. Because it has no channel yet it shows the "I\'m live" screen, not a '
        'dashboard.\n\n'

        '## Add it to the channel\n'
        '• Green <b>➕ Add bot to a channel</b> — Telegram\'s picker opens with the bot pre-selected '
        'as an administrator and <b>Post Messages</b> ticked.\n'
        '• Or forward a post from the channel, or send its <code>@username</code> / '
        '<code>t.me</code> link.\n'
        '• Private channel: add the bot as an administrator from the channel\'s own settings; it '
        'detects that on its own.\n\n'

        '## The automatic check\n'
        'After the button, the bot re-checks once after <b>10 seconds</b> and continues by itself. '
        'The automatic check is capped at <b>5 per day</b>; after that use <b>🔄 Check Again</b>, '
        'which is unlimited.\n\n'

        '## The time zone\n'
        'A city, your current time, a shared location or the list. It is stored for this channel '
        'only; other channels keep their own zone and the account default is written only if it is '
        'still empty.\n\n'

        '## Next\n'
        '[[gs_step3|Step 3: Schedule a Message]].'
    ),
    'children': None,
}

# ================================================== SURGICAL CORRECTIONS ==
# Applied as exact substring replacements; a miss is reported, not ignored.

REPLACE_EN = {
    'channel_connect': [
        (
            'Two bots may need rights, and they are checked separately.\n\n'
            '## @FastSchedulerBot\n'
            'Needs to be an administrator with <b>Post Messages</b> to verify and manage the channel. '
            'Add it in channel settings → Administrators → Add Administrator.\n\n'
            '## Your sender bot\n',
            'Only one bot does the work: <b>your sender bot</b>.\n\n'
            '## Your sender bot (required)\n'
        ),
    ],
    'channel_add': [
        (
            '## Before you start\n'
            'You must be an administrator of the channel, and @FastSchedulerBot must be an '
            'administrator there with <b>Post Messages</b>.',
            '## Before you start\n'
            'You must be an administrator of the channel, and the <b>sender bot</b> that will serve '
            'it must be an administrator there with <b>Post Messages</b>. The main bot does not need '
            'any rights in the channel.'
        ),
        (
            '## Connect it\n'
            '1. Open <b>📢 Channels</b> → <b>📢 Connect Channel</b>. You can also use '
            '<b>➕ Add New Channel</b> inside a scheduling channel picker.',
            '## Connect it\n'
            '1. Open <b>📢 Channels</b> → <b>📢 Connect Channel</b>. The bot lists your idle sender '
            'bots — pick one and it opens with the connect flow already running. You can also use '
            '<b>➕ Add New Channel</b> inside a scheduling channel picker.'
        ),
        (
            '## After connecting\n'
            'The channel has no sender bot yet. Add one from <b>🤖 Bots</b> → '
            '<b>🔑 I Have a Token</b> (or create one via @BotFather) and promote it in the channel. '
            'Until then scheduling remains locked.',
            '## After connecting\n'
            'If you picked a sender bot, the channel is linked to it and the time zone is the last '
            'step. If you connected the channel without a bot (the escape hatch), scheduling stays '
            'locked until you attach one — every channel needs its own sender bot.'
        ),
        (
            '• <b>Bot is not an admin</b> — promote @FastSchedulerBot.',
            '• <b>Bot is not an admin</b> — tap the green <b>➕ Add bot to a channel</b> button inside '
            'the sender bot, or promote it by hand with <b>Post Messages</b>.'
        ),
    ],
    'tutorial_walkthrough': [
        (
            'It runs once, after <code>/start</code>, and has three steps in a fixed order: channel → '
            'time zone → sender bot. The order matters — you cannot set a channel\'s time zone before '
            'the channel exists, and you cannot connect a sender bot before there is a channel to '
            'attach it to.',
            'It runs once, after <code>/start</code>, and has two screens in the main bot: <b>connect '
            'your sender bot</b>, then <b>open it</b>. The channel and the time zone are set inside '
            'the sender bot, in one short flow — the main bot never has to be a channel '
            'administrator.'
        ),
        (
            '• You are an <b>administrator</b> of the channel (not just its owner in name — Telegram '
            'must list you as an admin).',
            '• You are an <b>administrator</b> of the channel (not just its owner in name — Telegram '
            'must list you as an admin). You do not need to add @FastSchedulerBot anywhere.'
        ),
    ],
    'connect_bot': [
        (
            '## Attach the channel\n'
            'Choose the channel this bot serves. One bot = one channel.',
            '## Attach the channel\n'
            'One bot = one channel. Easiest: open the sender bot and tap the green <b>➕ Add bot to a '
            'channel</b> button — Telegram\'s picker pre-selects administrator rights. The bot '
            're-checks on its own after 10 seconds (5 automatic checks per day).'
        ),
        (
            '## Promote the bot\n'
            'Channel → Administrators → Add Administrator → your bot → <b>Post Messages</b>. Return to '
            'the bot and press <b>🔄 Check Again</b> if it is waiting for verification.',
            '## If it is still not an administrator\n'
            'Channel → Administrators → Add Administrator → your bot → <b>Post Messages</b>. Return to '
            'the bot and press <b>🔄 Check Again</b>. The main bot does not need to be added.'
        ),
    ],
    'channel_permissions': [
        (
            'Fast Scheduler only needs ordinary administrator rights; it never asks for your Telegram '
            'password or a login code.',
            'Only your <b>sender bot</b> needs ordinary administrator rights in the channel; the main '
            'bot needs none. Fast Scheduler never asks for your Telegram password or a login code.'
        ),
    ],
}

STALE_CLAIMS = [
    '@FastSchedulerBot must be an administrator',
    'Add @FastSchedulerBot as an administrator',
]
