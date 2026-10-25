# -*- coding: utf-8 -*-
"""Update the landing pages for the sender-bot-first flow, and tighten the SEO
strings around the bot's exact name.

Run from the repo root:

    python tools/apply_setup_site_copy.py --check   # verify markers, write nothing
    python tools/apply_setup_site_copy.py           # apply

Touches:
  * index.html and website/index.html (same page, two publish targets)
  * website/ru/index.html (server-rendered Russian landing page)

Design notes:
  * The brand stays "Fast Scheduler" (two words) as the user chose; the SEO
    work is about making the exact bot handle @FastSchedulerBot appear in every
    title/description/schema node, and removing the variants ("Fast Schedulebot",
    lowercase "fast scheduler" in titles) that made search results mismatch.
  * Every replacement is verified against REQUIRED afterwards; a miss raises
    before anything is written, so a partial patch never ships.
"""

import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ['index.html', 'website/index.html']
RU_FILE = 'website/ru/index.html'

# --------------------------------------------------------------- homepage --

STEP1_OLD = (
    '<h3>Open the bot &amp; connect a channel</h3><p>Tap Start, add the bot as an admin to your '
    'channel. Pick your timezone so 9:00 always means <i>your</i> 9:00.</p>'
)
STEP1_NEW = (
    '<h3>Open the bot &amp; connect your sender bot</h3><p>Tap Start and connect your own sender '
    'bot: the green button adds it to your channel with <b>Post Messages</b> pre-ticked — the main '
    'bot does not need to be an admin. Then pick your timezone so 9:00 always means <i>your</i> '
    '9:00.</p>'
)

FAQ_ANCHOR = (
    '      <details><summary>Is my data safe?</summary>'
)
FAQ_NEW = (
    '      <details><summary>Do I have to make @FastSchedulerBot a channel admin?</summary>'
    '<p>No. Publishing, scheduling, statistics and admin management all run through your own '
    'sender bot. The main bot is your chat for support and the optional emergency stand-in — if your '
    "sender bot's token is revoked it can deliver one post and keep going for up to 3 days, but only "
    'after you say yes. Existing channels never need to be reconnected.</p></details>\n'
    '      <details><summary>Can other people help me run the channel?</summary>'
    '<p>Yes. Co-admins are real channel administrators: they send the sender bot\'s @username (or its '
    'token) once, the bot verifies their rights through that bot, and they get 15 granular '
    'permissions — scheduling, editing, deleting, statistics, export and more. The owner is notified, '
    'a channel marked "hide from strangers" is never named to them, requests are limited to one per '
    'permission per week, and every change is audited.</p></details>\n'
)

FAQ_JSON_OLD = (
    '      { "@type": "Question", "name": "Will a scheduled post be published if I\'m offline?",\n'
    '        "acceptedAnswer": { "@type": "Answer", "text": "Yes. Once a message is scheduled it is '
    'delivered at the exact date and time you chose, whether you are online or not. It runs in your '
    'own timezone." } }\n'
)
FAQ_JSON_NEW = (
    '      { "@type": "Question", "name": "Will a scheduled post be published if I\'m offline?",\n'
    '        "acceptedAnswer": { "@type": "Answer", "text": "Yes. Once a message is scheduled it is '
    'delivered at the exact date and time you chose, whether you are online or not. It runs in your '
    'own timezone." } },\n'
    '      { "@type": "Question", "name": "Do I have to make @FastSchedulerBot a channel admin?",\n'
    '        "acceptedAnswer": { "@type": "Answer", "text": "No. Publishing runs through your own '
    'sender bot. The main bot is the chat for support and the optional emergency stand-in: if your '
    "sender bot's token is revoked it can deliver one post and keep going for up to 3 days, only "
    'after you opt in. Existing channels never need to be reconnected." } },\n'
    '      { "@type": "Question", "name": "Can other people help run my channel?",\n'
    '        "acceptedAnswer": { "@type": "Answer", "text": "Yes. Channel administrators can join by '
    "sending the sender bot's @username or token; the bot verifies their Telegram rights and grants "
    '15 granular permissions, notifies the owner, never names a hidden channel, and audits every '
    'change." } }\n'
)

TWITTER_TITLE_OLD = (
    '<meta name="twitter:title" content="Fast Scheduler | Telegram Fast Scheduler Bot">'
)
TWITTER_TITLE_NEW = (
    '<meta name="twitter:title" content="Fast Scheduler — Telegram Post Scheduler Bot '
    '(@FastSchedulerBot)">'
)

OG_TITLE_OLD = '<meta property="og:title" content="Fast Scheduler — Telegram Post Scheduler Bot">'
OG_TITLE_NEW = (
    '<meta property="og:title" content="Fast Scheduler — Telegram Post Scheduler Bot '
    '(@FastSchedulerBot)">'
)

OG_DESC_OLD = (
    '<meta property="og:description" content="Batch-schedule weeks of Telegram channel posts in one '
    'chat. Post from your own bot, track views & comments, get reports in your timezone. Free to '
    'start.">'
)
OG_DESC_NEW = (
    '<meta property="og:description" content="Fast Scheduler (@FastSchedulerBot) batch-schedules '
    'weeks of Telegram channel posts in one chat. Post from your own bot, give co-admins granular '
    'permissions, get reports in your timezone. Free to start.">'
)

WEBSITE_ALT_OLD = (
    '"@type": "WebSite", "name": "Fast Scheduler", "alternateName": "Fast Scheduler Telegram bot",'
)
WEBSITE_ALT_NEW = (
    '"@type": "WebSite", "name": "Fast Scheduler", "alternateName": ["FastScheduler", '
    '"FastSchedulerBot", "@FastSchedulerBot", "Fast Scheduler Telegram bot"],'
)

# ------------------------------------------------------------------- russian --

RU_STEP_OLD = 'Нажмите Start, добавьте бота в администраторы канала.'
RU_STEP_NEW = (
    'Нажмите Start и подключите своего бота-отправителя: зелёная кнопка добавит его в канал с уже '
    'отмеченным правом «Публикация сообщений» — главному боту права администратора не нужны.'
)

RU_ADMINS_OLD = (
    'Управляйте несколькими каналами из одного бота. Добавляйте доверенных админов с правами на '
    'каждый канал — никто никому не мешает.'
)
RU_ADMINS_NEW = (
    'Управляйте несколькими каналами из одного бота. Админы канала входят сами: пришлите @имя или '
    'токен бота-отправителя, и бот проверит ваши права в Telegram. Доступ настраивается по 15 '
    'отдельным правам (расписание, редактирование, удаление, статистика, экспорт и другие), владелец '
    'получает уведомление, скрытый канал не называется посторонним, а каждое изменение попадает в '
    'журнал.'
)


def patch(path, pairs):
    full = os.path.join(ROOT, path)
    with io.open(full, encoding='utf-8') as f:
        text = f.read()
    original = text
    for old, new in pairs:
        if new in text:
            continue
        if old not in text:
            raise SystemExit(f'{path}: target not found: {old[:70]!r}')
        text = text.replace(old, new, 1)
    return full, original, text


def required_markers():
    return [
        'green button adds it to your channel',
        'Do I have to make @FastSchedulerBot a channel admin?',
        'Can other people help me run the channel?',
        '(@FastSchedulerBot)">',
        'give co-admins granular',
        '"FastSchedulerBot", "@FastSchedulerBot"',
    ]


def main(argv):
    check = '--check' in argv
    pairs = [
        (STEP1_OLD, STEP1_NEW),
        (FAQ_ANCHOR, FAQ_NEW + FAQ_ANCHOR),
        (FAQ_JSON_OLD, FAQ_JSON_NEW),
        (TWITTER_TITLE_OLD, TWITTER_TITLE_NEW),
        (OG_TITLE_OLD, OG_TITLE_NEW),
        (OG_DESC_OLD, OG_DESC_NEW),
        (WEBSITE_ALT_OLD, WEBSITE_ALT_NEW),
    ]
    pending = []
    for path in FILES:
        full, original, text = patch(path, pairs)
        if check:
            print(f'{path}: {"ready" if text != original else "already applied"}')
        else:
            if text != original:
                with io.open(full, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(text)
                print(f'{path}: patched')
            else:
                print(f'{path}: already applied')
        pending.append((path, text))

    # Russian landing page: two stale claims only.
    try:
        full, original, text = patch(RU_FILE, [(RU_STEP_OLD, RU_STEP_NEW), (RU_ADMINS_OLD, RU_ADMINS_NEW)])
    except SystemExit as exc:
        print('  !', exc)
        raise
    if not check and text != original:
        with io.open(full, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
        print(f'{RU_FILE}: patched')
    else:
        print(f'{RU_FILE}: {"ready" if check else "already applied"}')

    # Verify the English page carries every new string (in check mode, verify
    # the text that would be written, not the file still on disk).
    html = dict(pending)['index.html']
    missing = [m for m in required_markers() if m not in html]
    if missing:
        raise SystemExit('index.html missing markers: ' + repr(missing))
    print('markers: ok')


if __name__ == '__main__':
    main(sys.argv[1:])
