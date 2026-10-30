"""Generate website/help.html — a professional web Help Center for Fast Scheduler.

Source of truth: the ``help`` section of translations/en.json (the same tree
the support bot serves). Run from the repo root:

    python website/_build/build_help.py

Design:
  * Real help-center information architecture — home (category grid) ->
    category (topic list) -> article pages, hash-routed as a static SPA.
  * Every article is rendered statically in the HTML (crawlable, works
    without JS via <noscript>); the router only toggles visibility.
  * Client-side scored search (substring + word-prefix, ranked) with a
    results dropdown, keyboard navigation and "/" shortcut.
  * Breadcrumbs, prev/next pager, FAQ accordions, related-topic chips,
    "ask in the bot" CTA.
  * Full light/dark theme support (no-flash inline script + toggle).
  * Stroke SVG icons everywhere — no emoji.
  * SEO: title/description, OpenGraph, JSON-LD breadcrumb.
"""
import json
import os
import re
import sys
import html as html_mod
import datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TRANSLATIONS = os.path.join(REPO_ROOT, 'translations', 'en.json')
OUT_PATH = os.path.join(REPO_ROOT, 'website', 'help.html')

# Fill {plan_limit} placeholders in help texts from the single source of truth
# (src/core/plans.py) so the website and the bot always agree.
sys.path.insert(0, REPO_ROOT)
try:
    from src.core.plans import get_help_kwargs as _plan_kwargs
except Exception:  # pragma: no cover - build still works without values
    _plan_kwargs = lambda: {}

BOT_URL = 'https://t.me/FastSchedulerSupport_bot?start=_t'
SUPPORT_URL = 'https://t.me/FastSchedulerSupport_bot'
CSS_VER = '20260924a'

# ---------------------------------------------------------------- icons ----
ICONS = {
    # ui icons
    'close': '<path d="M6 6l12 12M18 6L6 18"/>',
    # category icons
    'compass':   '<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>',
    'calendar':  '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    'megaphone': '<path d="m3 11 18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/>',
    'bot':       '<rect x="4" y="8" width="16" height="12" rx="2"/><path d="M12 8V4"/><circle cx="12" cy="3" r="1"/><line x1="9" y1="13" x2="9" y2="15"/><line x1="15" y1="13" x2="15" y2="15"/>',
    'shield':    '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    'crown':     '<path d="m2 4 3 12h14l3-12-6 7-4-7-4 7-6-7z"/><path d="M5 20h14"/>',
    'gift':      '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13"/><path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7"/><path d="M7.5 8a2.5 2.5 0 0 1 0-5C11 3 12 8 12 8s1-5 4.5-5a2.5 2.5 0 0 1 0 5"/>',
    'gauge':     '<path d="M12 15l3.5-3.5"/><path d="M20.3 18a10 10 0 1 0-16.6 0"/>',
    'globe':     '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    'languages': '<path d="M5 8l6 6"/><path d="m4 14 6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="m22 22-5-10-5 10"/><path d="M14 18h6"/>',
    'export':    '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>',
    'import':    '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/>',
    'cloud-down':'<path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"/><path d="m8 17 4 4 4-4"/><line x1="12" y1="12" x2="12" y2="21"/>',
    'image':     '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/>',
    'wrench':    '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    'bulb':      '<path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.4 1 2.3h6c0-.9.4-1.8 1-2.3A7 7 0 0 0 12 2z"/>',
    'message':   '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    'help':      '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    'terminal':  '<polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/>',
    'alert':     '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    'lock':      '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    'scale':     '<path d="M12 3v18"/><path d="m5 7 7-4 7 4"/><path d="M3 13l2-6 2 6a3 3 0 0 1-4 0z"/><path d="m17 13 2-6 2 6a3 3 0 0 1-4 0z"/><path d="M8 21h8"/>',
    'mail':      '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/>',
    'buoy':      '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><line x1="4.93" y1="4.93" x2="9.17" y2="9.17"/><line x1="14.83" y1="14.83" x2="19.07" y2="19.07"/><line x1="14.83" y1="9.17" x2="19.07" y2="4.93"/><line x1="4.93" y1="19.07" x2="9.17" y2="14.83"/>',
    'settings':  '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
    'book':      '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    # ui icons
    'menu':      '<line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>',
    'search':    '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    'chev':      '<polyline points="9 18 15 12 9 6"/>',
    'arrow-r':   '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
    'arrow-l':   '<line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>',
    'home':      '<path d="M3 11l9-8 9 8M5 10v10h14V10"/>',
    'sun':       '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>',
    'moon':      '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>',
    'send':      '<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>',
    'zap':       '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    'sparkles':  '<path d="M12 3l1.9 5.8a2 2 0 0 0 1.3 1.3L21 12l-5.8 1.9a2 2 0 0 0-1.3 1.3L12 21l-1.9-5.8a2 2 0 0 0-1.3-1.3L3 12l5.8-1.9a2 2 0 0 0 1.3-1.3z"/>',
    'keys':      '<rect x="2" y="6" width="20" height="12" rx="2.5"/><path d="M6.5 10h.01M10.5 10h.01M14.5 10h.01M18 10h.01M8 13.5h8"/>',
    'expand':    '<path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M16 3h3a2 2 0 0 1 2 2v3"/><path d="M8 21H5a2 2 0 0 1-2-2v-3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/>',
    'thumb-up':  '<path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z"/>',
    'thumb-dn':  '<path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22a3.13 3.13 0 0 1-3-3.88Z"/>',
    'gear':      '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33h0a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51h0a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v0a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
}


CAT_ICONS = {
    'start': 'compass', 'scheduling': 'calendar', 'channels': 'megaphone', 'bots': 'bot',
    'admins': 'shield', 'premium': 'crown', 'referral': 'gift', 'limits': 'gauge',
    'timezone': 'globe', 'language': 'languages', 'export': 'export', 'import': 'import',
    'backup': 'cloud-down', 'media_storage': 'image', 'tools': 'wrench', 'tips': 'bulb',
    'feedback': 'message', 'faq': 'help', 'commands': 'terminal', 'errors': 'alert',
    'privacy': 'lock', 'legal': 'scale', 'contact': 'mail', 'help': 'buoy', 'config': 'settings',
}
DEFAULT_ICON = 'book'

# One-line card descriptions for the "Browse by topic" grid (icon + title +
# what lives inside, Wise-style). Russian twins live in RU_EXT2 inside
# tools/build_ru_pages3.py — keep the keys in sync.
CAT_DESC = {
    'start': 'Connect a channel and send your first post',
    'scheduling': 'One-time and recurring posts',
    'channels': 'Connect and manage channels',
    'bots': 'Use your own sender bot',
    'admins': 'Team access and shared limits',
    'premium': 'Plans, Stars and payments',
    'referral': 'Invite owners, earn Premium days',
    'limits': 'Free and Premium quotas',
    'timezone': 'Post at the right hour',
    'language': 'Interface languages',
    'export': 'Take your data with you',
    'import': 'Bring chats and files in',
    'backup': 'Backups, restore and safety',
    'media_storage': 'Store photos, video and files',
    'tools': 'Search, stats and calendar',
    'tips': 'Pro workflows that save hours',
    'feedback': 'Report bugs, request features',
    'faq': 'Short answers, fast',
    'commands': 'Bot commands cheat sheet',
    'errors': 'Fix what went wrong',
    'privacy': 'Your data and safety',
    'legal': 'Terms, privacy and refunds',
    'contact': 'Talk to a human',
    'help': 'About this help center',
    'config': 'Signatures and fine-tuning',
    'misc': 'Everything else',
}
DEFAULT_DESC = 'Guides and answers'

QUICK_LINK_IDS = ['channel_add', 'bot_add', 'premium_buy', 'payment_stars', 'backup_create', 'referral_how']

# "Try asking" chips on the hero - natural questions the mini-AI search
# answers well. Every question must hit a real article.
TRY_ASKING = [
    "What's the difference between .fsback and .fspback?",
    'Why are my scheduled posts not publishing?',
    'How do I connect my own sender bot?',
    'How do I repeat a post every week?',
    'What are the free plan limits?',
    'How do I get a refund?',
]

# ---------------------------------------------------- web-only help model --
# The web Help Center shows a curated view of the bot's help tree: short
# in-bot notes are unified into longer articles and bot-UI-only nodes are
# folded into their parent guides. The bot itself keeps its full tree.
WEB_DROPS = {
    # Only pages that are genuinely not user-facing articles are dropped:
    # meta pages, infrastructure notes and two-line stubs. Every real help
    # topic keeps its own page now, because the articles are full guides and
    # cross-links must resolve to a real file on the static mirror.
    'website_help', 'website_premium', 'help_about',      # meta pages
    'website_tour',                                       # meta page
    'bot_webhook', 'payment_webhook',                     # infra details
    'bot_isolated', 'security_isolation',                 # architecture notes
    'legal_cookie',                                       # 2-line stub
    'support_hours', 'support_priority',                  # folded into Response Time
    'mt_storage', 'ts_storage',                           # 2-line stubs
}
WEB_MERGE_CHILDREN = {}

WEB_LINK_FIX = {
    'schedule_text': 'scheduling', 'schedule_review': 'scheduling', 'schedule_one_time': 'scheduling',
    'schedule_edit': 'edit', 'schedule_delete': 'delete',
    'language_sync': 'language_change',
    'schedule_location': 'schedule_advanced', 'schedule_poll_quiz': 'schedule_poll',
    'schedule_sticker': 'schedule_media', 'schedule_voice': 'schedule_media',
    'schedule_animation': 'schedule_media', 'schedule_album': 'schedule_media',
    'schedule_caption': 'schedule_media', 'schedule_video': 'schedule_media',
    'schedule_document': 'schedule_media',
    'gs_step1': 'getting_started', 'gs_step2': 'getting_started', 'gs_step3': 'getting_started',
    'onboarding_step1': 'getting_started', 'onboarding_step2': 'getting_started',
    'timezone_auto': 'timezone_set', 'timezone_detect': 'timezone_set', 'timezone_examples': 'timezone_list',
    'language_help': 'language_change',
    'ms_search': 'ms_manage', 'ms_from_storage_help': 'ms_save',
    'website_help': 'help', 'website_premium': 'premium_buy', 'help_about': 'help',
    'commands_help': 'commands_list',
    'premium_freezing': 'premium_freeze',
}
# Fuller answers shown on the web where the in-bot FAQ answer is a stub.
WEB_FAQ_ANSWER = {
    'legal_data': {0: (
        "The bot stores only what it needs to run your scheduling: your Telegram user ID, the IDs of "
        "channels you connect, the messages you schedule, and your settings (language, time zone, "
        "signatures, bot tokens). Nothing else is collected, nothing is sold or shared, and media is "
        "kept as Telegram file references — not re-uploaded copies.")},
    'onboarding_step2': {0: (
        "Every post is delivered by your channel's <b>sender bot</b> — the bot you paired with the "
        "channel in step 2. The main bot coordinates the schedule; your sender bot publishes under "
        "your brand.")},
    'premium': {5: (
        "Add a <b>signature</b> once and every post in that channel carries it: send "
        "<code>/signature</code> (or tap <b>📝 Signature</b> on the review screen), pick the channel, and send the text. Manage or remove it any "
        "time from the same menu.")},
    'premium_troubleshooting': {0: (
        "Payment taken but no Premium? Restart the bot with <code>/start</code> — activation is "
        "checked on launch. Still nothing? Open <b>Feedback</b> with your payment date and method; "
        "a human sorts it the same day.")},
}


def apply_web_model(help_sec):
    """Curate the bot's help tree for the web edition."""
    # Legal & Terms stay in the Help Center: the articles explain how the bot
    # handles data and are cross-linked from privacy/troubleshooting pages. The
    # dedicated website/legal/* pages remain the formal documents in the footer.
    for k in WEB_DROPS:
        help_sec.pop(k, None)
    for parent, kids in WEB_MERGE_CHILDREN.items():
        node = help_sec.get(parent)
        if isinstance(node, dict):
            node['children'] = [k for k in kids if k in help_sec]
    for node in help_sec.values():
        if not isinstance(node, dict):
            continue
        for f in node.get('faq') or []:
            links = f.get('links')
            if isinstance(links, str):
                links = [x.strip() for x in links.split(',') if x.strip()]
            if isinstance(links, list):
                out = []
                for l in links:
                    t = WEB_LINK_FIX.get(l, l)
                    if t and t in help_sec and t not in out:
                        out.append(t)
                f['links'] = out
    for tid, patches in WEB_FAQ_ANSWER.items():
        node = help_sec.get(tid)
        if isinstance(node, dict) and node.get('faq'):
            for idx, answer in patches.items():
                if idx < len(node['faq']):
                    node['faq'][idx]['a'] = answer


def svg(name, cls=''):
    cls_attr = f' class="{cls}"' if cls else ''
    return (f'<svg{cls_attr} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{ICONS[name]}</svg>')


# Chrome strings come from translations/website/<lang>.json so the navbar,
# settings menu and footer are written once and read in every language. The
# old per-language Python dicts are gone: a missing Russian key now falls back
# to English instead of raising KeyError mid-build.
import site_i18n as _i18n

RU_CHROME = _i18n.chrome('ru')
_CHROME_EN = _i18n.chrome('en')


def tr(key, lang='en'):
    """Chrome string in the page language (EN default, byte-identical)."""
    table = RU_CHROME if lang == 'ru' else _CHROME_EN
    return table.get(key) or _CHROME_EN.get(key, '')


def settings_menu(support_url, lang='en', reading=False):
    """Settings-gear dropdown in the page language (blog adds reading rows)."""
    t = lambda k: tr(k, lang)  # noqa: E731
    fonts = (f'<div class="gp-row gp-fonts" data-fonts role="group" aria-label="{t("font_size")}">{svg("book")}<span>{t("font_size")}</span>'
             f'<span class="hc-fonts"><button type="button" data-font="s" aria-label="{t("font_s")}">A</button>'
             f'<button type="button" data-font="m" aria-label="{t("font_m")}">A</button>'
             f'<button type="button" data-font="l" aria-label="{t("font_l")}">A</button></span></div>')
    read = ''
    if reading:
        read = (f'<div class="gp-sep gp-reading" data-blog-reading></div>\n'
                f'          <div class="gp-head gp-reading" data-blog-reading>{t("reading")}</div>\n'
                f'          <button type="button" class="gp-row gp-reading" data-blog-reading aria-pressed="false" data-blog-wide>{svg("expand")}<span>{t("wide")}</span><span class="io-switch" aria-hidden="true"></span></button>\n'
                f'          <button type="button" class="gp-row gp-reading" data-blog-reading aria-pressed="true" data-blog-rail>{svg("book")}<span>{t("rail")}</span><span class="io-switch" aria-hidden="true"></span></button>\n'
                f'          <button type="button" class="gp-row gp-reading" data-blog-reading aria-pressed="false" data-blog-fs>{svg("expand")}<span>{t("fullscreen")}</span><span class="io-switch" aria-hidden="true"></span></button>\n'
                f'          {fonts}')
    return (f'<div class="gp-head" role="none">{t("settings")}</div>\n'
            f'        <button type="button" class="gp-row" aria-pressed="false" id="rowDark">{svg("moon")}<span>{t("dark")}</span><span class="io-switch" aria-hidden="true"></span></button>\n'
            f'        <button type="button" class="gp-row" aria-pressed="true" id="rowAnim">{svg("zap")}<span>{t("anim")}</span><span class="io-switch" aria-hidden="true"></span></button>\n'
            f'        <button type="button" class="gp-row" aria-pressed="true" id="rowFx">{svg("sparkles")}<span>{t("fx")}</span><span class="io-switch" aria-hidden="true"></span></button>\n'
            f'        <button type="button" class="gp-row" aria-pressed="true" id="rowKeys">{svg("keys")}<span>{t("keys")}</span><span class="io-switch" aria-hidden="true"></span></button>\n'
            f'        {fonts if not reading else ""}\n'
            f'        {read}\n'
            f'        <button type="button" class="gp-row gp-row-sub" id="rowKeysHelp"><svg viewBox="0 0 24 24" fill="none" stroke="none" aria-hidden="true" style="visibility:hidden;width:18px;height:18px"></svg><span class="gp-sub-label">{t("see_keys")}</span><svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9 18 15 12 9 6"/></svg></button>\n'
            f'        <div class="gp-sep" role="separator"></div>\n'
            f'        <a class="gp-row" href="{support_url}" target="_blank" rel="noopener noreferrer">{svg("send")}<span>{t("support")}</span>{svg("chev")}</a>')


def unified_nav(rel, bot_url, menu_inner, left_extra='', center_extra='',
                brand_extra='', cta_html=None, right_extra='', lang='en',
                with_search=True):
    """Single shared navbar for every non-main page (help, blog, legal, 404).

    Left group: brand logo. Right group: Blog and Help Center pills, then
    the single Open Bot CTA, then the settings gear (gear always trails the
    CTA so it stays reachable at the bar's right edge), then right_extra
    (help hub burger: dead last so it owns the bar's right edge on phones).
    center_extra holds
    page extras (help search, legal doc tabs); brand_extra appends to the
    brand (help "Help Center" suffix);
    cta_html overrides the default CTA (legal tooltip CTA). The Help
    quick-search popover (#siteMenu, owned by help-search.js) hangs off the
    Help Center pill. The main page (index) keeps its own navbar.
    """
    t = lambda k: tr(k, lang)  # noqa: E731
    R = rel + ('/ru' if lang == 'ru' else '')
    cta = cta_html or (f'<a class="btn btn-primary nav-cta" data-cta-short="{t("open_short")}" aria-label="{t("open_bot")}" href="{bot_url}" target="_blank" '
           f'rel="noopener noreferrer">{svg("send")}<span>{t("open_bot")}</span>'
           f'<kbd class="tab-kbd" aria-hidden="true">B</kbd></a>')
    gear = ('<span class="settings-wrap">'
            '<button type="button" class="icon-btn" id="settingsBtn" aria-haspopup="menu" '
            f'aria-expanded="false" aria-label="{t("settings")}" data-hk="settings dark anim fx keys">'
            f'{svg("gear")}</button>'
            f'<div class="glass-pop" id="settingsMenu" role="group" aria-label="{t("settings")}">'
            f'{menu_inner}</div></span>')
    brand = (f'<a class="brand" href="{R}/index.html" aria-label="{t("brand_home")} (FS)">'
             f'<span class="brand-mark"><img src="{rel}/brand-logo-128.png" alt="" '
             f'width="30" height="30" decoding="async"></span>'
             f'<span class="brand-full">Fast Scheduler</span>'
             f'<span class="brand-short">FS</span>{brand_extra}</a>')
    # Search lives only in the Help Center. Other pages render the Help pill
    # as a plain navigation link (with_search=False) instead of a search popover.
    pop = (f'<div class="glass-pop site-menu-pop help-menu nav-menu-pop" id="siteMenu" role="dialog" '
           f'aria-label="{t("pop_aria")}">'
           f'<form class="help-search" id="helpSearchForm" role="search">'
           f'{svg("search", "sic")}'
           f'<input type="search" id="helpSearchInput" placeholder="{t("search_ph")}" '
           f'autocomplete="off" aria-label="{t("search_aria")}">'
           f'</form>'
           f'<div class="help-recent">'
           f'<div class="help-recent-title" id="helpRecentTitle">{t("popular")}</div>'
           f'<div class="help-recent-list" id="helpRecentList"></div>'
           f'</div>'            f'<a class="gp-row help-menu-open" aria-label="{t("open_help")}" href="{R}/help.html">'
           f'{svg("book")}<span>{t("open_help")}</span>{svg("chev")}</a>'
           f'</div>')
    center = f'<div class="nav-center">{center_extra}</div>' if center_extra else ''
    return (f'<header class="site"><div class="wrap nav nav-unified">'
            f'<div class="nav-group nav-left">{brand}{left_extra}</div>'
            f'{center}'
            f'<div class="nav-group nav-right">'
            f'<a class="nav-link" href="{R}/blog/index.html" aria-label="{t("blog")}">{svg("megaphone")}<span>{t("blog")}</span></a>'
            f'<span class="site-menu-wrap">'
            f'<a class="nav-link site-menu-row" href="{R}/help.html" aria-label="{t("help_center")}" '
            f'aria-haspopup="menu" aria-expanded="false">{svg("book")}<span>{t("help_center")}</span></a>'
            f'{pop if with_search else ""}</span>'
            f'{cta}{gear}{right_extra}'
            f'</div></div></header>')


def esc(text):
    return html_mod.escape(str(text), quote=True)


TITLE_LIMIT = 62
DESC_LIMIT = 155

# --- Entity layer (GEO/AEO) -------------------------------------------------
# One canonical description of the product for search engines and answer
# engines. Google reads WebSite/Organization for site-name and logo signals;
# other engines use the aliases to resolve abbreviations and alternate names.
SITE_URL = 'https://fastscheduler.github.io'
ORG_ID = SITE_URL + '/#organization'
WEBSITE_ID = SITE_URL + '/#website'

# How the product is actually typed. The brand is two words, but the bot's
# handle, the domain and most search queries are one: "fastscheduler",
# "FastScheduler", "@FastSchedulerBot", and the older "FastSchedule Bot". Every
# generated page publishes this list as the entity's alternateName so a query in
# any of those spellings resolves to the same entity — a one-character mismatch
# ("fast schedular", "FastSchedule") used to drop the page out of the result.
BRAND_ALIASES = [
    'Fast Scheduler Bot', 'FastSchedulerBot', 'FastScheduler',
    'fastscheduler', 'fastschedulerbot', '@FastSchedulerBot',
    'FastSchedule', 'FastSchedule Bot',
    'Fast Scheduler Telegram bot', 'fast scheduler telegram bot',
    'TG Scheduler', 'Telegram Scheduler Bot', 'Telegram post scheduler',
    'TG Fast Scheduler', 'Fast Scheduler TG',
]

BRAND_DESCRIPTION = (
    'Fast Scheduler is a Telegram bot (@FastSchedulerBot) that batch-schedules, '
    'auto-publishes and tracks channel posts. It is unrelated to calendar, '
    'project-management or crew-scheduling products that share the name.'
)


def site_entity_ld():
    """Organization + WebSite JSON-LD shared by every page.

    Kept in one place so the homepage, help center, blog and legal pages all
    describe the same entity with the same @id, name, aliases and logo.
    """
    org = {
        '@context': 'https://schema.org',
        '@type': 'Organization',
        '@id': ORG_ID,
        'name': 'Fast Scheduler',
        'alternateName': BRAND_ALIASES,
        'url': SITE_URL + '/',
        'logo': {
            '@type': 'ImageObject', '@id': SITE_URL + '/#logo',
            'url': SITE_URL + '/icon-512.png',
            'contentUrl': SITE_URL + '/icon-512.png',
            'width': 512, 'height': 512, 'caption': 'Fast Scheduler',
        },
        'image': SITE_URL + '/icon-512.png',
        'description': BRAND_DESCRIPTION,
        'email': 'fastschedulebot@gmail.com',
        'sameAs': [
            'https://t.me/FastSchedulerBot',
            'https://t.me/FastSchedulerSupport_bot',
        ],
        'contactPoint': {
            '@type': 'ContactPoint', 'contactType': 'customer support',
            'email': 'fastschedulebot@gmail.com',
            'availableLanguage': ['English', 'Russian', 'Spanish'],
            'url': 'https://t.me/FastSchedulerSupport_bot',
        },
    }
    site = {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        '@id': WEBSITE_ID,
        'name': 'Fast Scheduler',
        'alternateName': BRAND_ALIASES,
        'url': SITE_URL + '/',
        'publisher': {'@id': ORG_ID},
        'inLanguage': ['en', 'ru', 'es'],
        'description': BRAND_DESCRIPTION,
        'hasPart': [
            {'@type': 'WebPage', 'name': 'Fast Scheduler Help Center',
             'url': SITE_URL + '/help.html'},
            {'@type': 'Blog', 'name': 'Fast Scheduler Blog',
             'url': SITE_URL + '/blog/'},
            {'@type': 'WebPage', 'name': 'Pricing and plans',
             'url': SITE_URL + '/#pricing'},
        ],
    }
    render = lambda o: ('<script type="application/ld+json">'
                        + json.dumps(o, ensure_ascii=False) + '</script>')
    return render(org) + chr(10) + render(site)


def _cut_words(s, n):
    """Trim to <= n chars on a word boundary, without dangling punctuation."""
    s = re.sub(r'\s+', ' ', s or '').strip()
    if len(s) <= n:
        return s
    cut = s[:n]
    sp = cut.rfind(' ')
    if sp >= n * 0.55:
        cut = cut[:sp]
    return cut.rstrip(' ,;:-\u2013\u2014&|/')


def fit_title(t):
    """Title that survives the SERP without Google rewriting it.

    Search results clip around 60 characters; longer titles get replaced by
    Google with text from the page, which is how an exact-phrase match gets
    thrown away. Keep the brand suffix, spend the budget on the subject.
    """
    t = re.sub(r'\s+', ' ', t or '').strip()
    if len(t) <= TITLE_LIMIT:
        return t
    for sep in (' \u2014 ', ' | ', ' - ', ': '):
        i = t.rfind(sep)
        if i >= 18:
            tail = t[i:]
            budget = TITLE_LIMIT - len(tail)
            if budget >= 18:
                return _cut_words(t[:i], budget) + tail
    return _cut_words(t, TITLE_LIMIT)


def smart_desc(text, floor=70, limit=DESC_LIMIT):
    """Whole-sentence meta description.

    The old build sliced raw article text at exactly 160 characters, so
    descriptions ended mid-word ("...The basic flow 1. Tap S"). Prefer the
    last full sentence that fits; fall back to a clean word-boundary cut.
    """
    t = re.sub(r'\s+', ' ', (text or '').replace('\u2014', '-').replace('&mdash;', '-')).strip()
    if not t:
        return ''
    if len(t) <= limit:
        return t
    best = ''
    for m in re.finditer(r'[.!?](?=\s|$)', t):
        end = m.end()
        if floor <= end <= limit:
            best = t[:end]
        elif end > limit:
            break
    if best and len(best) < floor:
        # Still thin. Keep appending whole sentences (FAQ ledes are often two
        # short sentences) until the snippet has some weight in the SERP.
        for m in re.finditer(r'[.!?](?=\s|$)', t[len(best):]):
            if len(best) + m.end() <= limit:
                best = t[:len(best) + m.end()]
            else:
                break
    return best or _cut_words(t, limit)


def esc_q(text):
    """Escape FAQ question text, but keep <code> tags real so they
    render as styled inline code instead of leaking as literal text."""
    out = esc(text)
    out = re.sub(r'&lt;(/?)code&gt;', r'<\1code>', out)
    # safety net: any other tag still leaks -> drop it entirely
    return re.sub(r'&lt;/?[a-zA-Z][^&]*?&gt;', '', out)


# ------------------------------------------------------------- data model --
def load_help_tree():
    with open(TRANSLATIONS, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    help_sec = data.get('help', {})
    inject_comparison_table(help_sec)
    return help_sec, data


def _filled_comparison_markdown():
    """The bot's premium_comparison_rich table with real plan values.

    Same inputs as the bot (_comparison_filled in build_site.py): plan-limit
    kwargs + monthly/yearly labels + savings + report counts.
    """
    try:
        from src.core.plans import get_comparison_kwargs
        from src.core.config import PREMIUM_PRICE_MONTHLY_CENTS, PREMIUM_PRICE_YEARLY_CENTS
    except Exception:
        return ''
    try:
        with open(TRANSLATIONS, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        rich = data.get('premium_comparison_rich') or (data.get('premium', {}) or {}).get('comparison_rich', '')
        monthly = PREMIUM_PRICE_MONTHLY_CENTS / 100
        yearly = PREMIUM_PRICE_YEARLY_CENTS / 100
        saved = monthly * 12 - yearly
        months_free = int(round(saved / monthly)) if monthly else 0
        percent = round(saved / (monthly * 12) * 100) if monthly else 0
        kwargs = get_comparison_kwargs(dash_empty=True)
        _support_bot = os.getenv('SUPPORT_BOT_USERNAME', 'FastSchedulerSupport_bot').lstrip('@')
        _support_url = f'https://t.me/{_support_bot}?start=help_premium'
        kwargs.update(
            monthly_label=f"${monthly:.2f}/month",
            yearly_label=f"${yearly:.2f}/year",
            yearly_savings=f"{months_free} MONTHS FREE - Save {percent}%" if saved > 0 else "",
            reports_free=kwargs['limit_report_schedules_free'],
            reports_prem=kwargs['limit_report_schedules_prem'],
            support_url=_support_url,
        )
        return rich.format(**kwargs)
    except Exception:
        return ''


def _md_table_to_html(md):
    """Render one markdown table (| cells |) to HTML. Returns '' if none."""
    rows = [ln.strip() for ln in (md or '').splitlines() if ln.strip().startswith('|')]
    if len(rows) < 3:
        return ''

    def cells(ln):
        return [c.strip() for c in ln.strip().strip('|').split('|')]

    head = cells(rows[0])
    out = ['<div class="table-scroll"><table><thead><tr>'
           + ''.join('<th>%s</th>' % html_mod.escape(c) for c in head)
           + '</tr></thead><tbody>']
    for ln in rows[2:]:
        cc = cells(ln)
        tds = []
        for i, c in enumerate(cc):
            style = '' if i == 0 else ' style="text-align: center;"'
            tds.append('<td%s>%s</td>' % (style, html_mod.escape(c)))
        out.append('<tr>' + ''.join(tds) + '</tr>')
    out.append('</tbody></table></div>')
    return '\n'.join(out)


def inject_comparison_table(help_sec):
    """Append the full plan-comparison table (real data) to the Compare Plans
    article. The translation only carries a prose summary; the website article
    must show the same full table the Premium menu shows in the bot."""
    node = help_sec.get('premium_compare')
    if not isinstance(node, dict):
        return
    table_html = _md_table_to_html(_filled_comparison_markdown())
    if not table_html or '<table' in (node.get('content') or ''):
        return
    base = node.get('content', '') or ''
    node['content'] = (text_to_html(base) + '\n' + table_html) if base else table_html
    node['_raw_html'] = True


def strip_storage(text):
    """Drop @@STORAGE@@-prefixed content markers (kept only for the bot)."""
    if not isinstance(text, str):
        return text
    return re.sub(r'@@STORAGE@@', '', text)


def fill_placeholders(text):
    """Fill {plan_limit} placeholders with real values from src/core/plans.py.

    Unknown placeholders are left as-is; a stray single '{' or '}' (which the
    bot's format step tolerates) must not crash the build."""
    if not isinstance(text, str) or '{' not in text:
        return text
    known = _plan_kwargs()
    try:
        return text.format(**known)
    except (KeyError, IndexError, ValueError):
        # Fill known keys one by one so a single unknown placeholder cannot
        # blank out every other value in the same text.
        out = text
        for k, v in known.items():
            out = out.replace('{' + k + '}', str(v))
        return out


def _faq_of(node):
    faq = []
    for f in node.get('faq') or []:
        if isinstance(f, dict) and (f.get('q') or f.get('a')):
            links = f.get('links', '') or []
            if isinstance(links, str):
                links = [c.strip() for c in links.split(',') if c.strip()]
            fixed = []
            for l in links:
                t = WEB_LINK_FIX.get(l, l)
                if t and t not in fixed:
                    fixed.append(t)
            faq.append({
                'q': fill_placeholders(strip_storage(f.get('q', ''))),
                'a': fill_placeholders(strip_storage(f.get('a', ''))),
                'links': fixed,
            })
    return faq


def node_from_sec(help_sec, tid):
    node = help_sec.get(tid) if isinstance(help_sec.get(tid), dict) else {}
    content = node.get('content', '')
    if not isinstance(content, str):
        content = ''
    return {
        'id': tid,
        'title': fill_placeholders(strip_storage(node.get('title', '')).strip()),
        'content': fill_placeholders(strip_storage(content).strip()),
        'faq': _faq_of(node),
        'description': plain_links(strip_storage(node.get('description', '') or '')),
        '_raw_html': bool(node.get('_raw_html')),
    }


def art_eligible(n):
    return bool(n['title']) and bool(n['content'] or n['faq'])


def build_groups(help_sec):
    """Group the help tree under its root categories, mirroring the bot."""
    root_children = [c for c in (help_sec.get('root', {}).get('children') or []) if isinstance(c, str)]
    groups, claimed = [], set()

    def collect(tid, kids):
        node = help_sec.get(tid)
        if not isinstance(node, dict):
            return
        for ch in node.get('children') or []:
            if isinstance(ch, str):
                ch = ch.strip()
                if ch and ch not in claimed and ch not in WEB_DROPS:
                    claimed.add(ch)
                    kids.append(node_from_sec(help_sec, ch))
                    collect(ch, kids)

    for cat in root_children:
        cat_node = node_from_sec(help_sec, cat)
        if not cat_node['title']:
            continue
        kids = []
        collect(cat, kids)
        groups.append({'cat': cat_node, 'kids': kids})
        claimed.add(cat)

    # Safety net: nodes unreachable from root still deserve a place.
    orphans = []
    for tid, node in help_sec.items():
        if isinstance(node, dict) and 'title' in node and tid not in claimed and tid != 'root':
            n = node_from_sec(help_sec, tid)
            if art_eligible(n):
                orphans.append(n)
    if orphans:
        groups.append({'cat': {'id': 'misc', 'title': 'More topics', 'content': '', 'faq': []},
                       'kids': orphans})
    return groups


def _ascii_tables_to_html(text):
    """Convert ASCII box tables (│ separators, as Telegram renders them)
    inside *escaped* text into styled HTML tables. Non-table lines pass
    through unchanged; rendered tables are appended after the text."""
    lines = text.split('\n')
    out, rows = [], []
    table_parts = []

    def flush():
        if rows:
            ncols = max(len(r) for r in rows)
            t = ['<div class="table-scroll"><table><thead><tr>']
            t += ['<th>%s</th>' % c for c in rows[0]]
            t += ['</tr></thead><tbody>']
            for r in rows[1:]:
                r = r + [''] * (ncols - len(r))
                t.append('<tr>' + ''.join('<td>%s</td>' % c for c in r) + '</tr>')
            t.append('</tbody></table></div>')
            table_parts.append(''.join(t))
            rows.clear()

    for ln in lines:
        if '│' in ln:
            if re.fullmatch(r'[─┌┐└┘├┤┬┴┼│\s]+', ln):
                continue
            cells = [c.strip() for c in re.split('│', ln) if c.strip()]
            if cells:
                rows.append(cells)
            continue
        # separator rule lines (─ ┼ with no │) belong to the table — drop them
        if re.fullmatch(r'[\u2500\u250c\u2510\u2514\u2518\u251c\u2524\u252c\u2534\u253c\u2502\s]+', ln):
            continue
        flush()
        out.append(ln)
    flush()
    body = '\n'.join(out)
    # Merge fragments: an escaped <b> title inside the table block splits the
    # header row from its body rows, so a header-only table is stitched into
    # the fragment that follows it.
    merged = []
    for t in table_parts:
        if merged and '<tbody></tbody>' in merged[-1]:
            b = t.index('<tbody>') + len('<tbody>')
            e = t.index('</tbody>')
            hb = t.index('<th>')
            he = t.index('</tr>', hb)  # the fragment's own header row
            head_cells = t[hb:he].replace('<th>', '<td>').replace('</th>', '</td>')
            merged[-1] = merged[-1].replace(
                '<tbody></tbody></table></div>',
                '<tbody><tr>' + head_cells + '</tr>' + t[b:e] + '</tbody></table></div>')
        else:
            merged.append(t)
    table_parts = merged
    for t in table_parts:
        body = (body + '\n\n' + t) if body else t
    return body


# ------------------------------------------------------- inline links ----
# Article bodies may point at another help article with
#     [[article_id|Visible label]]
# The website turns that into a hash route (or a real .html link on the
# static mirrors); both bots turn it into the matching web Help Center URL.
# Keeping the marker in the translations instead of raw <a> tags means the
# same text renders correctly in every consumer and can never ink an
# unverified URL into a wall of prose.
HELP_LINK_RE = re.compile(r'\[\[([a-zA-Z0-9_-]+)(?:\|([^\]]+))?\]\]')


def plain_links(text):
    """Marker-free copy for search snippets, meta descriptions and llms.txt."""
    if not text:
        return ''
    return HELP_LINK_RE.sub(
        lambda m: (m.group(2) or m.group(1).replace('_', ' ').title()), text)


def text_to_html(text):
    """Minimal, safe markup: keep the inline tags the bot already uses, turn
    blank-line separated blocks into <p>, keep bullet lines as a list, and
    render ASCII box tables (│ separators) as real styled tables."""
    if not text:
        return ''
    text = html_mod.escape(text, quote=False)
    # Telegram-only <pre> wrappers: their content is a plain ASCII table the
    # converter below turns into a real HTML table — drop the markers.
    text = text.replace('&lt;pre&gt;', '').replace('&lt;/pre&gt;', '')
    text = _ascii_tables_to_html(text)
    for tag in ('b', 'i', 'code', 'u', 's'):
        text = text.replace('&lt;%s&gt;' % tag, '<%s>' % tag).replace('&lt;/%s&gt;' % tag, '</%s>' % tag)
    # Source help texts ship pre-escaped entities (&lt; &gt; &quot;) for display;
    # html.escape() above double-escaped them (&amp;lt; ...) so pages showed
    # literal "&quot;"/"&lt;" garbage. Restore single escaping. Raw "&" from
    # normal copy (e.g. "Backup & export") stays correctly escaped. The
    # &amp;amp; rule runs last so nested "&amp;lt;" still resolves correctly.
    for _a, _b in (('&amp;lt;', '&lt;'), ('&amp;gt;', '&gt;'),
                   ('&amp;quot;', '&quot;'), ('&amp;#39;', '&#39;'),
                   ('&amp;amp;', '&amp;')):
        text = text.replace(_a, _b)
    text = HELP_LINK_RE.sub(
        lambda m: '<a class="hc-ilink" href="#/a/%s">%s</a>'
                  % (m.group(1), m.group(2) or m.group(1).replace('_', ' ').title()),
        text)
    # Source strings carry whole lists inline ("Requirements • Bot must be an
    # admin • Post messages ..." or "1. Open the bot 2. Tap ..."), so nothing
    # ever became a list and the article read as one wall of text. Break every
    # bullet and numbered step onto its own line before the block splitter.
    text = re.sub(r'[ \t]*\u2022[ \t]*', '\n\u2022 ', text)
    text = re.sub(r'[ \t]+(?=[1-9][0-9]?\.[ \t])', '\n', text)
    # Bullets already on their own lines just gained a leading newline above;
    # keep the list together instead of turning every item into its own block.
    text = re.sub(r'\n{2,}\u2022 ', '\n\u2022 ', text)
    blocks = re.split(r'\n\s*\n', text)
    out = []
    for block in blocks:
        if 'table-scroll' in block:
            out.append(block.strip())
            continue
        lines = [ln.strip() for ln in block.split('\n') if ln.strip()]

        def _flush(seg):
            """Emit prose, bullets and numbered steps as separate blocks."""
            if not seg:
                return
            chunk, kind = [], None

            def emit(k, items):
                if not items or not k:
                    return
                if k == 'p':
                    out.append('<p>%s</p>' % '<br>'.join(items))
                else:
                    out.append('<%s>%s</%s>' % (k, ''.join('<li>%s</li>' % i for i in items), k))

            for ln in seg:
                m = re.match(r'^(?:\u2022|[-*])[ \t]+(.*)$', ln)
                if m:
                    k, val = 'ul', m.group(1)
                else:
                    m = re.match(r'^[0-9]{1,2}\.[ \t]+(.*)$', ln)
                    k, val = ('ol', m.group(1)) if m else ('p', ln)
                if k != kind:
                    emit(kind, chunk)
                    chunk, kind = [], k
                chunk.append(val)
            emit(kind, chunk)

        # A "## Heading" line becomes a real section heading, so long guides
        # get the jump-to-section rail on the article page. It works no matter
        # where the heading sits inside its blank-line separated block.
        seg = []
        for ln in lines:
            if ln.startswith('## '):
                _flush(seg)
                seg = []
                out.append('<h3>%s</h3>' % ln[3:].strip())
            else:
                seg.append(ln)
        _flush(seg)
    return '\n'.join(out)


def _load_seo_articles():
    """Load the web-only SEO article set (website/_build/seo_articles.py)."""
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        if here not in sys.path:
            sys.path.insert(0, here)
        from seo_articles import SEO_ARTICLES
        arts = [a for a in SEO_ARTICLES if isinstance(a, dict) and a.get('id')]
        try:
            from seo_articles_b import ARTICLES_B
            arts += [a for a in ARTICLES_B if isinstance(a, dict) and a.get('id')]
        except Exception:  # pragma: no cover
            pass
        seen, out = set(), []
        for a in arts:
            if a['id'] not in seen:
                seen.add(a['id'])
                out.append(a)
        return out
    except Exception:  # pragma: no cover - build must not die over marketing
        return []


def inject_seo_articles(help_sec):
    """Attach web-only SEO articles to the help tree (build-time only).

    Every article is appended under its ``category`` so it appears in that
    category page, its card count and the search index; each node keeps its
    own longer human-written copy plus Q&A pairs for FAQPage rich results.
    """
    for art in _load_seo_articles():
        tid = art['id']
        if tid in help_sec:
            continue
        help_sec[tid] = {
            'title': fill_placeholders(art.get('title', '')),
            'content': fill_placeholders(art.get('content', '')),
            'description': fill_placeholders(art.get('description', '')),
            'faq': [{'q': fill_placeholders(f.get('q', '')),
                     'a': fill_placeholders(f.get('a', '')),
                     'links': [l for l in (f.get('links') or []) if isinstance(l, str)]}
                    for f in art.get('faq', []) if isinstance(f, dict) and (f.get('q') or f.get('a'))],
            'children': [],
            '_raw_html': True,
            '_seo': True,
        }
        parent = art.get('category')
        if parent and isinstance(help_sec.get(parent), dict):
            kids = help_sec[parent].setdefault('children', [])
            if isinstance(kids, list) and tid not in kids:
                kids.append(tid)


def article_faq_ld(n):
    """FAQPage JSON-LD for one article (drives Google rich results)."""
    if not n.get('faq'):
        return ''
    ents = []
    for f in n['faq']:
        # Wiki links ([[id|Label]]) must be resolved before the tags are
        # stripped: an unresolved marker is invisible on the page but ships
        # straight into the FAQPage JSON-LD that Google reads.
        a = ' '.join(re.sub(r'<[^>]+>', ' ', plain_links(f['a'])).split())
        ents.append({'@type': 'Question', 'name': ' '.join(re.sub(r'<[^>]+>', ' ', plain_links(f['q'])).split()),
                     'acceptedAnswer': {'@type': 'Answer', 'text': a}})
    payload = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': ents}
    return ('\n  <script type="application/ld+json">'
            + json.dumps(payload, ensure_ascii=False) + '</script>')


def _blog_search_docs():
    """Blog articles as search docs. c='blog' renders a Blog chip; href
    points at the real blog page. Reads the index the blog builder exports
    (falls back to importing the article modules directly)."""
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    idx = os.path.join(here, '_blog_search_data.json')
    docs = []
    try:
        raw = json.load(open(idx, encoding='utf-8'))
        docs = [{'id': d['id'], 'c': 'blog', 't': d['t'], 'b': d['b'], 'f': d.get('f', ''),
                 'd': d.get('d', ''), 'href': 'blog/a/' + d['id'] + '.html'} for d in raw]
    except Exception:
        pass
    return docs


def build_search_json(article_order, groups):
    cat_title = {g['cat']['id']: g['cat']['title'] for g in groups}
    sections = []
    for n in article_order:
        faq = ' '.join((re.sub(r'<[^>]+>', ' ', f['q']) + ' ' + re.sub(r'<[^>]+>', ' ', f['a'])) for f in n['faq'])
        body = re.sub(r'<[^>]+>', ' ', plain_links(n['content']))
        desc = (plain_links(n.get('description') or '') or ' '.join(body.split())[:160])
        sections.append({'id': n['id'], 'c': n.get('c', ''), 't': n['title'], 'b': body, 'f': faq, 'd': desc})
    # Blog articles are intentionally NOT part of the help index: the help
    # search must only answer with help articles, and the blog hub searches
    # its own corpus (window.__BLOG_DOCS). Mixing the two used to surface
    # marketing posts inside help results and burned half of every result
    # list on articles that do not describe the bot.
    return json.dumps(sections, ensure_ascii=False)


# ------------------------------------------------------------------ CSS ----
CSS = r'''
    :root { --hc-r: 18px; --hc-head: 64px; }

    /* This page scrolls normally — opt out of the legal-pages mobile shell. */
    @media (max-width: 760px) {
      html, body { height: auto; }
      body { display: block; height: auto; overflow: visible; }
      footer.site { display: block; }
    }

    /* ---------- phones: the shell reads as a simple single column ---------- */
    @media (max-width: 760px) {
      .hc-content { padding: 0 18px 90px; }
      .hc-hero { padding-top: 26px; }
      .hc-hero h1 { font-size: clamp(1.55rem, 7.2vw, 2.2rem); }
      .hc-search { margin-top: 22px; }
      #hcSearch { min-height: 54px; font-size: 1rem; }
      .hc-try { margin-top: 20px; }
      .hc-grid { gap: 12px; }
      .hc-card { border-radius: 16px; }
      .hc-side-title { padding: 10px 12px 12px; }
      /* the AI line wraps on narrow screens */
      .hc-ai-line { margin: 2px 8px 10px; font-size: .82rem; }
      .hc-pager { margin-bottom: 60px; }
    }

    body { background: var(--bg); }

    a { color: var(--green-strong); }
    a:focus-visible, button:focus-visible, input:focus-visible {
      outline: 2px solid var(--green); outline-offset: 2px; border-radius: 8px;
    }

    /* ---------- views ---------- */
    .view[hidden] { display: none !important; }
    .view.anim { animation: hcIn .38s cubic-bezier(.22,.61,.36,1) both; }
    .view h1:focus, .view h2:focus { outline: none; } /* a11y focus target, ring is visual noise */
    @keyframes hcIn { from { opacity: 0; transform: translateY(14px); } }
    main.help-main { min-height: 60vh; }

    /* ---------- cards ---------- */
    .hc-card {
      background: var(--surface);
      border: 1px solid var(--border); border-radius: var(--hc-r);
      box-shadow: var(--shadow-sm);
    }

    /* ---------- shell: flush-left sidebar + content (TikTok-style) ---------- */
    .hc-shell { display: flex; align-items: flex-start; max-width: none; padding: 0; }
    .hc-side {
      flex: none; width: 278px; position: sticky; top: var(--hc-head);
      height: calc(100vh - var(--hc-head)); overflow-y: auto; overscroll-behavior: contain;
      border-right: 1px solid var(--border); padding: 18px 12px 48px; scrollbar-width: thin;
    }
    @media (min-width: 1021px) {
      .hc-side { transition: margin-left .45s var(--ease-apple), opacity .3s var(--ease-apple), visibility 0s .45s; }
      html.hc-collapsed .hc-side { margin-left: -284px; opacity: 0; visibility: hidden; pointer-events: none; }
      html:not(.hc-collapsed) .hc-side { transition-delay: 0s; }
    }
    html[data-motion="off"] .hc-side { transition: none !important; }
    .hc-side-title button { margin-left: auto; }
    .hc-side-x {
      display: inline-flex; align-items: center; justify-content: center; flex: none;
      width: 30px; height: 30px; border-radius: 9px; background: none;
      border: 1px solid transparent; color: var(--text-dim); cursor: pointer;
      transition: border-color .2s, color .2s, background .2s;
    }
    .hc-side-x:hover { border-color: var(--border); color: var(--text); background: var(--surface-2); }
    .hc-side-x svg { width: 16px; height: 16px; transform: rotate(180deg); }
    .hc-side-reveal {
      display: none; position: fixed; z-index: 70; top: calc(var(--hc-head) + 14px); left: 14px;
      align-items: center; gap: 8px; padding: 9px 15px 9px 12px; border-radius: 999px;
      font: inherit; font-size: .85rem; font-weight: 750; color: var(--text);
      background: var(--surface);
      border: 1px solid var(--border); cursor: pointer;
      box-shadow: var(--shadow-sm); transition: border-color .2s, color .2s, opacity .3s,
        visibility 0s, transform .35s var(--ease-apple);
    }
    .hc-side-reveal:hover { border-color: var(--green); color: var(--green-strong); text-decoration: none; }
    .hc-side-reveal svg { width: 16px; height: 16px; color: var(--green-strong); }
    @media (min-width: 1021px) {
      html.hc-collapsed .hc-side-reveal { display: inline-flex; }
    }
    .hc-side-title { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.02rem; padding: 2px 10px 14px; letter-spacing: -.01em; }
    .hc-side-title svg { width: 20px; height: 20px; color: var(--green-strong); }
    .hc-nav { display: flex; flex-direction: column; gap: 2px; }
    .hc-nav-item {
      display: flex; align-items: center; gap: 10px; padding: 9px 10px; border-radius: 10px;
      color: var(--text); font-weight: 600; font-size: .9rem; line-height: 1.25;
      transition: background .16s, color .16s;
    }
    .hc-nav-item:hover { background: color-mix(in srgb, var(--green) 8%, transparent); text-decoration: none; }
    .hc-nav-item svg { flex: none; width: 18px; height: 18px; color: var(--text-dim); transition: color .16s; }
    .hc-nav-item .n {
      margin-left: auto; flex: none; font-size: .72rem; font-weight: 700; color: var(--text-dim);
      background: var(--surface-2); border-radius: 999px; padding: 2px 8px; font-variant-numeric: tabular-nums;
    }
    .hc-nav-item.active { background: color-mix(in srgb, var(--green) 12%, transparent); color: var(--green-strong); }
    .hc-nav-item.active svg { color: var(--green-strong); }
    .hc-nav-item.active .n { background: color-mix(in srgb, var(--green) 18%, transparent); color: var(--green-strong); }
    /* topics submenu slides open/closed (grid-rows trick); the site's
       Animations setting neutralises the transition automatically */
    .hc-subnav { display: grid; grid-template-rows: 0fr; opacity: 0;
      transition: grid-template-rows .42s var(--ease-apple), opacity .28s var(--ease-apple); }
    .hc-subnav.open { grid-template-rows: 1fr; opacity: 1; }
    .hc-subnav-in { overflow: hidden; min-height: 0; display: flex; flex-direction: column; gap: 1px; }
    .hc-subnav a {
      display: block; padding: 6px 10px 6px 38px; border-radius: 8px;
      color: var(--text-dim); font-size: .845rem; font-weight: 550; line-height: 1.35;
    }
    .hc-subnav a:hover { color: var(--green-strong); background: color-mix(in srgb, var(--green) 7%, transparent); text-decoration: none; }
    .hc-subnav a.active { color: var(--green-strong); font-weight: 750; background: color-mix(in srgb, var(--green) 10%, transparent); }
    .hc-side-cta {
      margin: 18px 6px 0; padding: 14px; border-radius: 14px; text-align: center;
      background: color-mix(in srgb, var(--green) 8%, transparent); border: 1px dashed color-mix(in srgb, var(--green) 35%, transparent);
      font-size: .84rem; color: var(--text-dim);
    }
    .hc-side-cta b { display: block; color: var(--text); margin-bottom: 8px; font-size: .9rem; }

    .hc-content { flex: 1; min-width: 0; --hc-gut: clamp(20px, 4vw, 40px); padding: 0 var(--hc-gut) 90px; }
    .hc-content > .view { max-width: 1120px; margin: 0 auto; }
    .hc-content .hc-hero, .hc-content .hc-grid, .hc-content .hc-art,
    .hc-content .hc-crumbs, .hc-content .hc-cat-head, .hc-content .hc-intro,
    .hc-content .hc-list, .hc-content .hc-pager, .hc-content .hc-faq { margin-left: auto; margin-right: auto; }

    /* mobile drawer */
    .hc-scrim { position: fixed; inset: 0; z-index: 80; background: rgba(8,14,11,.45); opacity: 0; pointer-events: none; transition: opacity .25s; }
    .hc-menu-btn { display: none; }
    @media (max-width: 1020px) {
      /* the parked drawer lives off-canvas — never let it widen the page */
      html, body { overflow-x: clip; }
      .hc-content { padding-left: var(--hc-gut); }
      /* The drawer hangs off the right edge and slides in from it, under the
         burger that opened it. */
      .hc-side {
        position: fixed; z-index: 90; top: 0; right: 0; left: auto; height: 100dvh; width: min(320px, 86vw);
        background: var(--surface); transform: translateX(104%);
        transition: transform .3s cubic-bezier(.22,.61,.36,1); box-shadow: var(--shadow); padding-top: 14px;
      }
      body.hc-side-open .hc-side { transform: none; }
      body.hc-side-open .hc-scrim { opacity: 1; pointer-events: auto; }
      .hc-menu-btn { display: inline-flex; }
    }
    @media (min-width: 1021px) { .hc-scrim { display: none; } }

    /* ---------- header search (TikTok-style, every page) ---------- */
    .hc-hsearch { position: relative; width: min(400px, 34vw); margin-left: 6px; }
    .hc-hsearch .sic { position: absolute; left: 13px; top: 50%; translate: 0 -50%; width: 16px; height: 16px; color: var(--text-dim); pointer-events: none; z-index: 2; }
    .hc-hsearch input {
      width: 100%; height: 40px; padding: 0 62px 0 37px; font: inherit; font-size: .9rem; color: var(--text);
      background: var(--surface-2); border: 1px solid transparent; border-radius: 999px; outline: none;
      transition: background .2s, border-color .2s, box-shadow .2s;
    }
    .hc-hsearch input::placeholder { color: var(--text-dim); }
    .hc-hsearch input:focus {
      background: var(--surface); border-color: color-mix(in srgb, var(--green) 55%, transparent);
      box-shadow: 0 0 0 3px color-mix(in srgb, var(--green) 14%, transparent);
    }
    .hc-hsearch kbd {
      position: absolute; right: 10px; top: 50%; translate: 0 -50%; pointer-events: none;
      font-family: inherit; font-size: .72rem; font-weight: 800; color: var(--text-dim);
      background: var(--surface); border: 1px solid var(--border); border-bottom-width: 2px;
      border-radius: 6px; padding: 2px 8px;
    }
    /* only one search per context: hero search owns the home page,
       header search owns every other view */
    body.hc-onhome .hc-hsearch { display: none; }
    .hc-brand-help { color: var(--text-dim); font-weight: 600; font-size: 1rem; }
    .hc-brand-help::before { content: "/"; margin: 0 10px; color: var(--border); font-weight: 400; }

    /* results dropdown (anchored to whichever input is focused) */
    /* mini-AI interpretation line above results */
    .hc-ai-line {
      display: flex; align-items: center; gap: 8px;
      margin: 4px 10px 10px; padding: 8px 12px;
      border-radius: 12px; font-size: .86rem; color: var(--text-dim);
      background: color-mix(in srgb, var(--green) 7%, transparent);
      border: 1px solid color-mix(in srgb, var(--green) 22%, transparent);
    }
    .hc-ai-line b { color: var(--green-strong); font-weight: 750; }
    .hc-ai-dot { width: 7px; height: 7px; border-radius: 50%; flex: none;
      background: var(--green); box-shadow: 0 0 0 3px color-mix(in srgb, var(--green) 18%, transparent); }

    .hc-results {
      position: absolute; top: calc(100% + 8px); left: 0; right: auto; min-width: 100%; width: max-content; max-width: min(480px, 92vw);
      z-index: 95; background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
      box-shadow: var(--shadow); text-align: left; max-height: 420px; overflow-y: auto; scrollbar-width: thin;
    }
    .hc-hsearch .hc-results { left: auto; right: 0; }
    .hc-res {
      display: block; width: 100%; text-align: left; font: inherit; color: var(--text);
      background: none; border: 0; border-bottom: 1px solid var(--border);
      padding: 12px 16px; cursor: pointer;
    }
    .hc-res:last-child { border-bottom: 0; }
    .hc-res:hover, .hc-res.cur { background: color-mix(in srgb, var(--green) 9%, transparent); }
    .hc-res-top { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
    .hc-res-t { font-weight: 750; font-size: .94rem; }
    .hc-res-cat {
      flex: none; font-size: .71rem; font-weight: 700; color: var(--green-strong);
      background: color-mix(in srgb, var(--green) 11%, transparent);
      padding: 3px 9px; border-radius: 999px; white-space: nowrap;
    }
    .hc-res-s { margin: 5px 0 0; font-size: .84rem; color: var(--text-dim); line-height: 1.45;
      display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .hc-results .hc-empty { padding: 16px; font-size: .9rem; color: var(--text-dim); }
    .hc-res-all { display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%;
      padding: 12px 16px; font: inherit; font-size: .88rem; font-weight: 750; color: var(--green-strong);
      background: color-mix(in srgb, var(--green) 7%, transparent); border: 0; cursor: pointer; text-decoration: none; }
    .hc-res-all:hover { text-decoration: none; background: color-mix(in srgb, var(--green) 13%, transparent); }
    .hc-res-all svg { width: 15px; height: 15px; }
    .hc-empty-ill { display: grid; place-items: center; width: 56px; height: 56px; margin: 6px auto 12px;
      border-radius: 16px; color: var(--green-strong);
      background: color-mix(in srgb, var(--green) 10%, transparent);
      border: 1px solid color-mix(in srgb, var(--green) 24%, transparent); }
    .hc-empty-ill svg { width: 26px; height: 26px; }
    .hc-empty-q { font-size: .92rem; color: var(--text-dim); padding: 0 16px; text-align: center; }
    .hc-empty-t { font-weight: 800; font-size: .98rem; color: var(--text); padding: 2px 16px 0; text-align: center; }
    .hc-empty-s { font-size: .85rem; color: var(--text-dim); padding: 4px 16px 2px; text-align: center; }
    .hc-sug-h { padding: 10px 16px 4px; font-size: .8rem; font-weight: 700; color: var(--text-dim); }
    .hc-sug-h a { color: var(--green-strong); }
    /* "Best result" split: one clear winner gets a labeled hero card, the
       rest stay compact rows below it */
    .hc-res-sec {
      padding: 10px 16px 5px; font-size: .84rem; font-weight: 800;
      letter-spacing: 0; color: var(--text-dim);
    }
    .hc-res-best {
      border-bottom: 1px solid var(--border);
      border-left: 3px solid var(--green);
      background: color-mix(in srgb, var(--green) 7%, transparent);
    }
    .hc-res-best:hover, .hc-res-best.cur {
      background: color-mix(in srgb, var(--green) 13%, transparent); padding-left: 16px;
    }
    .hc-res-best .hc-res-t { font-size: 1rem; }
    .hc-best {
      display: block; max-width: 760px; margin: 0 auto 20px; padding: 16px 20px 17px;
      border-radius: var(--hc-r); text-decoration: none; color: var(--text);
      border: 1px solid var(--border); background: var(--surface);
      transition: border-color .2s, box-shadow .2s;
    }
    .hc-best:hover { text-decoration: none; border-color: var(--green); box-shadow: var(--shadow-sm); }
    .hc-best-label {
      display: inline-flex; align-items: center; gap: 7px;
      font-size: .84rem; font-weight: 700; letter-spacing: 0;
      color: var(--text-dim);
      background: none; padding: 0; border-radius: 0; margin-bottom: 8px;
    }
    .hc-best-label::before {
      content: ''; width: 6px; height: 6px; border-radius: 50%;
      background: var(--green); flex: none;
    }
    .hc-best b { display: block; font-size: 1.06rem; line-height: 1.3; letter-spacing: -.01em; }
    .hc-best .hc-best-cat { display: inline-block; margin-top: 5px; font-size: .74rem; font-weight: 700; color: var(--text-dim); }
    .hc-best p { margin: 8px 0 0; font-size: .88rem; color: var(--text-dim); line-height: 1.5;
      display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    mark { background: color-mix(in srgb, #ffd84d 50%, transparent); color: inherit; border-radius: 3px; padding: 0 1px; }

    /* ---------- hero (home) ---------- */
    .hc-hero { text-align: center; padding: clamp(40px, 6.5vw, 84px) 0 8px; }
    .hc-kicker {
      display: inline-flex; align-items: center; gap: 8px; font-size: .86rem; font-weight: 650;
      color: var(--green-strong);
      background: color-mix(in srgb, var(--green) 11%, transparent);
      border: 1px solid color-mix(in srgb, var(--green) 28%, transparent);
      padding: 7px 14px; border-radius: 999px;
    }
    .hc-kicker svg { width: 15px; height: 15px; }
    .hc-hero h1 {
      font-size: clamp(2.2rem, 5.2vw, 3.4rem); line-height: 1.06; letter-spacing: -.035em;
      margin: 20px 0 0;
    }
    .hc-hero h1 .grad { color: var(--green); }
    .hc-sub { color: var(--text-dim); font-size: 1.03rem; margin: 16px auto 0; max-width: 560px; line-height: 1.55; }

    .hc-search { position: relative; max-width: 680px; margin: 30px auto 0; }
    .hc-search .sic { position: absolute; left: 21px; top: 50%; translate: 0 -50%; width: 20px; height: 20px; color: var(--text-dim); pointer-events: none; z-index: 2; }
    #hcSearch {
      width: 100%; min-height: 60px; padding: 15px 76px 15px 54px; font-size: 1.04rem;
      font-family: inherit; color: var(--text);
      background: var(--surface); border: 1px solid var(--border); border-radius: 999px; outline: none;
      box-shadow: var(--shadow-sm); transition: border-color .2s, box-shadow .2s;
    }
    #hcSearch::placeholder { color: var(--text-dim); }
    #hcSearch:focus {
      border-color: color-mix(in srgb, var(--green) 60%, transparent);
      box-shadow: 0 0 0 4px color-mix(in srgb, var(--green) 15%, transparent), var(--shadow-sm);
      /* the focus ring must paint UNDER the icon, not over it — the glow ring
         used to cover the magnifier the moment the field was focused */
      --hc-icon-z: 2;
    }
    .hc-search .sic { z-index: 2; }
    .hc-sbtn {
      position: absolute; right: 12px; top: 50%; translate: 0 -50%;
      font-family: inherit; font-size: .8rem; font-weight: 800; line-height: 1.3;
      color: var(--text-dim); background: var(--surface-2);
      border: 1px solid var(--border); border-bottom-width: 2px;
      border-radius: 7px; padding: 3px 11px; cursor: pointer;
      transition: color .15s, border-color .15s;
    }
    .hc-sbtn:hover { color: var(--green-strong); border-color: color-mix(in srgb, var(--green) 45%, var(--border)); }
    .hc-search .hc-results { left: 0; right: 0; width: auto; max-width: none; }
    @media (max-width: 560px) { .hc-sbtn { display: none; } #hcSearch { padding-right: 20px; } }

    /* "Try asking" chips (Canva-style) */
    .hc-try { margin: 26px auto 0; max-width: 760px; }
    .hc-try-label { font-size: .84rem; font-weight: 650; letter-spacing: 0; color: var(--text-dim); }
    .hc-chiprow { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-top: 13px; }
    .hc-chip {
      display: inline-flex; align-items: center; gap: 8px; font-size: .88rem; font-weight: 650;
      color: var(--text); background: var(--surface); border: 1px solid var(--border);
      padding: 9px 16px; border-radius: 999px; cursor: pointer; font-family: inherit; line-height: 1.3;
      transition: border-color .18s, color .18s, transform .18s, box-shadow .18s;
    }
    .hc-chip svg { width: 15px; height: 15px; flex: none; color: var(--green-strong); }
    .hc-chip:hover { border-color: color-mix(in srgb, var(--green) 50%, transparent); color: var(--green-strong); text-decoration: none; }

    /* ---------- browse by topic ---------- */
    .hc-section-h { display: flex; align-items: baseline; gap: 12px; margin: 48px 0 2px; }
    .hc-section-h h2 { font-size: 1.42rem; letter-spacing: -.02em; margin: 0; }
    .hc-section-h span { color: var(--text-dim); font-size: .88rem; }

    .hc-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; padding: 16px 0 8px; }
    @media (max-width: 1020px) { .hc-grid { grid-template-columns: 1fr 1fr; } }
    @media (max-width: 640px)  { .hc-grid { grid-template-columns: 1fr 1fr; gap: 10px; }
      /* Phones keep two cards per row: halves the scroll through 20+ topics. Cards tighten up and the article preview hides (one tap away). */
      .hc-grid > .hc-cat { padding: 13px; }
      .hc-grid .hc-cat-head { gap: 9px; }
      .hc-grid .hc-cat-go { display: none; }
      .hc-grid .hc-cat-prev { display: none; } }
    .hc-grid > .hc-cat, .hc-list > .hc-row { min-width: 0; }
    .hc-cat { display: block; padding: 18px; color: var(--text); transition: transform .2s, border-color .2s, box-shadow .2s; }
    .hc-cat:hover { text-decoration: none; border-color: color-mix(in srgb, var(--green) 45%, var(--border)); transform: translateY(-2px); box-shadow: var(--shadow); }
    .hc-cat-head { display: flex; align-items: center; gap: 13px; }
    .hc-cat-head > * { min-width: 0; } /* long titles must shrink inside 170px phone cards */
    .hc-ic {
      flex: none; width: 46px; height: 46px; border-radius: 13px; display: grid; place-items: center;
      color: var(--green-strong);
      background: color-mix(in srgb, var(--green) 10%, transparent);
      border: 1px solid color-mix(in srgb, var(--green) 22%, transparent);
    }
    /* varied accents: every 6th card gets its own hue + corner rhythm */
    .hc-grid > .hc-cat:nth-child(6n+2) .hc-ic { color: #2563eb; background: color-mix(in srgb, #2563eb 10%, transparent); border-color: color-mix(in srgb, #2563eb 24%, transparent); }
    .hc-grid > .hc-cat:nth-child(6n+3) .hc-ic { color: #7c3aed; background: color-mix(in srgb, #7c3aed 10%, transparent); border-color: color-mix(in srgb, #7c3aed 24%, transparent); }
    .hc-grid > .hc-cat:nth-child(6n+4) .hc-ic { color: #b45309; background: color-mix(in srgb, #b45309 10%, transparent); border-color: color-mix(in srgb, #b45309 24%, transparent); }
    .hc-grid > .hc-cat:nth-child(6n+5) .hc-ic { color: #0e7490; background: color-mix(in srgb, #0e7490 10%, transparent); border-color: color-mix(in srgb, #0e7490 24%, transparent); }
    .hc-grid > .hc-cat:nth-child(6n+6) .hc-ic { color: #be123c; background: color-mix(in srgb, #be123c 10%, transparent); border-color: color-mix(in srgb, #be123c 24%, transparent); }
    .hc-grid > .hc-cat:nth-child(6n+2) { border-radius: 20px; }
    .hc-grid > .hc-cat:nth-child(6n+4) { border-radius: 12px; }
    .hc-grid > .hc-cat:nth-child(6n+5) { border-radius: 22px 16px 22px 16px; }
    .hc-band-grid > a:nth-child(6n+2) { border-color: color-mix(in srgb, #2563eb 35%, var(--border)); }
    .hc-band-grid > a:nth-child(6n+3) { border-color: color-mix(in srgb, #7c3aed 35%, var(--border)); }
    .hc-band-grid > a:nth-child(6n+4) { border-color: color-mix(in srgb, #b45309 35%, var(--border)); }
    .hc-band-grid > a:nth-child(6n+5) { border-color: color-mix(in srgb, #0e7490 35%, var(--border)); }
    .hc-band-grid > a:nth-child(6n+6) { border-color: color-mix(in srgb, #be123c 35%, var(--border)); }
    .hc-ic svg { width: 22px; height: 22px; }
    .hc-cat-t { font-weight: 800; font-size: .98rem; letter-spacing: -.01em; }
    .hc-cat-c { display: block; font-size: .78rem; color: var(--text-dim); margin-top: 1px; }
    .hc-cat-go { margin-left: auto; color: var(--text-dim); transition: transform .2s, color .2s; }
    .hc-cat-go svg { width: 17px; height: 17px; display: block; }
    .hc-cat:hover .hc-cat-go { color: var(--green-strong); transform: translateX(3px); }
    .hc-cat-prev { margin: 13px 0 0; padding: 11px 0 0; border-top: 1px dashed var(--border); display: flex; flex-direction: column; gap: 5px; }
    .hc-cat-prev span { font-size: .82rem; color: var(--text-dim); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .hc-cat-prev span::before { content: ""; display: inline-block; width: 5px; height: 5px; border-radius: 50%; background: color-mix(in srgb, var(--green) 55%, transparent); margin: 2px 8px 2px 2px; vertical-align: 2px; }
    .hc-cat-d { display: block; margin-top: 10px; font-size: .84rem; color: var(--text-dim); line-height: 1.5;
      display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

    .hc-home-cta { margin: 40px 0 20px; }
    /* ---------- support CTA strip (home, under the platform band) ---------- */
    .hc-cta { display: flex; align-items: center; gap: 16px; margin: 30px 0 4px; padding: 20px 22px;
      border-radius: 20px; background: color-mix(in srgb, var(--green) 8%, var(--surface));
      border: 1px solid color-mix(in srgb, var(--green) 26%, var(--border)); }
    .hc-cta .hc-ic { width: 44px; height: 44px; flex: none; }
    .hc-cta-t { flex: 1; min-width: 0; }
    .hc-cta-t b { display: block; font-size: 1rem; letter-spacing: -.01em; }
    .hc-cta-t span { color: rgba(255, 255, 255, .92); font-size: .88rem; }
    .hc-cta .btn { flex: none; }
    @media (max-width: 640px) { .hc-cta { flex-wrap: wrap; } .hc-cta .btn { width: 100%; justify-content: center; } }

    /* ---------- breadcrumbs ---------- */
    .hc-crumbs { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; padding: 26px 0 0; font-size: .87rem; color: var(--text-dim); }
    .hc-crumbs a { color: var(--text-dim); font-weight: 650; }
    .hc-crumbs a:hover { color: var(--green-strong); text-decoration: none; }
    .hc-crumbs svg { width: 13px; height: 13px; opacity: .6; }
    .hc-crumbs [aria-current] { color: var(--text); font-weight: 650; }

    /* ---------- category page ---------- */
    .hc-cat-head { display: flex; align-items: center; gap: 16px; padding: 26px 0 6px; scroll-margin-top: 84px; }
    .hc-cat-head .hc-ic { width: 56px; height: 56px; border-radius: 16px; }
    .hc-cat-head .hc-ic svg { width: 26px; height: 26px; }
    .hc-cat-head h1, .hc-cat-head h2 { margin: 0; font-size: clamp(1.55rem, 3.4vw, 2.15rem); letter-spacing: -.025em; }
    .hc-cat-head p { margin: 3px 0 0; color: var(--text-dim); font-size: .92rem; }
    .hc-intro { max-width: 780px; margin: 10px 0 0; color: var(--text); font-size: .97rem; line-height: 1.65; }
    .hc-intro p { margin: 0 0 8px; }

    /* TikTok-style two-column article list */
    .hc-list { display: grid; grid-template-columns: 1fr 1fr; column-gap: 48px; padding: 14px 0 26px; }
    @media (max-width: 860px) { .hc-list { grid-template-columns: 1fr; column-gap: 0; } }
    .hc-row {
      display: flex; align-items: center; gap: 12px; padding: 14px 6px;
      color: var(--text); border-bottom: 1px solid color-mix(in srgb, var(--border) 62%, transparent);
      transition: color .15s;
    }
    .hc-row:hover { text-decoration: none; color: var(--green-strong); }
    .hc-row-t { flex: 1; min-width: 0; font-weight: 650; font-size: .95rem; line-height: 1.4; }
    .hc-row:hover .hc-row-t { color: var(--green-strong); }
    .hc-row-m {
      flex: none; font-size: .73rem; font-weight: 700; color: var(--text-dim);
      background: var(--surface-2); border-radius: 999px; padding: 3px 9px; white-space: nowrap;
    }
    .hc-row-lead .hc-row-m { color: var(--green-strong); background: color-mix(in srgb, var(--green) 11%, transparent); }
    .hc-row > svg { flex: none; width: 15px; height: 15px; color: var(--text-dim); transition: transform .15s, color .15s; }
    .hc-row:hover > svg { color: var(--green-strong); transform: translateX(2px); }

    /* search page category filter chips */
    .hc-filters { display: flex; flex-wrap: wrap; gap: 8px; margin: 14px 0 6px; }
    .hc-filters[hidden] { display: none; }
    .hc-fchip { font: inherit; font-size: .84rem; font-weight: 650; color: var(--text-dim);
      background: var(--surface); border: 1px solid var(--border); border-radius: 999px;
      padding: 7px 14px; cursor: pointer; transition: color .18s, border-color .18s, background .18s; }
    .hc-fchip:hover { color: var(--green-strong); border-color: color-mix(in srgb, var(--green) 50%, transparent); }
    .hc-fchip.on { color: #fff; background: var(--green-strong); border-color: var(--green-strong); }

    /* ---------- full search results page ---------- */
    .hc-sempty { text-align: center; padding: 54px 20px 20px; }
    .hc-sempty .hc-ic { width: 64px; height: 64px; border-radius: 18px; margin: 0 auto 18px; }
    .hc-sempty .hc-ic svg { width: 28px; height: 28px; }
    .hc-sempty h2 { font-size: 1.35rem; letter-spacing: -.02em; margin: 0 0 8px; }
    .hc-sempty p { color: var(--text-dim); margin: 0 0 18px; }
    .hc-sempty .hc-sug-h { text-align: left; font-size: .8rem; font-weight: 700; color: var(--text-dim); margin: 8px 0 2px; }
    .hc-sempty .hc-list { text-align: left; }

    .hc-others { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; padding: 4px 0 72px; font-size: .85rem; color: var(--text-dim); }
    .hc-others a { color: var(--text); font-weight: 650; padding: 6px 12px; border-radius: 999px; background: var(--surface); border: 1px solid var(--border); }
    .hc-others a:hover { border-color: var(--green); color: var(--green-strong); text-decoration: none; }

    /* ---------- article page ---------- */
    .hc-art { max-width: 860px; margin: 12px auto 0; padding: clamp(26px, 4.5vw, 48px); }
    @media (max-width: 640px) {
      .hc-art { padding: 22px 18px 30px; border-radius: 14px; }
      .hc-body, .hc-body * { overflow-wrap: anywhere; }
      .hc-body .table-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; margin: 16px 0; }
    .hc-body table { width: 100%; border-collapse: collapse; background: var(--surface);
      border: 1px solid var(--border); border-radius: 12px; overflow: hidden;
      box-shadow: var(--shadow-sm); font-size: .9rem; }
    .hc-body th, .hc-body td { padding: 10px 14px; text-align: left;
      border-bottom: 1px solid var(--border); }
    .hc-body thead th { background: color-mix(in srgb, var(--green) 14%, transparent);
      font-weight: 700; }
    .hc-body tbody tr:last-child td { border-bottom: none; }
    .hc-body tbody tr:nth-child(even) { background: color-mix(in srgb, var(--green) 5%, transparent); }
    .hc-body td:not(:first-child), .hc-body th:not(:first-child) { text-align: center; }
    .hc-body code { word-break: break-all; }
    }
    .hc-art > h1, .hc-art > h2 { margin: 0; font-size: clamp(1.65rem, 3.6vw, 2.25rem); letter-spacing: -.025em; line-height: 1.15; }
    .hc-body { margin-top: 16px; }
    .hc-body p { margin: 0 0 13px; font-size: .98rem; line-height: 1.72; color: var(--text); }
    .hc-body ul { margin: 0 0 13px; padding-left: 22px; color: var(--text); font-size: .95rem; line-height: 1.7; }
    .hc-body li { margin: 3px 0; }
    .hc-body h3 { font-size: 1.2rem; letter-spacing: -.015em; margin: 30px 0 10px; scroll-margin-top: 86px; }
    .hc-body code {
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: .86em;
      background: color-mix(in srgb, var(--surface-2) 85%, transparent);
      border: 1px solid var(--border); padding: 1px 6px; border-radius: 6px;
    }

    /* Jump to a section — a slim strip tab glued to the sidebar's right
       edge (desktop). Hover/focus slides out a glass popover with the
       section names, like the legal pages' contents. Articles without
       sections render no container at all, so nothing shows. Mobile keeps
       the floating Contents button. */
    .hc-jump {
      position: fixed; left: 277px; top: 50%; transform: translateY(-50%);
      z-index: 60;
    }
    html.hc-collapsed .hc-jump { left: 0; }
    .hc-jump:empty { display: none; }
    .hc-jump-strip {
      display: flex; flex-direction: column; align-items: center; gap: 7px;
      padding: 13px 7px; cursor: pointer;
      border: 1px solid var(--border); border-left: none; border-radius: 0 14px 14px 0;
      background: var(--surface);
      box-shadow: 6px 6px 18px rgba(17, 24, 39, .06);
      transition: border-color .2s, color .2s, background .2s, padding .25s var(--ease-apple);
    }
    .hc-jump-strip svg { width: 17px; height: 17px; color: var(--green-strong); flex: none; }
    .hc-jump-strip .vtxt {
      writing-mode: vertical-rl; text-orientation: mixed;
      font-size: .68rem; font-weight: 650; letter-spacing: .04em;
      color: var(--text-dim);
    }
    .hc-jump:hover .hc-jump-strip, .hc-jump:focus-within .hc-jump-strip {
      border-color: var(--green); background: color-mix(in srgb, var(--green) 7%, var(--surface) 78%, transparent);
    }
    .hc-jump-pop {
      position: absolute; left: calc(100% + 10px); top: 50%; right: auto;
      translate: 0 -50%; transform: translateX(-8px); transform-origin: left center;
      min-width: 290px; max-width: 360px; max-height: min(60vh, 480px); overflow-y: auto;
    }
    .hc-jump:hover .hc-jump-pop, .hc-jump:focus-within .hc-jump-pop {
      opacity: 1; transform: translateX(0); pointer-events: auto; visibility: visible;
    }
    .hc-jump-pop .hc-jump-head { font-size: .8rem; font-weight: 650; letter-spacing: 0; color: var(--text-dim); padding: 4px 6px 8px; }
    .hc-jump-n { display: flex; flex-direction: column; gap: 2px; font-size: .93rem; }
    .hc-jump-n a { font-weight: 650; padding: 8px 12px; display: block; border-radius: 10px; color: var(--text); }
    .hc-jump-n a:hover { color: var(--green-strong); background: color-mix(in srgb, var(--green) 8%, transparent); }
    .hc-jump-n a::before { content: ""; display: inline-block; width: 5px; height: 5px; border-radius: 50%; background: var(--green); margin: 0 10px 2px 0; vertical-align: middle; }
    .hc-jump-n .dot { display: none; }
    @media (max-width: 1020px) {
      .hc-jump { display: none; }
    }

    /* mobile floating Contents button + bottom sheet (legal-pages style) */
    .hc-toc-fab {
      display: none; position: fixed; z-index: 85; left: 16px; bottom: calc(16px + env(safe-area-inset-bottom));
      align-items: center; gap: 8px; padding: 11px 16px; border-radius: 999px;
      font: inherit; font-size: .9rem; font-weight: 750; color: var(--text); cursor: pointer;
      background: var(--surface);
      border: 1px solid var(--border);
      box-shadow: var(--shadow-sm);
    }
    .hc-toc-fab svg { width: 17px; height: 17px; color: var(--green-strong); }
    @media (max-width: 640px) {
      .hc-toc-fab { display: inline-flex; }
      .hc-toc-fab[hidden] { display: none; }
    }
    .hc-toc-sheet {
      position: fixed; inset: auto 0 0 0; z-index: 101; max-height: 72dvh; display: flex; flex-direction: column;
      background: var(--surface); border-top: 1px solid var(--border); border-radius: 18px 18px 0 0;
      padding: 8px 20px calc(20px + env(safe-area-inset-bottom));
      transform: translateY(105%); visibility: hidden;
      transition: transform .38s cubic-bezier(.32,.72,.35,1), visibility 0s .4s;
    }
    .hc-toc-sheet.open { transform: none; visibility: visible; transition: transform .38s cubic-bezier(.32,.72,.35,1); }
    .hc-toc-head { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; font-weight: 800; font-size: 1.05rem; flex: none; }
    .hc-toc-nav { display: grid; grid-template-columns: 1fr 1.2fr 1fr; gap: 8px; margin: 2px 0 10px; }
    .hc-toc-navc { display: block; min-width: 0; padding: 9px 11px; border: 1px solid var(--border); border-radius: 12px;
      background: color-mix(in srgb, var(--surface-2) 55%, transparent); text-decoration: none; color: var(--text); position: relative; }
    .hc-toc-navc small { display: block; font-size: .76rem; font-weight: 700; letter-spacing: 0; color: var(--text-dim); }
    .hc-toc-navc b { display: block; font-size: .8rem; line-height: 1.3; margin-top: 3px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
    .hc-toc-navc span { display: none; }
    .hc-toc-navc svg { position: absolute; right: 8px; top: 50%; translate: 0 -50%; width: 14px; height: 14px; color: var(--text-dim); }
    a.hc-toc-navc:hover { text-decoration: none; border-color: var(--green); }
    .hc-toc-navc.cur { background: color-mix(in srgb, var(--green) 8%, transparent); border-color: color-mix(in srgb, var(--green) 35%, var(--border)); }
    .hc-toc-navc.cur b { -webkit-line-clamp: 3; }
    .hc-toc-navc.none { border-style: dashed; opacity: .6; }
    .hc-toc-list { flex: 1 1 auto; min-height: 0; overflow-y: auto; border-left: 2px dotted var(--border); margin: 6px 0 6px 6px; }
    .hc-toc-list li { position: relative; padding: 9px 0 9px 20px; list-style: none; }
    .hc-toc-list li::before { content: ''; position: absolute; left: -6px; top: 16px; width: 10px; height: 10px; border-radius: 50%; background: var(--surface); border: 2px solid var(--text-dim); box-sizing: border-box; }
    .hc-toc-list li a { display: block; color: var(--text); font-weight: 650; }
    .hc-toc-scrim { position: fixed; inset: 0; z-index: 100; background: rgba(0,0,0,.45); opacity: 0; pointer-events: none; transition: opacity .3s; }
    .hc-toc-scrim.open { opacity: 1; pointer-events: auto; }
    @media (min-width: 641px) { .hc-toc-sheet, .hc-toc-scrim { display: none !important; } }

    .hc-faq { margin-top: 26px; border-top: 1px solid var(--border); padding-top: 6px; }
    .hc-faq h2 { font-size: .9rem; font-weight: 650; letter-spacing: 0; color: var(--text-dim); margin: 14px 0 4px; }
    .hc-faq details { border-bottom: 1px dashed var(--border); }
    .hc-faq details:last-child { border-bottom: 0; }
    .hc-faq summary code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: .86em; background: var(--surface-2); padding: 1px 5px; border-radius: 6px; }
    .hc-faq summary {
      cursor: pointer; list-style: none; display: flex; align-items: center; justify-content: space-between;
      gap: 14px; padding: 14px 0; font-weight: 700; font-size: .95rem;
    }
    .hc-faq summary::-webkit-details-marker { display: none; }
    /* drawn plus (two bars, one shared center) instead of a "+" glyph:
       glyphs rotate off-center and the open-state x looks broken. Both
       bars spin together into a clean x. */
    .hc-faq summary { position: relative; padding-right: 28px; }
    .hc-faq summary::before, .hc-faq summary::after {
      content: ""; position: absolute; top: 50%; background: var(--green-strong);
      border-radius: 2px; transition: transform .25s var(--ease-spring, ease);
    }
    .hc-faq summary::before { right: 1px; width: 14px; height: 2px; transform: translateY(-50%); }
    .hc-faq summary::after { right: 7px; width: 2px; height: 14px; transform: translateY(-50%); }
    .hc-faq details[open] summary::before,
    .hc-faq details[open] summary::after { transform: translateY(-50%) rotate(135deg); }
    .hc-fa { padding: 0 0 16px; }
    .hc-fa p { margin: 0 0 8px; color: var(--text-dim); font-size: .92rem; line-height: 1.65; }
    .hc-fa ul { margin: 0 0 8px; padding-left: 20px; color: var(--text-dim); font-size: .92rem; line-height: 1.65; }
    .hc-fa code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: .86em; background: var(--surface-2); padding: 1px 5px; border-radius: 6px; }

    .hc-chips { display: flex; flex-wrap: wrap; gap: 8px; }
    .hc-chips .hc-chip { max-width: 300px; padding: 7px 14px; font-size: .85rem; }
    .hc-chips .hc-chip span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .hc-chips .hc-chip svg { width: 13px; height: 13px; }
    .hc-related { margin-top: 26px; padding-top: 18px; border-top: 1px solid var(--border); }
    .hc-related h2 { font-size: .9rem; font-weight: 650; letter-spacing: 0; color: var(--text-dim); margin: 0 0 12px; }

    .hc-pager { max-width: 860px; margin: 16px auto 0; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 12px; }
    @media (max-width: 640px) {
      .hc-pager { gap: 9px; }
      .hc-pager a { padding: 12px 13px; gap: 9px; }
      .hc-pager b { font-size: .84rem; }
      .hc-pager svg { width: 15px; height: 15px; }
    }
    .hc-pager a { display: flex; align-items: center; gap: 12px; padding: 14px 17px; color: var(--text); }
    .hc-pager a:hover { text-decoration: none; transform: translateY(-2px); border-color: color-mix(in srgb, var(--green) 45%, var(--border)); }
    .hc-pager a.next { justify-content: flex-end; text-align: right; }
    .hc-pager a.next svg { order: 2; }
    .hc-pager svg { flex: none; width: 17px; height: 17px; color: var(--text-dim); }
    .hc-pager small { display: block; font-size: .78rem; font-weight: 650; letter-spacing: 0; color: var(--text-dim); }
    .hc-pager a span { min-width: 0; flex: 1 1 auto; }
    .hc-pager b { display: block; font-size: .9rem; margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 100%; }

    .hc-cta {
      max-width: 860px; margin: 16px auto 20px; padding: 22px 26px; border-radius: var(--hc-r);
      display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap;
      background: var(--green-strong); color: #fff;
    }
    .hc-cta b { font-size: 1.02rem; }
    .hc-cta p { margin: 3px 0 0; font-size: .88rem; opacity: .92; }
    .hc-cta .btn { flex: none; background: #fff; color: var(--green-strong); border: 0; }
    .hc-cta .btn:hover { background: #f0fff7; transform: translateY(-1px); }
    .hc-cta svg { width: 16px; height: 16px; }

    /* floating "ask in bot" pill (TikTok's chat-with-us) */
    .hc-fab {
      position: fixed; right: 22px; bottom: 22px; z-index: 70;
      display: inline-flex; align-items: center; gap: 9px;
      background: var(--green); color: #fff; font-weight: 750; font-size: .92rem;
      border-radius: 999px; padding: 12px 19px;
      box-shadow: 0 10px 26px color-mix(in srgb, var(--green) 45%, transparent);
      transition: background .18s, box-shadow .22s, color .18s, opacity .3s, visibility 0s,
        transform .35s var(--ease-apple);
    }
    .hc-fab:hover { text-decoration: none; background: var(--green-strong); color: #fff; }
    .hc-fab svg { width: 17px; height: 17px; }
    @media (max-width: 560px) {
      .hc-fab span { display: none; }
      .hc-fab { padding: 13px; right: 16px; bottom: calc(16px + env(safe-area-inset-bottom)); }
    }
    @media (max-width: 640px) {
      /* keep clear of the Contents pill on the left */
      .hc-fab { right: 16px; bottom: calc(16px + env(safe-area-inset-bottom)); }
    }

    /* article reading progress */
    .hc-progress {
      position: fixed; top: var(--hc-head); left: 0; height: 3px; width: 0;
      background: var(--green);
      z-index: 60; border-radius: 0 3px 3px 0; pointer-events: none;
      transition: top .32s var(--ease-apple, ease), opacity .3s, visibility 0s;
    }
    /* the navbar slides away on scroll-down (nav-hide.js): pin the bar to
       the viewport top so it never floats over the article text */
    html.nav-hidden .hc-progress { top: 0; }

    /* ---------- 404 ---------- */
    .hc-404 { text-align: center; padding: 90px 0 110px; }
    .hc-404 .hc-ic { margin: 0 auto 18px; width: 60px; height: 60px; border-radius: 18px; }
    .hc-404 .hc-ic svg { width: 28px; height: 28px; }
    .hc-404 h1, .hc-404 h2 { margin: 0 0 8px; font-size: 1.8rem; }
    .hc-404 p { color: var(--text-dim); margin: 0 0 22px; }

    /* ---------- header density on small screens ---------- */
    @media (max-width: 900px) {
      .hc-hsearch { width: auto; flex: 1; min-width: 0; max-width: none; }
      .hc-hsearch kbd { display: none; }
      .hc-brand-help { display: none; }
    }
    /* Tablets keep a compact icon-only CTA; phones (<=640px) show the
       full Open Bot label next to the gear (main.css sizes it). */
    @media (min-width: 641px) and (max-width: 900px) {
      .nav-unified .nav-right .nav-cta span { display: none; }
      .nav-unified .nav-right .nav-cta { padding: 0 12px; }
    }

    @media (prefers-reduced-motion: reduce) {
      .view.anim { animation: none; }
      * { scroll-behavior: auto !important; }
    }
    html[data-motion="off"] .view.anim { animation: none; }
    html[data-motion="off"] .hc-sbtn { animation: none; }

    /* ================= Apple spring + liquid-glass motion ================= */
    :root { --ease-spring: cubic-bezier(.34,1.56,.64,1); --ease-apple: cubic-bezier(.32,.72,0,1); }
    html[data-motion="off"] *, html[data-motion="off"] *::before, html[data-motion="off"] *::after {
      animation-duration: .001s !important; animation-iteration-count: 1 !important;
      transition-duration: .001s !important; }
    html[data-motion="off"] { scroll-behavior: auto !important; }

    /* staggered entrance inside each rendered view */
    .view.anim .hc-side-title, .view.anim .hc-nav-item, .view.anim .hc-card,
    .view.anim .hc-cat, .view.anim .hc-art > *, .view.anim .hc-fa, .view.anim details {
      animation: hcRise .6s var(--ease-apple) both; }
    .view.anim .hc-nav-item:nth-child(1), .view.anim .hc-cat:nth-of-type(1), .view.anim .hc-art > *:nth-child(1) { animation-delay: .04s; }
    .view.anim .hc-nav-item:nth-child(2), .view.anim .hc-cat:nth-of-type(2), .view.anim .hc-art > *:nth-child(2) { animation-delay: .08s; }
    .view.anim .hc-nav-item:nth-child(3), .view.anim .hc-cat:nth-of-type(3), .view.anim .hc-art > *:nth-child(3) { animation-delay: .12s; }
    .view.anim .hc-nav-item:nth-child(4), .view.anim .hc-cat:nth-of-type(4), .view.anim .hc-art > *:nth-child(4) { animation-delay: .16s; }
    .view.anim .hc-nav-item:nth-child(5), .view.anim .hc-cat:nth-of-type(5), .view.anim .hc-art > *:nth-child(5) { animation-delay: .2s; }
    .view.anim .hc-nav-item:nth-child(6) { animation-delay: .24s; }
    .view.anim .hc-nav-item:nth-child(n+7) { animation-delay: .28s; }
    .view.anim .hc-art > *:nth-child(n+6) { animation-delay: .24s; }
    @keyframes hcRise { from { opacity: 0; transform: translateY(12px); } }

    /* liquid-glass search results popover (both inputs) */
    .hc-results {
      background: var(--surface);
      border: 1px solid var(--border);
      box-shadow: 0 12px 32px rgba(17, 24, 39, .14);
      transform-origin: top;
      animation: hcPopOpen .36s var(--ease-spring) both;
    }
    [data-theme="dark"] .hc-results {
      border-color: color-mix(in srgb, #ffffff 12%, var(--border) 88%);
      box-shadow: 0 26px 60px rgba(0, 0, 0, .55), inset 0 1px 0 rgba(255, 255, 255, .07); }
    @keyframes hcPopOpen { from { opacity: 0; transform: translateY(-8px) scale(.95); } }
    .hc-res { transition: background .18s, padding-left .3s var(--ease-spring); animation: hcRowIn .34s var(--ease-apple) both; }
    .hc-res:nth-child(1) { animation-delay: .04s; }
    .hc-res:nth-child(2) { animation-delay: .08s; }
    .hc-res:nth-child(3) { animation-delay: .12s; }
    .hc-res:nth-child(4) { animation-delay: .16s; }
    .hc-res:nth-child(5) { animation-delay: .2s; }
    .hc-res:nth-child(6) { animation-delay: .24s; }
    .hc-res:nth-child(n+7) { animation-delay: .28s; }
    @keyframes hcRowIn { from { opacity: 0; transform: translateY(-5px); } }
    .hc-res:hover, .hc-res.cur { padding-left: 21px; }
    .hc-res:active { transform: scale(.985); }

    /* header search input lifts on focus */
    .hc-hsearch input:focus { transform: translateY(-1px); }

    /* sidebar nav: hover nudge + active pill slide-in */
    .hc-nav-item { transition: background .2s, color .2s, transform .45s var(--ease-spring); }
    .hc-nav-item:hover { transform: translateX(3px); }
    .hc-nav-item.active { animation: hcPill .45s var(--ease-spring); }
    @keyframes hcPill { from { transform: scale(.97); } }

    /* hero chips staggered float-in */
    .hc-chiprow .hc-chip { animation: hcRise .55s var(--ease-apple) both; }
    .hc-chiprow .hc-chip:nth-child(1) { animation-delay: .05s; }
    .hc-chiprow .hc-chip:nth-child(2) { animation-delay: .1s; }
    .hc-chiprow .hc-chip:nth-child(3) { animation-delay: .15s; }
    .hc-chiprow .hc-chip:nth-child(4) { animation-delay: .2s; }
    .hc-chiprow .hc-chip:nth-child(5) { animation-delay: .25s; }
    .hc-chiprow .hc-chip:nth-child(6) { animation-delay: .3s; }
    .hc-chiprow .hc-chip:nth-child(n+7) { animation-delay: .35s; }
    .hc-chip { transition: border-color .18s, color .18s, transform .5s var(--ease-spring), box-shadow .2s; }
    .hc-chip:active { transform: scale(.95); }

    /* category cards: spring hover + press */
    .hc-card { transition: border-color .25s, box-shadow .3s; -webkit-tap-highlight-color: transparent; }
    /* only link-cards lift — the article itself is not interactive and must
       never move or gain hover depth under the cursor */
    a.hc-card:hover { box-shadow: var(--shadow); transform: translateY(-2px); }
    .hc-card { transition: border-color .25s, box-shadow .3s, transform .25s var(--ease-apple); }
    [data-theme="dark"] a.hc-card:hover { box-shadow: 0 1px 2px rgba(0,0,0,.5), 0 10px 26px rgba(0,0,0,.35); }
    @media (hover: none) {
      .hc-card:active { transform: scale(.985); transition: transform .12s; }
      /* the article card never shrinks on tap: pressing any link inside it made
         the whole page visibly go small then big on navigation */
      .hc-art:active { transform: none; transition: none; }
    }
    a.hc-card:hover .hc-ic { transform: rotate(-6deg) scale(1.08); }
    .hc-ic { transition: transform .5s var(--ease-spring); }

    /* mobile drawer: springy slide + scrim. ONLY at drawer widths — under
       1021px this used to leak into desktop and overwrite the sidebar's
       margin-left collapse transition (T/O key: no animation). */
    @media (max-width: 1020px) {
      .hc-side { transition: transform .44s var(--ease-spring); }
      .hc-scrim { transition: opacity .3s var(--ease-apple); }
      body:not(.hc-side-open) .hc-side { transition: transform .3s var(--ease-apple); }
    }

    /* FAB press feedback: gentle color/shadow lift only — no movement,
       the overshooting spring curve made the button visibly jump */
    .hc-fab { transition: background .18s, box-shadow .22s, color .18s; }
    .hc-fab:active { box-shadow: 0 6px 16px color-mix(in srgb, var(--green) 40%, transparent); }
    .hc-faq details { transition: transform .3s var(--ease-apple); }
    .hc-faq details[open] { transform: none; }
    .hc-faq summary { transition: color .18s; }
    .hc-faq summary:hover { color: var(--green-strong); }

    /* keyboard hint on the S button */

    @media (prefers-reduced-motion: reduce) {
      .view.anim .hc-side-title, .view.anim .hc-nav-item, .view.anim .hc-card,
      .view.anim .hc-cat, .view.anim .hc-art > *, .view.anim .hc-fa, .view.anim details,
      .hc-chiprow .hc-chip, .hc-sbtn { animation: none; }
      .hc-results, .hc-res, .hc-nav-item, .hc-card, .hc-chip, .hc-fab { transition: none; animation: none; }
    }


    h3[id], details[id] { scroll-margin-top: calc(var(--hc-head) + 14px); }

    /* ================= docs redesign: calm professional system ================= */
    .hc-shell { column-gap: 0; }

    /* ---- sidebar as a true docs tree ---- */
    .hc-side { width: 266px; padding: 20px 10px 48px; font-size: .9rem; }
    .hc-side-title { font-size: .95rem; font-weight: 800; letter-spacing: -.01em;
      color: var(--text); padding: 2px 12px 12px; }
    .hc-side-title svg { width: 15px; height: 15px; }
    .hc-nav-item { padding: 7px 10px; font-size: .88rem; font-weight: 650; border-radius: 8px; }
    .hc-nav-item svg { width: 16px; height: 16px; }
    .hc-nav-item.active { background: color-mix(in srgb, var(--green) 13%, transparent); }
    .hc-subnav a { padding: 5px 10px 5px 36px; font-size: .83rem; border-left: 2px solid transparent;
      border-radius: 0 8px 8px 0; margin-left: 10px; }
    .hc-subnav a:hover { border-left-color: color-mix(in srgb, var(--green) 40%, transparent); }
    .hc-subnav a.active { border-left-color: var(--green); background: color-mix(in srgb, var(--green) 9%, transparent); }
    .hc-side-cta { margin: 16px 8px 0; }

    /* ---- content + right rail grid ---- */
    .hc-content { --hc-gut: clamp(20px, 3.5vw, 44px); }
    .hc-doc { display: grid; grid-template-columns: minmax(0, 1fr) 228px; gap: clamp(28px, 4vw, 56px);
      align-items: start; }
    .hc-doc > article { min-width: 0; }
    .hc-rail { position: sticky; top: calc(var(--hc-head) + 28px); max-height: calc(100vh - var(--hc-head) - 56px);
      overflow-y: auto; scrollbar-width: thin; font-size: .83rem; padding-bottom: 24px; }
    .hc-rail-t { font-weight: 800; font-size: .92rem; letter-spacing: -.01em;
      color: var(--text); margin: 4px 0 10px; }
    .hc-rail nav { display: flex; flex-direction: column; gap: 1px; border-left: 2px solid var(--border); }
    .hc-rail a { display: block; padding: 4px 0 4px 14px; margin-left: -2px; border-left: 2px solid transparent;
      color: var(--text-dim); line-height: 1.45; }
    .hc-rail a:hover { color: var(--green-strong); text-decoration: none; }
    .hc-rail a.on { color: var(--green-strong); font-weight: 700; border-left-color: var(--green); }
    .hc-rail .hc-rail-rel { margin-top: 14px; }
    .hc-rail .hc-rail-rel span { display: block; font-weight: 800; font-size: .88rem; letter-spacing: -.01em;
      color: var(--text); margin-bottom: 6px; }
    @media (max-width: 1279px) { .hc-doc { grid-template-columns: minmax(0, 1fr); } .hc-rail { display: none; } }

    /* ---- docs home: brand-green hero band (greeting + search + chips),
       category cards with descriptions, support CTA ---- */
    .hc-docs-head {
      position: relative; overflow: hidden; text-align: center;
      margin: 26px 0 0; padding: clamp(46px, 6vw, 78px) 24px clamp(42px, 5vw, 66px);
      border-radius: 26px; color: #fff;
      background:
        radial-gradient(1000px 300px at 88% -30%, rgba(255,255,255,.17), transparent 60%),
        radial-gradient(820px 300px at 6% 118%, rgba(0,0,0,.20), transparent 55%),
        linear-gradient(135deg, #0a5c31 0%, #12934e 55%, #1faa59 100%);
      border: 1px solid color-mix(in srgb, #0a5c31 55%, transparent);
    }
    [data-theme="dark"] .hc-docs-head {
      background:
        radial-gradient(1000px 300px at 88% -30%, rgba(255,255,255,.10), transparent 60%),
        radial-gradient(820px 300px at 6% 118%, rgba(0,0,0,.38), transparent 55%),
        linear-gradient(135deg, #062d1a 0%, #0a5230 60%, #0d7340 100%);
      border-color: color-mix(in srgb, #1faa59 32%, transparent);
    }
    .hc-docs-head .hc-kicker { color: #fff; background: rgba(255,255,255,.13); border-color: rgba(255,255,255,.30); }
    .hc-docs-head h1 { margin: 18px 0 0; font-size: clamp(2rem, 4.6vw, 2.9rem); letter-spacing: -.03em;
      line-height: 1.08; font-weight: 800; color: #fff; }
    .hc-docs-head h1 .grad { color: #fff; background: linear-gradient(transparent 62%, rgba(255,255,255,.38) 62%); }
    .hc-docs-head .hc-title { font-family: var(--font-display); text-transform: uppercase;
      font-size: clamp(2.7rem, 8vw, 4.7rem); font-weight: 800; letter-spacing: -.045em; line-height: .94;
      margin: 16px 0 0; }
    .hc-docs-head .hc-sub { margin: 14px auto 0; font-size: 1.02rem; color: rgba(255,255,255,.84); max-width: 60ch; }
    .hc-docs-head .hc-search { margin: 26px auto 0; max-width: 640px; }
    .hc-docs-head .hc-try { margin-top: 20px; }
    .hc-docs-head .hc-try-label { color: rgba(255,255,255,.72); }
    .hc-docs-head .hc-chip { background: rgba(255,255,255,.12); border-color: rgba(255,255,255,.26); color: #fff; }
    .hc-docs-head .hc-chip svg { color: #fff; }
    .hc-docs-head .hc-chip:hover { background: rgba(255,255,255,.22); border-color: rgba(255,255,255,.55); color: #fff; }
    .hc-docs-head .hc-pop { justify-content: center; margin: 18px 0 0; color: rgba(255,255,255,.78); }
    .hc-docs-head .hc-pop b { color: #fff; }
    .hc-docs-head .hc-pop a { color: #fff; background: rgba(255,255,255,.10); border-color: rgba(255,255,255,.26); }
    .hc-docs-head .hc-pop a:hover { background: rgba(255,255,255,.20); border-color: rgba(255,255,255,.55); color: #fff; }
    /* Phones: the hero is a full-bleed green band — no floating card, no
       rounded corners — and the ask-chips become one clean left-aligned
       column instead of a ragged wrap. */
    @media (max-width: 760px) {
      .hc-docs-head {
        margin: 0 -18px; border-radius: 0; border-left: 0; border-right: 0;
        padding: 28px 18px 30px;
      }
      .hc-docs-head .hc-kicker { font-size: .74rem; padding: 5px 12px; }
      .hc-docs-head .hc-title { font-size: clamp(2.3rem, 11vw, 3rem); margin-top: 14px; }
      .hc-docs-head .hc-sub { margin-top: 12px; font-size: .95rem; line-height: 1.55; max-width: 44ch; }
      .hc-docs-head .hc-search { margin-top: 20px; }
      .hc-docs-head .hc-try { margin-top: 18px; }
      .hc-docs-head .hc-try-label { font-size: .8rem; }
      .hc-docs-head .hc-chiprow { flex-direction: column; gap: 8px; justify-content: stretch; margin-top: 10px; }
      .hc-docs-head .hc-chip { width: 100%; justify-content: flex-start; text-align: left;
        border-radius: 14px; padding: 12px 14px; font-size: .87rem; line-height: 1.35; }
      .hc-docs-head .hc-chip svg { width: 16px; height: 16px; }
      .hc-docs-head .hc-pop { margin-top: 16px; }
    }
    .hc-pop { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 10px; margin: 20px 0 6px;
      font-size: .87rem; color: var(--text-dim); }
    .hc-pop b { font-weight: 750; color: var(--text); }
    .hc-pop a { color: var(--green-strong); font-weight: 600; padding: 4px 10px; border-radius: 999px;
      border: 1px solid var(--border); background: var(--surface); white-space: nowrap; }
    .hc-pop a:hover { border-color: var(--green); text-decoration: none; }
    .hc-section-h { display: flex; align-items: baseline; gap: 12px; margin: 34px 0 4px; }
    .hc-section-h h2 { margin: 0; font-size: 1.15rem; letter-spacing: -.01em; }
    .hc-section-h span { color: var(--text-dim); font-size: .86rem; }
    .hc-grid { grid-template-columns: repeat(3, 1fr); }
    @media (max-width: 1020px) { .hc-grid { grid-template-columns: 1fr 1fr; } }
    @media (max-width: 640px) { .hc-grid { grid-template-columns: 1fr 1fr; gap: 10px; }
      /* Phones keep two cards per row: halves the scroll through 20+ topics. Cards tighten up and the article preview hides (one tap away). */
      .hc-grid > .hc-cat { padding: 14px; }
      .hc-grid .hc-cat-head { gap: 9px; }
      .hc-grid .hc-cat-go { display: none; }
      .hc-grid .hc-cat-prev { display: none; } }
    .hc-cat { display: flex; flex-direction: column; gap: 10px; padding: 20px; text-decoration: none; }
    .hc-grid > .hc-cat { padding: 22px; gap: 8px; border-radius: 20px; }
    .hc-grid > .hc-cat .hc-ic { width: 54px; height: 54px; border-radius: 16px; margin-bottom: 2px; }
    .hc-grid > .hc-cat .hc-ic svg { width: 27px; height: 27px; }
    .hc-grid > .hc-cat .hc-cat-t { font-size: 1.06rem; }
    .hc-cat:hover { text-decoration: none; border-color: color-mix(in srgb, var(--green) 45%, var(--border)); transform: translateY(-2px); box-shadow: var(--shadow); }
    .hc-cat-head { display: flex; align-items: center; gap: 12px; }
    .hc-ic { display: inline-flex; align-items: center; justify-content: center; flex: none;
      width: 40px; height: 40px; border-radius: 12px; color: var(--green-strong);
      background: color-mix(in srgb, var(--green) 12%, transparent); }
    .hc-ic svg { width: 20px; height: 20px; }
    .hc-cat-t { display: block; font-weight: 750; font-size: .98rem; color: var(--text); }
    .hc-cat-c { display: block; font-size: .8rem; color: var(--text-dim); font-weight: 600; margin-top: 2px; }
    .hc-cat-go { margin-left: auto; color: var(--text-dim); }
    .hc-cat-go svg { width: 16px; height: 16px; }
    .hc-cat:hover .hc-cat-go { color: var(--green-strong); }
    .hc-cat-prev { border-top: 1px dashed var(--border); padding-top: 10px; }

    /* ---- article page: flat docs typography ---- */
    .hc-art { background: none; border: 0; box-shadow: none; border-radius: 0;
      max-width: 780px; margin: 0; padding: 0; }
    .hc-crumbs { padding: 24px 0 0; font-size: .82rem; }
    .hc-art > h1, .hc-art > h2 { font-size: clamp(1.7rem, 3.4vw, 2.3rem); margin: 12px 0 6px; }
    .hc-art-meta { color: var(--text-dim); font-size: .87rem; margin: 0 0 18px; display: flex; gap: 8px;
      align-items: center; flex-wrap: wrap; }
    .hc-art-meta .dot::before { content: "·"; margin-right: 8px; }
    .hc-body { font-size: 1.0rem; }
    .hc-body p, .hc-body li { line-height: 1.72; }
    .hc-body p { margin: 0 0 14px; }
    .hc-body ul { margin: 0 0 16px; padding-left: 22px; display: flex; flex-direction: column; gap: 7px; }
    .hc-body li::marker { color: var(--green-strong); }
    .hc-body a { text-decoration: underline; text-underline-offset: 3px; text-decoration-thickness: 1px;
      text-decoration-color: color-mix(in srgb, var(--green-strong) 55%, transparent); }
    .hc-body a:hover { text-decoration-color: var(--green-strong); }
    .hc-body h2, .hc-body h3 { letter-spacing: -.015em; line-height: 1.3; margin: 30px 0 10px; }
    .hc-body h2 { font-size: 1.28rem; }
    .hc-body h3 { font-size: 1.08rem; }
    .hc-body code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: .86em;
      background: var(--surface-2); border: 1px solid var(--border); padding: 1px 6px; border-radius: 6px; }
    .hc-body pre { background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
      padding: 14px 16px; overflow-x: auto; font-size: .85rem; line-height: 1.6; }
    .hc-body table { border-collapse: collapse; width: 100%; font-size: .9rem; margin: 0 0 18px; }
    .hc-body th, .hc-body td { border: 1px solid var(--border); padding: 8px 12px; text-align: left; }
    .hc-body th { background: var(--surface-2); font-weight: 750; }
    .hc-body img { max-width: 100%; border-radius: 12px; border: 1px solid var(--border); }

    /* ---- faq / related / pager / cta ---- */
    .hc-faq { margin-top: 30px; }
    .hc-faq > h2 { font-size: 1.02rem; font-weight: 800; letter-spacing: -.01em; }
    .hc-faq details { border: 1px solid var(--border); border-radius: 12px; padding: 0 16px; margin-bottom: 8px; }
    .hc-faq details[open] { border-color: color-mix(in srgb, var(--green) 40%, var(--border)); }
    .hc-faq summary { padding: 13px 0; font-weight: 700; font-size: .95rem; cursor: pointer; list-style: none; }
    .hc-faq summary::-webkit-details-marker { display: none; }
    .hc-faq summary { position: relative; padding-right: 28px; }
    .hc-faq summary::before, .hc-faq summary::after {
      content: ""; position: absolute; top: 50%; background: var(--green-strong);
      border-radius: 2px; transition: transform .25s var(--ease-spring, ease);
    }
    .hc-faq summary::before { right: 1px; width: 14px; height: 2px; transform: translateY(-50%); }
    .hc-faq summary::after { right: 7px; width: 2px; height: 14px; transform: translateY(-50%); }
    .hc-faq details[open] summary::before,
    .hc-faq details[open] summary::after { transform: translateY(-50%) rotate(135deg); }
    .hc-fa { padding: 0 0 16px; color: var(--text); }
    .hc-fa p, .hc-fa li { line-height: 1.7; }
    .hc-related { margin-top: 26px; }
    .hc-related > h2 { font-size: 1.02rem; font-weight: 800; letter-spacing: -.01em;
      color: var(--text); margin: 0 0 10px; }
    .hc-pager { max-width: 780px; margin: 30px 0 0; }
    .hc-pager a { border-radius: 14px; background: var(--surface); }
    .hc-pager small { display: block; font-size: .82rem; font-weight: 700; letter-spacing: 0;
      color: var(--text-dim); margin-bottom: 3px; }
    .hc-pager b { font-size: .95rem; }
    .hc-cta { max-width: 780px; border-radius: 16px; margin-top: 26px; }


    /* ---- category / list / search ---- */
    .hc-cat-head { display: flex; gap: 14px; align-items: center; margin: 14px 0 4px; }
    .hc-cat-head h1, .hc-cat-head h2 { margin: 0; font-size: clamp(1.6rem, 3.2vw, 2.1rem); letter-spacing: -.02em; }
    .hc-cat-head p { margin: 4px 0 0; color: var(--text-dim); }
    .hc-intro { max-width: 780px; color: var(--text); }
    .hc-intro p { line-height: 1.7; }
    .hc-list { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 16px; max-width: 960px; }
    @media (min-width: 1400px) { .hc-list { grid-template-columns: 1fr 1fr 1fr; } }
    @media (max-width: 760px) { .hc-list { grid-template-columns: 1fr; } }
    .hc-row { display: flex; align-items: center; gap: 12px; padding: 13px 16px; border: 1px solid var(--border);
      border-radius: 12px; background: var(--surface); }
    .hc-row:hover { border-color: color-mix(in srgb, var(--green) 45%, var(--border)); text-decoration: none; }
    .hc-row-t { font-weight: 650; color: var(--text); }
    .hc-row-m { margin-left: auto; flex: none; font-size: .8rem; color: var(--text-dim); font-weight: 650; }
    /* Search/suggestion cards: the nowrap category badge used to squeeze
       the title down to one word per line in narrow grid columns. The title
       now takes its own full-width line; badge + chevron share a row beneath it. */
    .hc-list > .hc-row { flex-wrap: wrap; row-gap: 8px; }
    .hc-list .hc-row-t { flex: 1 1 100%; }
    .hc-list .hc-row-m { margin-left: 0; }
    .hc-list > .hc-row > svg { margin-left: auto; width: 15px; height: 15px; flex: none; color: var(--text-dim); }
    .hc-others { margin-top: 26px; font-size: .88rem; color: var(--text-dim); display: flex; flex-wrap: wrap; gap: 6px 12px; }
    .hc-others a { font-weight: 600; }

    /* ---- static .doc pages share the type system ---- */
    .doc { font-size: 1.0rem; }
    .doc h1 { letter-spacing: -.025em; line-height: 1.15; }
    .doc p, .doc li { line-height: 1.72; }
    .doc a { text-decoration: underline; text-underline-offset: 3px;
      text-decoration-color: color-mix(in srgb, var(--green-strong) 55%, transparent); }
    .doc-layout { display: grid; grid-template-columns: minmax(0, 1fr) 228px; gap: clamp(28px, 4vw, 56px);
      align-items: start; }
    @media (max-width: 1279px) { .doc-layout { grid-template-columns: minmax(0, 1fr); } .doc-layout .hc-rail { display: none; } }

    @media (max-width: 760px) {
      .hc-side { width: min(320px, 88vw); }
      .hc-doc { grid-template-columns: minmax(0, 1fr); }
      .hc-rail { display: none; }
      .hc-docs-head h1 { font-size: 1.9rem; }
      .hc-pager { grid-template-columns: minmax(0, 1fr); }
      /* Phone-width code samples wrap instead of hiding half the line behind a
         horizontal swipe — the batch format is the content, not decoration. */
      .hc-body pre { font-size: .8rem; white-space: pre-wrap; overflow-wrap: anywhere; }
    }

    /* ---- pro docs layer ---- */
    .hc-side-title span { color: var(--green-strong); font-size: .95rem; }
    .hc-grp { margin: 16px 8px 5px; font-size: .86rem; font-weight: 800; letter-spacing: -.01em; color: var(--text); }
    .hc-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 22px 0 0; }
    .hc-toolbar .hc-crumbs { padding: 0; flex: 1; min-width: 0; }
    .hc-tools { position: relative; display: flex; align-items: center; gap: 6px; flex: none; }
    .hc-tool { display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 9px; border: 1px solid transparent; background: var(--surface-2); color: var(--text-dim); cursor: pointer; }
    .hc-tool:hover { border-color: var(--border); color: var(--text); background: var(--surface); }
    .hc-tool.on { color: var(--green-strong); border-color: var(--green); }
    .hc-tool svg { width: 16px; height: 16px; }
    html[data-hcfont="s"] .hc-body { font-size: .88rem; }
    html[data-hcfont="l"] .hc-body { font-size: 1.22rem; }
    html[data-hcfont="l"] .hc-art > h1, html[data-hcfont="l"] .hc-art > h2 { font-size: clamp(1.9rem, 3.6vw, 2.5rem); }

    html[data-hcfont="s"] .hc-body { font-size: .94rem; }
    html[data-hcfont="l"] .hc-body { font-size: 1.12rem; }
    html.hc-wide .hc-doc { grid-template-columns: minmax(0,1fr); }
    html.hc-wide .hc-rail { display: none; }
    html.hc-wide .hc-art, html.hc-wide .hc-pager, html.hc-wide .hc-cta { max-width: 960px; }
    html.rail-off .hc-doc { grid-template-columns: minmax(0,1fr); }
    html.rail-off .hc-rail { display: none; }
    .hc-feat { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 26px 0 6px; }
    .hc-feat a { display: flex; flex-direction: column; gap: 8px; padding: 18px; border-radius: 16px; background: var(--surface); border: 1px solid var(--border); text-decoration: none; }
    .hc-feat a:hover { border-color: var(--green); text-decoration: none; }
    .hc-feat .hc-ic { width: 38px; height: 38px; }
    .hc-feat b { color: var(--text); font-size: .93rem; }
    .hc-feat span.s { color: var(--text-dim); font-size: .82rem; line-height: 1.45; }
    .hc-band { margin: 30px 0 8px; border-radius: 22px; padding: 28px; color: #fff;
      background:
        radial-gradient(700px 220px at 90% -20%, rgba(255,255,255,.14), transparent 60%),
        linear-gradient(135deg, #07331d 0%, #0b6b38 60%, #12934e 100%);
      border: 1px solid color-mix(in srgb, #1faa59 30%, transparent); }
    .hc-band h2 { margin: 0 0 4px; color: #fff; font-size: 1.3rem; }
    .hc-band p.sub { margin: 0 0 18px; color: rgba(255,255,255,.72); font-size: .9rem; }
    .hc-band-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
    .hc-band-grid a { display: block; padding: 16px 18px; border-radius: 14px; text-decoration: none; background: #f2f0e8; color: #12312f; }
    .hc-band-grid a:hover { text-decoration: none; }
    .hc-band-grid b { display: block; font-size: .94rem; }
    .hc-band-grid span { display: block; margin-top: 3px; font-size: .8rem; color: rgba(18,49,47,.68); }
    @media (max-width: 1020px) { .hc-feat { grid-template-columns: 1fr 1fr; } .hc-band-grid { grid-template-columns: 1fr 1fr; } }
    /* Phones keep two cards per row for the featured topics and the platform band. */
    @media (max-width: 640px) { .hc-feat { grid-template-columns: 1fr 1fr; gap: 10px; } .hc-feat a { padding: 14px; } .hc-band-grid { grid-template-columns: 1fr 1fr; gap: 10px; } .hc-band-grid a { padding: 14px; } .hc-tools .hc-tool.opt { display: none; } }

    .gp-reading[hidden] { display: none !important; }
    /* mobile: no room for layout toggles — font size only */
    @media (max-width: 1020px) {
      #settingsMenu [data-rail-toggle] { display: none !important; }
    }
    .gp-row.gp-fonts { cursor: default; }
    .hc-fonts { display: inline-flex; align-items: baseline; gap: 2px; margin-left: auto; }
    .hc-fonts button { font: inherit; background: none; border: 0; cursor: pointer; color: var(--text-dim);
      padding: 3px 8px; border-radius: 8px; font-weight: 800; line-height: 1; }
    .hc-fonts button:hover { color: var(--green-strong); }
    .hc-fonts button.on { color: #fff; background: var(--green-strong); }
    .hc-fonts button:nth-child(1) { font-size: .78rem; }
    .hc-fonts button:nth-child(2) { font-size: .95rem; }
    .hc-fonts button:nth-child(3) { font-size: 1.12rem; }
    .hc-more { display: inline-flex; align-items: center; gap: 8px; margin: 6px 0 0; font: inherit;
      font-size: .88rem; font-weight: 700; color: var(--green-strong); background: var(--surface);
      border: 1px solid var(--border); border-radius: 10px; padding: 9px 18px; cursor: pointer; }
    /* docked to the right end: inside chips/others rows it rides beside the
       last item (vertically centered); inside article lists it right-aligns
       under the rows (the rows are full-width links, so the button gets its
       own right-aligned row). */
    .hc-chips.has-more, .hc-others.has-more { align-items: center; }
    .hc-chips > .hc-more, .hc-others > .hc-more { margin: 0 0 0 auto; align-self: center; flex: none; }
    [data-list].has-more { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 16px; }
    @media (max-width: 760px) { [data-list].has-more { grid-template-columns: 1fr; } }
    [data-list] > .hc-more { grid-column: 1 / -1; justify-self: center; margin: 14px 0 0; }
    .hc-more:hover { border-color: var(--green); }
    .hc-more[hidden] { display: none; }
    .hc-list.is-collapsed .hc-row:nth-child(n+7) { display: none; }
    .hc-others.is-collapsed a:nth-child(n+7) { display: none; }
    .hc-chips.is-collapsed .hc-chip:nth-child(n+4) { display: none; }
    .hc-list.is-expanded .hc-row:nth-child(n+7) { animation: hcMoreIn .35s cubic-bezier(.22,.61,.36,1) both; }
    .hc-others.is-expanded a:nth-child(n+7), .hc-chips.is-expanded .hc-chip:nth-child(n+4) { animation: hcMoreIn .35s cubic-bezier(.22,.61,.36,1) both; }
    @keyframes hcMoreIn { from { opacity: 0; transform: translateY(8px); } }
    /* in-flow fade blocks: the way back in glides too */
    .hc-cta, .hc-pager, .hc-rail {
      transition: opacity .3s var(--ease-apple), display .3s allow-discrete, visibility 0s; }
    /* ---- fullscreen focus mode: chrome hides WITH animation ----
       The navbar slides up (same transform + negative-margin trick as
       scroll-hide, so the article glides up to fill the space); floating
       bits fade; in-flow blocks fade, then release space via display
       allow-discrete (older browsers fall back to the old instant hide).
       The search field lives inside the header, so it rides along. The
       shell stays flex so the collapsing sidebar glides (as when the
       sidebar is closed normally) instead of jumping. */
    html.hc-fs header.site { transform: translateY(-100%); margin-bottom: calc(-1 * var(--nav-h, 65px)); }
    html.hc-fs .hc-progress, html.hc-fs .hc-fab, html.hc-fs .hc-rail, html.hc-fs .hc-side-reveal {
      opacity: 0; visibility: hidden; pointer-events: none;
      transition: opacity .3s var(--ease-apple), transform .35s var(--ease-apple), visibility 0s .4s; }
    html.hc-fs .hc-fab, html.hc-fs .hc-rail, html.hc-fs .hc-side-reveal { transform: translateY(10px); }
    /* Focus mode hides the footer and CTA only. The previous/next pager
       stays on screen so readers can keep moving through the help center. */
    html.hc-fs footer.site, html.hc-fs .hc-cta, html.hc-fs .hc-rail {
      display: none; opacity: 0; visibility: hidden;
      transition: opacity .3s var(--ease-apple), display 0s .35s allow-discrete, visibility 0s .35s; }
    html.hc-fs .hc-side { display: none; opacity: 0; visibility: hidden; pointer-events: none;
      transition: opacity .3s var(--ease-apple), display 0s .45s allow-discrete, visibility 0s .45s; }
    @media (min-width: 1021px) {
      html.hc-fs .hc-side { margin-left: -284px; }
    }
    /* OS-level reduced motion: instant hide (the navbar is already covered
       by the shared reduced-motion block; this covers the fs fades). */
    @media (prefers-reduced-motion: reduce) {
      html.hc-fs .hc-progress, html.hc-fs .hc-fab, html.hc-fs .hc-rail,
      html.hc-fs .hc-side-reveal, html.hc-fs footer.site, html.hc-fs .hc-cta,
      html.hc-fs .hc-side,
      .hc-cta, .hc-pager, .hc-rail, .hc-progress, .hc-fab,
      .hc-side-reveal { transition: none !important; }
    }
    html.hc-fs .hc-content { max-width: 920px; margin: 0 auto; padding: 0 clamp(20px, 4vw, 44px) 90px; }
    html.hc-fs .hc-doc { grid-template-columns: minmax(0, 1fr); }
    html.hc-fs .hc-art { max-width: none; }
    html.hc-fs .hc-tool[data-fs-btn] { color: var(--green-strong); border-color: var(--green); }

    /* ---- liquid-glass section reel: floating prev/current/next ---- */
    .hc-reel { position: fixed; left: 50%; bottom: calc(18px + env(safe-area-inset-bottom)); z-index: 90;
      transform: translateX(-50%) translateY(24px); width: min(340px, calc(100vw - 32px));
      border-radius: 18px; padding: 10px 16px 12px; opacity: 0; pointer-events: none;
      transition: opacity .3s, transform .3s cubic-bezier(.22,.61,.36,1);
      background: linear-gradient(135deg, color-mix(in srgb, var(--surface) 62%, transparent), color-mix(in srgb, var(--surface-2) 45%, transparent));
      -webkit-backdrop-filter: blur(18px) saturate(1.4); backdrop-filter: blur(18px) saturate(1.4);
      border: 1px solid color-mix(in srgb, #fff 22%, var(--border));
      box-shadow: 0 12px 40px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.18); overflow: hidden; }
    .hc-reel.show { opacity: 1; pointer-events: auto; transform: translateX(-50%); }
    .hc-reel::after { content: ''; position: absolute; inset: 0; pointer-events: none;
      background: linear-gradient(105deg, transparent 30%, rgba(255,255,255,.14) 45%, transparent 60%);
      transform: translateX(-110%); animation: reelSheen 7s ease-in-out infinite; }
    @keyframes reelSheen { 0%, 72% { transform: translateX(-110%); } 88%, 100% { transform: translateX(110%); } }
    .hc-reel button { display: block; width: 100%; background: none; border: 0; padding: 0; font: inherit;
      color: var(--text-dim); cursor: pointer; text-align: center; }
    .hc-reel button span { display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .hc-reel [data-reel-prev] span, .hc-reel [data-reel-next] span { font-size: .74rem; font-weight: 600; opacity: .75; }
    .hc-reel [data-reel-cur] { margin: 2px 0; }
    .hc-reel [data-reel-cur] span { font-size: 1rem; font-weight: 800; letter-spacing: -.01em; color: var(--text); }
    .hc-reel.swap [data-reel-cur] span { animation: reelSwap .32s cubic-bezier(.22,.61,.36,1) both; }
    @keyframes reelSwap { 0% { opacity: 0; transform: translateY(10px) scale(.94); } 60% { opacity: 1; transform: translateY(-1px) scale(1.02); } 100% { opacity: 1; transform: none; } }
    html[data-motion="off"] .hc-reel::after, html[data-motion="off"] .hc-reel.swap [data-reel-cur] span { animation: none; }

    @media print {
      header.site, footer.site, .hc-cta, .hc-pager, .hc-search, .hc-crumbs, .hc-side, .hc-fab, .hc-progress, .hc-hsearch { display: none !important; }
      .view[hidden] { display: block !important; }
      .hc-card { border: 0; box-shadow: none; background: none; }
    }
'''


# ------------------------------------------------------------------- JS ----
JS = r'''
(function () {
  'use strict';
  var DATA = [];
  try { DATA = window.__HELP_DATA || []; } catch (e) {}
  var SIDE = [];
  try { SIDE = window.__HELP_SIDE || []; } catch (e) {}
  var CATS = {};
  SIDE.forEach(function (c) { CATS[c.id] = c.title; });
  var byId = {};
  DATA.forEach(function (s) { byId[s.id] = s; });
  /* AI intent per article: category id doubles as the intent tag the mini
     engine matches queries against (schedule, media, payment, ...) */
  if (window.HelpAI) {
    var CAT_INTENT = { scheduling: 'schedule', recurring: 'schedule', timezone: 'schedule',
      media: 'media', media_storage: 'media', channels: 'channel', bots: 'bot',
      premium: 'payment', payment: 'payment', backup: 'backup', export: 'backup', import: 'backup',
      statistics: 'stats', errors: 'error', faq: 'error', start: 'account', getting_started: 'account',
      feedback: 'feedback', formatting: 'formatting', tips: 'formatting', limits: 'limits',
      tools: 'schedule', language: 'formatting', misc: 'error', legal: 'payment', commands: 'schedule' };
    DATA.forEach(function (s) { s.intent = CAT_INTENT[s.c] || ''; });
  }
  /* one shared interpreter for the AI "you mean" line */
  function aiLabel(q) {
    if (!window.HelpAI) return '';
    var ex = window.HelpAI.interpret(q);
    return ex.label || '';
  }

  var views = Array.prototype.slice.call(document.querySelectorAll('.view'));
  var sideNav = document.getElementById('hcSideNav');
  var progressBar = document.getElementById('hcProgress');
  var norm = function (s) { return (s || '').toLowerCase(); };

  /* ---------------- router ---------------- */
  function parseHash() {
    var h = location.hash || '', m;
    if ((m = h.match(/^#\/a\/([\w-]+)/)))  return { view: 'article',  id: m[1] };
    if ((m = h.match(/^#\/c\/([\w-]+)/)))  return { view: 'category', id: m[1] };
    if ((m = h.match(/^#\/s\/(.+)$/)))      return { view: 'search',   id: decodeURIComponent(m[1].replace(/\+/g, ' ')) };
    if ((m = h.match(/^#help-([\w-]+)/)))  return { view: 'article',  id: m[1], legacy: true };
    if ((m = h.match(/^#cat-([\w-]+)/)))   return { view: 'category', id: m[1], legacy: true };
    return { view: 'home' };
  }

  function currentTitle(r) {
    if (r.view === 'article' && byId[r.id]) return byId[r.id].t;
    if (r.view === 'category' && CATS[r.id]) return CATS[r.id];
    if (r.view === 'search') return 'Search: ' + r.id;
    return '';
  }

  function activeCatId(r) {
    if (r.view === 'category') return r.id;
    if (r.view === 'article' && byId[r.id]) return byId[r.id].c;
    return null;
  }

  function updateSidebar(r) {
    if (!sideNav) return;
    var cat = activeCatId(r);
    Array.prototype.forEach.call(sideNav.querySelectorAll('[data-cat]'), function (a) {
      var on = a.getAttribute('data-cat') === cat;
      a.classList.toggle('active', on);
      var sub = document.getElementById('hc-sub-' + a.getAttribute('data-cat'));
      if (sub) sub.classList.toggle('open', on);
    });
    var home = document.getElementById('hcSideHome');
    if (home) home.classList.toggle('active', r.view === 'home');
    var art = (r.view === 'article') ? r.id : null;
    Array.prototype.forEach.call(sideNav.querySelectorAll('[data-art]'), function (a) {
      a.classList.toggle('active', !!art && a.getAttribute('data-art') === art);
    });
  }

  function navigate() {
    var r = parseHash();
    /* Articles and categories are real pages now. Old hash links (bookmarks,
       search results from before the clean-URL move) redirect instead of
       rendering a second copy of the article inside the hub. */
    if (r.view === 'article' && byId[r.id]) { location.replace('a/' + r.id + '/'); return; }
    if (r.view === 'category' && CATS[r.id]) { location.replace('c/' + r.id + '/'); return; }
    if (r.legacy) {
      var valid = (r.view === 'article' && byId[r.id]) || (r.view === 'category' && CATS[r.id]);
      if (valid) { history.replaceState(null, '', (r.view === 'article' ? '#/a/' : '#/c/') + r.id); }
      else { r = { view: '404' }; }
    }
    if (r.view === 'article' && !byId[r.id]) r = { view: '404' };
    if (r.view === 'category' && !CATS[r.id]) r = { view: '404' };
    if (r.view === 'search') r.id = String(r.id || '').slice(0, 200);

    var sel = '.view[data-view="home"]';
    if (r.view === 'article')  sel = '.view[data-view="article"][data-art="' + r.id + '"]';
    if (r.view === 'category') sel = '.view[data-view="category"][data-cat="' + r.id + '"]';
    if (r.view === 'search')   sel = '.view[data-view="search"]';
    if (r.view === '404')      sel = '.view[data-view="404"]';
    var el = document.querySelector(sel);
    if (!el) { sel = '.view[data-view="404"]'; el = document.querySelector(sel); }

    views.forEach(function (v) { v.hidden = v !== el; });
    if (el) {
      el.classList.remove('anim');
      void el.offsetWidth; /* restart the entrance animation */
      el.classList.add('anim');
    }
    var t = currentTitle(r);
    document.title = r.view === 'search' ? (t + hcTitleSuffix()) :
      (t ? (t + hcTitleSuffix()) : hcT('Help Center — Fast Scheduler for Telegram'));
    try {
      var d = (r.view === 'article' && byId[r.id] && byId[r.id].d) || '';
      var md = document.querySelector('meta[name="description"]');
      var mo = document.querySelector('meta[property="og:title"]');
      var mod = document.querySelector('meta[property="og:description"]');
      if (d && md) md.setAttribute('content', d);
      if (t && mo) mo.setAttribute('content', t + ' — Fast Scheduler Help');
      if (d && mod) mod.setAttribute('content', d);
    } catch (e) {}
    window.scrollTo(0, 0);
    closeAllResults();
    updateSidebar(r);
    document.body.classList.toggle('hc-onhome', r.view === 'home');
    var onArt = r.view === 'article';
    document.body.classList.toggle('hc-onarticle', onArt);
    Array.prototype.forEach.call(document.querySelectorAll('[data-reading]'), function (el) { el.hidden = !onArt; });
    if (!onArt && window.__hcExitFs && document.documentElement.classList.contains('hc-fs')) window.__hcExitFs();
    if (onArt && window.__hcSetupMore) window.__hcSetupMore();
    try { document.dispatchEvent(new CustomEvent('viewchange', { detail: { view: r.view, id: r.id } })); } catch (e) {}
    /* setTimeout, not requestAnimationFrame: rAF can be throttled to never
       inside embedded webviews, which left the search page permanently blank */
    if (r.view === 'search') setTimeout(function () { renderSearchPage(r.id); }, 0);
    document.body.classList.remove('hc-side-open');
    updateProgress();
    if (el) {
      var h1 = el.querySelector('h1, h2');
      if (h1) { h1.setAttribute('tabindex', '-1'); h1.focus({ preventScroll: true }); }
    }
  }

  /* ---------------- docs rail + feedback ---------------- */
  function markRail(scope, key) {
    if (!scope) return;
    var rail = scope.querySelector('[data-rail]');
    if (!rail) return;
    Array.prototype.forEach.call(rail.querySelectorAll('a'), function (a) {
      a.classList.toggle('on', a.getAttribute('data-rk') === key);
    });
  }
  document.addEventListener('click', function (ev) {
    if (!ev.target.closest) return;
    var j = ev.target.closest('[data-jid]');
    if (j) {
      var sec = document.getElementById(j.getAttribute('data-jid'));
      if (sec) {
        ev.preventDefault();
        sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
        markRail(j.closest('section.view'), j.getAttribute('data-jid'));
      }
      return;
    }
    var fq = ev.target.closest('[data-faq-open]');
    if (fq) {
      var d = document.getElementById(fq.getAttribute('data-faq-open'));
      if (d) {
        ev.preventDefault();
        d.open = true;
        d.scrollIntoView({ behavior: 'smooth', block: 'start' });
        markRail(fq.closest('section.view'), fq.getAttribute('data-faq-open'));
      }
      return;
    }
  });
  function initRail() {
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (e.isIntersecting) markRail(e.target.closest('section.view'), e.target.id);
        });
      }, { rootMargin: '-25% 0px -65% 0px' });
      Array.prototype.forEach.call(
        document.querySelectorAll('section.view h3[id], section.view details[id]'),
        function (s) { io.observe(s); });
    }
  }
  (function () {
    var root = document.documentElement;
    function store(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
    function load(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
    function paintReader() {
      var wide = load('fs-help-wide') === 'on';
      var railOff = load('fs-rail') === 'off';
      var font = load('fs-font') || load('fs-help-font');
      var fs = load('fs-help-fs') === 'on';
      root.classList.toggle('hc-wide', wide);
      root.classList.toggle('rail-off', railOff);
      root.classList.toggle('hc-fs', fs);
      if (wide || fs) root.classList.add('hc-collapsed');
      else if (load('fs-help-side') !== 'closed') root.classList.remove('hc-collapsed');
      if (font) { root.setAttribute('data-font', font); root.setAttribute('data-hcfont', font); } else { root.removeAttribute('data-font'); root.removeAttribute('data-hcfont'); }
      var q = function (sel, fn) { Array.prototype.forEach.call(document.querySelectorAll(sel), fn); };
      q('[data-wide-toggle]', function (b) { b.setAttribute('aria-pressed', wide ? 'true' : 'false'); });
      q('[data-rail-toggle]', function (b) { b.setAttribute('aria-pressed', railOff ? 'false' : 'true'); });
      q('[data-fonts]', function (box) { Array.prototype.forEach.call(box.querySelectorAll('button'), function (b) { b.classList.toggle('on', (font || 'm') === b.getAttribute('data-font')); }); });
      q('[data-fs-btn]', function (b) { b.classList.toggle('on', fs); });
      if (window.__hcReelPaint) { try { window.__hcReelPaint(); } catch (e) {} }
    }
    function exitFs() { store('fs-help-fs', 'off'); paintReader(); }
    document.addEventListener('click', function (ev) {
      if (!ev.target.closest) return;
      var w = ev.target.closest('[data-wide-toggle]');
      if (w) { store('fs-help-wide', w.getAttribute('aria-pressed') !== 'true' ? 'on' : 'off'); paintReader(); return; }
      var r = ev.target.closest('[data-rail-toggle]');
      if (r) { store('fs-rail', r.getAttribute('aria-pressed') === 'true' ? 'off' : 'on'); paintReader(); return; }
      var f = ev.target.closest('[data-fonts] button');
      if (f) { var fv = f.getAttribute('data-font'); store('fs-font', fv); store('fs-help-font', fv); try { window.dispatchEvent(new CustomEvent('fs-font-change', { detail: { font: fv } })); } catch (e2) {} paintReader(); return; }
      var fb2 = ev.target.closest('[data-fs-btn]');
      if (fb2) { store('fs-help-fs', load('fs-help-fs') === 'on' ? 'off' : 'on'); paintReader(); return; }
      var mb = ev.target.closest('[data-more]');
      if (mb) {
        var box = mb.closest('[data-list],[data-others],[data-chips-more]') || mb.previousElementSibling;
        var collapsed = box && box.classList.contains('is-collapsed');
        if (box) { box.classList.toggle('is-collapsed', !collapsed); box.classList.toggle('is-expanded', !!collapsed); }
        var mt = mb.querySelector('[data-more-t]'), lt = mb.querySelector('[data-less-t]');
        if (mt) mt.hidden = !!collapsed;
        if (lt) lt.hidden = !collapsed;
      }
    });
    document.addEventListener('keydown', function (ev) {
      if ((ev.key === 'Escape' || ev.key === 'Esc') && load('fs-help-fs') === 'on') exitFs();
    });
    /* show-more setup: lists with more than N items start collapsed */
    function setupMore(scopeSel, itemSel, keep) {
      Array.prototype.forEach.call(document.querySelectorAll(scopeSel), function (box) {
        var items = box.querySelectorAll(itemSel);
        var btn = box.querySelector(':scope > [data-more]') || box.nextElementSibling;
        if (items.length > keep && btn && btn.hasAttribute('data-more')) {
          box.classList.add('is-collapsed');
          box.classList.add('has-more');
          if (btn.parentElement !== box) box.appendChild(btn);
          btn.hidden = false;
        } else if (btn && btn.hasAttribute('data-more')) {
          btn.hidden = true;
        }
      });
    }
    window.__hcSetupMore = function () {
      setupMore('[data-list]', '.hc-row', 6);
      setupMore('[data-others]', 'a', 5);
      setupMore('[data-chips-more]', '.hc-chip', 3);
    };
    window.__hcExitFs = exitFs;
    window.addEventListener('fs-font-change', function () { paintReader(); });
    window.__hcPaintReader = paintReader;
    try {
      if (load('fs-rail') === 'off') root.classList.add('rail-off');
      if (load('fs-help-wide') === 'on' || load('fs-help-fs') === 'on') root.classList.add('hc-collapsed');
    } catch (e) {}
    paintReader();
    window.__hcSetupMore();
  })();
  initRail();
  /* lang-aware chrome labels: write the final language synchronously so
     freshly injected nodes never flash EN before the RU observer runs. */
  function hcT(en) {
    try {
      if (window.FS_LANG && FS_LANG.get() === 'ru') {
        var m = (FS_LANG.RU_MAP || {})[en];
        if (m) return m;
        if (window.FS_RU_CHROME && FS_RU_CHROME.MAP && FS_RU_CHROME.MAP[en]) return FS_RU_CHROME.MAP[en];
      }
    } catch (e) {}
    return en;
  }
  function hcRuCount(n, q) {
    try {
      if (window.FS_LANG && FS_LANG.get() === 'ru') {
        var w = 'результатов';
        var m10 = n % 10, h10 = n % 100;
        if (m10 === 1 && h10 !== 11) w = 'результат';
        else if (m10 >= 2 && m10 <= 4 && (h10 < 12 || h10 > 14)) w = 'результата';
        return n + ' ' + w + ' по запросу \u201c' + q + '\u201d';
      }
    } catch (e) {}
    return null;
  }
  /* "See all N results" footer under the dropdown (Wise-style). Numbers
     can't travel through the RU dictionary, so branch like hcRuCount. */
  function hcSeeAll(n) {
    try {
      if (window.FS_LANG && FS_LANG.get() === 'ru') {
        var w = 'результат', m10 = n % 10, h10 = n % 100;
        if (m10 >= 2 && m10 <= 4 && (h10 < 12 || h10 > 14)) w = 'результата';
        else if (m10 !== 1 || h10 === 11) w = 'результатов';
        return 'Показать все ' + n + ' ' + w;
      }
    } catch (e) {}
    return 'See all ' + n + ' result' + (n === 1 ? '' : 's');
  }
  /* document.title on the RU hub: brand suffix + search prefix branch
     on FS_LANG like hcSeeAll (composite strings can't use the dict). */
  function hcTitleSuffix() {
    try { if (window.FS_LANG && FS_LANG.get() === 'ru') return ' — Справка Fast Scheduler'; } catch (e) {}
    return ' — Fast Scheduler Help';
  }
  function hcSearchPrefix() {
    try { if (window.FS_LANG && FS_LANG.get() === 'ru') return 'Поиск: '; } catch (e) {}
    return 'Search: ';
  }
  window.__hcDyn = window.__hcDyn || [];
  function hcTrack(n, en) {
    try {
      var arr = window.__hcDyn;
      for (var i = 0; i < arr.length; i++) { if (arr[i].n === n) { arr[i].en = en; return; } }
      arr.push({ n: n, en: en });
    } catch (e) {}
  }
  function hcTranslateNow(root) {
    try {
      if (!(window.FS_LANG && FS_LANG.get() === 'ru')) return;
      var map = FS_LANG.RU_MAP || {};
      var dict = (window.FS_RU_CHROME && FS_RU_CHROME.MAP) || {};
      var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
      var batch = [], tn;
      while ((tn = w.nextNode())) batch.push(tn);
      batch.forEach(function (n) {
        try {
          var p = n.parentNode;
          if (!p || (p.closest && p.closest('.fs-lang-seg'))) return;
          var tag = (p.tagName || '').toLowerCase();
          if (tag === 'script' || tag === 'style' || tag === 'code' || tag === 'pre' || tag === 'textarea') return;
          var t = n.nodeValue.trim();
          if (!t) return;
          var m = map[t] || dict[t];
          if (m && n.nodeValue.indexOf(m) === -1) {
            hcTrack(n, n.nodeValue);
            var lead = (n.nodeValue.match(/^\s*/) || [''])[0];
            var trail = (n.nodeValue.match(/\s*$/) || [''])[0];
            n.nodeValue = lead + m + trail;
          }
        } catch (e2) {}
      });
    } catch (e) {}
  }
  window.addEventListener('fs-lang-change', function (e) {
    /* RU->EN: restore synchronously translated dynamic nodes; EN->RU: the
       debounced observer plus hcTranslateNow on next render covers it. */
    try {
      var lang = (e && e.detail && e.detail.lang) || (window.FS_LANG && FS_LANG.get());
      if (lang === 'ru') return;
      var arr = window.__hcDyn || [];
      window.__hcDyn = [];
      arr.forEach(function (rec) { try { rec.n.nodeValue = rec.en; } catch (x) {} });
      /* re-render visible search UI so composite strings (counts) flip now */
      ['hcSearch', 'hcSearchH'].forEach(function (id) {
        var inp = document.getElementById(id);
        if (inp && inp.value && inp.offsetParent !== null) {
          try { inp.dispatchEvent(new Event('input', { bubbles: true })); } catch (x) {}
        }
      });
      if (window.__hcReelPaint) { try { window.__hcReelPaint(); } catch (x) {} }
    } catch (x) {}
  });
  /* floating liquid-glass section reel: prev / current / next */
  (function () {
    var reel = document.querySelector('[data-reel]');
    if (!reel) return;
    var bPrev = reel.querySelector('[data-reel-prev]');
    var bCur = reel.querySelector('[data-reel-cur]');
    var bNext = reel.querySelector('[data-reel-next]');
    var curKey = null, ticking = false;
    function railLinks() {
      var v = document.querySelector('section.view:not([hidden])');
      var nav = v && v.querySelector('[data-rail]');
      return nav ? Array.prototype.slice.call(nav.querySelectorAll('a')) : [];
    }
    function railGone() {
      if (document.documentElement.classList.contains('hc-fs')) return true;
      try { return window.matchMedia('(max-width: 1279px)').matches; } catch (e) { return true; }
    }
    function setLabel(btn, link) {
      btn.querySelector('span').textContent = link ? link.textContent.trim() : '';
      btn._rk = link ? link.getAttribute('data-rk') : null;
    }
    function jump(btn) {
      var el = btn._rk && document.getElementById(btn._rk);
      if (!el) return;
      if (el.tagName === 'DETAILS') el.open = true;
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    function paint() {
      var links = railLinks();
      var idx = -1;
      links.forEach(function (a, i) { if (a.classList.contains('on')) idx = i; });
      var sc = window.scrollY || document.documentElement.scrollTop || 0;
      var show = links.length >= 2 && sc > 480 && railGone();
      reel.hidden = !show;
      reel.setAttribute('aria-hidden', show ? 'false' : 'true');
      if (reel.classList.contains('show') !== show) reel.classList.toggle('show', show);
      if (!show) { curKey = null; return; }
      if (idx === -1) idx = 0;
      var key = links[idx].getAttribute('data-rk');
      if (key === curKey) return;
      curKey = key;
      setLabel(bPrev, links[idx - 1]);
      setLabel(bCur, links[idx]);
      setLabel(bNext, links[idx + 1]);
      bPrev.style.visibility = links[idx - 1] ? 'visible' : 'hidden';
      bNext.style.visibility = links[idx + 1] ? 'visible' : 'hidden';
      reel.classList.remove('swap');
      void reel.offsetWidth;
      reel.classList.add('swap');
    }
    bPrev.addEventListener('click', function () { jump(bPrev); });
    bCur.addEventListener('click', function () { jump(bCur); });
    bNext.addEventListener('click', function () { jump(bNext); });
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      var raf = window.requestAnimationFrame || function (cb) { setTimeout(cb, 100); };
      raf(function () { ticking = false; paint(); });
    }, { passive: true });
    document.addEventListener('viewchange', function () { curKey = null; paint(); });
    window.__hcReelPaint = function () { curKey = null; paint(); };
    window.addEventListener('fs-lang-change', function () { curKey = null; paint(); });
    window.addEventListener('fs-lang-applied', function () { curKey = null; paint(); });
    paint();
  })();
  window.addEventListener('hashchange', navigate);
  navigate();

  /* ---------------- sidebar ---------------- */
  function buildSidebar() {
    if (!sideNav) return;
    var html = '<a class="hc-nav-item" id="hcSideHome" href="#/">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 11l9-8 9 8M5 10v10h14V10"/></svg>' +
      '<span>Help Center home</span></a>';
    var GRPS = [{t:'Getting started',ids:['start','scheduling','channels','bots']},{t:'Plans & growth',ids:['admins','premium','referral','limits']},{t:'Setup',ids:['timezone','language','export','import','backup','media_storage']},{t:'Help & reference',ids:['tools','tips','feedback','faq','commands','errors']},{t:'About',ids:['privacy','legal','contact','config']}];
    var byCat = {};
    SIDE.forEach(function (cc) { byCat[cc.id] = cc; });
    var emitted = {};
    function navRow(c) {
      html += '<a class="hc-nav-item" data-cat="' + c.id + '" href="c/' + c.id + '/">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + c.icon + '</svg>' +
        '<span>' + c.title + '</span><span class="n">' + c.n + '</span></a>';
      if (c.kids && c.kids.length) {
        html += '<div class="hc-subnav" id="hc-sub-' + c.id + '"><div class="hc-subnav-in">';
        c.kids.forEach(function (k) { html += '<a href="a/' + k.id + '/" data-art="' + k.id + '">' + k.t + '</a>'; });
        html += '</div></div>';
      }
    }
    GRPS.forEach(function (g) {
      var items = [];
      g.ids.forEach(function (id) { if (byCat[id]) items.push(byCat[id]); });
      if (!items.length) return;
      html += '<div class="hc-grp">' + g.t + '</div>';
      items.forEach(function (c) { emitted[c.id] = 1; navRow(c); });
    });
    SIDE.forEach(function (c) {
      if (emitted[c.id]) return;
      html += '<a class="hc-nav-item" data-cat="' + c.id + '" href="c/' + c.id + '/">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + c.icon + '</svg>' +
        '<span>' + c.title + '</span><span class="n">' + c.n + '</span></a>';
      if (c.kids && c.kids.length) {
        html += '<div class="hc-subnav" id="hc-sub-' + c.id + '"><div class="hc-subnav-in">';
        c.kids.forEach(function (k) { html += '<a href="a/' + k.id + '/" data-art="' + k.id + '">' + k.t + '</a>'; });
        html += '</div></div>';
      }
    });
    sideNav.innerHTML = html;
    sideNav.addEventListener('click', function () { document.body.classList.remove('hc-side-open'); });
  }
  buildSidebar();

  var scrim = document.getElementById('hcScrim');
  var menuBtn = document.getElementById('hcMenuBtn');
  if (menuBtn) menuBtn.addEventListener('click', function () { document.body.classList.toggle('hc-side-open'); });
  if (scrim) scrim.addEventListener('click', function () { document.body.classList.remove('hc-side-open'); });

  /* ---------------- mini-AI natural-language search ----------------
     Understands everyday phrasing: strips filler words, expands synonyms
     ("can't post" -> not posted / sending), tolerates typos on long words,
     and ranks by how much of the question each article actually answers. */
  var STOP = {};
  'the a an and or of to for in on with your you my it is are be can how what when why do does i we they this that at as by from get make if not no want need about'.split(' ').forEach(function (w) { STOP[w] = 1; });
  var SYN = [
    ['sender', 'bot', 'bots', 'own bot', 'custom bot', 'botfather', 'token', 'newbot'],
    ['schedule', 'scheduled', 'scheduling', 'queue', 'queued', 'post later'],
    ['recurring', 'repeat', 'repeating', 'regular', 'auto repost'],
    ['timezone', 'time zone', 'time zones', 'utc', 'gmt'],
    ['delete', 'remove', 'cleanup', 'clean up'],
    ['edit', 'change', 'modify', 'update'],
    ['premium', 'pro', 'paid', 'subscription', 'upgrade'],
    ['limit', 'limits', 'cap', 'quota'],
    ['media', 'photo', 'photos', 'video', 'videos', 'image', 'images', 'album', 'albums', 'gif', 'gifs', 'sticker', 'stickers', 'voice', 'document', 'documents', 'file', 'files', 'poll', 'polls', 'quiz', 'quizzes'],
    ['storage', 'box', 'boxes', 'library', 'media storage'],
    ['channel', 'channels'],
    ['payment', 'pay', 'buy', 'purchase', 'stars', 'invoice', 'refund', 'refunds', 'crypto', 'price', 'pricing', 'cost'],
    ['backup', 'export', 'import', 'restore', 'fsback', 'fspback', 'migrate', 'migration', 'transfer', 'move'],
    ['admin', 'administrators', 'permission', 'permissions', 'rights'],
    ['signature', 'signatures', 'footer'],
    ['language', 'lang', 'english', 'russian', 'translation'],
    ['search', 'find', 'look up'],
    ['calendar', 'month view'],
    ['stats', 'statistics', 'usage', 'counter'],
    ['error', 'errors', 'problem', 'problems', 'issue', 'not working', 'fails', 'failed', 'stuck', 'fix', 'troubleshoot', 'troubleshooting'],
    ['late', 'delay', 'delayed', 'not posted', 'missing', 'skipped'],
    ['referral', 'invite', 'friends', 'bonus', 'promo', 'promocode', 'coupon', 'free days'],
    ['account', 'start', 'begin', 'setup', 'set up', 'onboarding', 'getting started', 'connect'],
    ['cancel', 'stop', 'pause'],
    ['post', 'posts', 'posting', 'publish', 'publishing', 'send', 'sending', 'message', 'messages'],
    ['feedback', 'support', 'contact', 'ticket'],
    ['auto', 'automatically', 'automatic', 'autopilot']
  ];
  function synth(w) {
    for (var i = 0; i < SYN.length; i++) if (SYN[i].indexOf(w) !== -1) return SYN[i];
    return [w];
  }
  function expand(q) {
    var words = q.split(/\s+/).filter(Boolean);
    var sets = [], all = [], key = [];
    words.forEach(function (w) {
      if (STOP[w]) return;
      key.push(w);
      var s = synth(w);
      sets.push(s);
      s.forEach(function (x) { if (all.indexOf(x) === -1) all.push(x); });
    });
    return { words: key, sets: sets, all: all };
  }
  function fuzzyPrefix(word, target) {
    var n = Math.max(4, word.length - 2);
    return target.slice(0, n) === word.slice(0, n);
  }
  function score(sec, q, ex) {
    var t = norm(sec.t), b = norm(sec.b), f = norm(sec.f);
    var s = 0;
    if (q.length > 2) {
      if (b.indexOf(q) !== -1 || f.indexOf(q) !== -1 || t.indexOf(q) !== -1) {
        s += 60;
        if (t.indexOf(q) !== -1) s += 60;
        if (f.indexOf(q) !== -1) s += 10;
      }
    }
    var titleWords = t.split(/\s+/);
    var bodyWords = (t + ' ' + b + ' ' + f).split(/\s+/);
    var matched = 0;
    ex.words.forEach(function (w) {
      var set = [w];
      for (var i = 0; i < ex.sets.length; i++) if (ex.sets[i][0] === w) { set = ex.sets[i]; break; }
      var wordScore = 0;
      titleWords.forEach(function (x) {
        if (x === w) wordScore = Math.max(wordScore, 120);
        else if (x.indexOf(w) === 0) wordScore = Math.max(wordScore, 55);
        else if (x.indexOf(w) !== -1) wordScore = Math.max(wordScore, 34);
        else if (w.length >= 5 && fuzzyPrefix(w, x)) wordScore = Math.max(wordScore, 20);
      });
      if (!wordScore && set.length > 1) {
        set.forEach(function (syn) {
          if (b.indexOf(syn) !== -1 || f.indexOf(syn) !== -1) wordScore = Math.max(wordScore, 15);
          titleWords.forEach(function (x) {
            if (x.indexOf(syn) === 0) wordScore = Math.max(wordScore, 24);
          });
        });
      }
      if (!wordScore && bodyWords.indexOf(w) !== -1) wordScore = 12;
      if (!wordScore && bodyWords.some(function (x) { return x.indexOf(w) === 0; })) wordScore = 22;
      if (wordScore > 0) { s += wordScore; matched++; }
      else s -= 45;
    });
    if (ex.words.length > 1 && matched === ex.words.length) s += 25;
    return s;
  }

  /* SECURITY: entity-encode (never strip) so no raw <, >, &, " or ' can
     reach an innerHTML sink. */
  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  /* Mark matches of q in RAW text: every literal segment is escaped, only
     the fixed <mark> tags are inserted as markup - safe by construction. */
  function markText(raw, q) {
    if (!q) return escapeHtml(raw);
    var out = '', low = String(raw).toLowerCase(), i = 0, idx;
    while ((idx = low.indexOf(q, i)) !== -1) {
      out += escapeHtml(raw.slice(i, idx)) + '<mark>' + escapeHtml(raw.slice(idx, idx + q.length)) + '</mark>';
      i = idx + q.length;
    }
    return out + escapeHtml(raw.slice(i));
  }

    function snippet(b, q) {
    var i = norm(b).indexOf(q);
    if (i === -1) return b.slice(0, 120);
    var start = Math.max(0, i - 42);
    var s = b.slice(start, start + 130);
    return (start > 0 ? '\u2026' : '') + s + (start + 130 < b.length ? '\u2026' : '');
  }

  function attachSearch(input, results) {
    if (!input || !results) return;
    var curIdx = -1;
    var resButtons = [];

    function close() {
      results.hidden = true; results.innerHTML = '';
      resButtons = []; curIdx = -1;
      input.setAttribute('aria-expanded', 'false');
    }
    function moveCursor(delta) {
      if (!resButtons.length) return;
      curIdx = (curIdx + delta + resButtons.length) % resButtons.length;
      resButtons.forEach(function (b, i) { b.classList.toggle('cur', i === curIdx); });
      resButtons[curIdx].scrollIntoView({ block: 'nearest' });
    }
    function render(q, ex, scored, total) {
      var html = '';
      /* "You mean" is an empty-state aid only — when there are results, the
         Best result card speaks for itself. */
      var top = scored[0], rest = scored.slice(1);
      /* a section split only makes sense when one result clearly dominates */
      var isClear = top.s >= 150 && (!rest.length || top.s >= rest[0].s + 50);
      if (isClear) {
        html += '<div class="hc-res-sec">' + hcT('Best result') + '</div>';
        html += '<button type="button" class="hc-res hc-res-best" role="option" data-art="' + top.sec.id + '">' +
          '<span class="hc-res-top"><span class="hc-res-t">' + markText(top.sec.t, q) + '</span>' +
          '<span class="hc-res-cat">' + escapeHtml(CATS[top.sec.c] || '') + '</span></span>' +
          '<p class="hc-res-s">' + markText(snippet(top.sec.b, q), q) + '</p></button>';
        if (rest.length) {
          html += '<div class="hc-res-sec">' + hcT('More results') + '</div>';
          rest.forEach(function (x) {
            var s = x.sec;
            html += '<button type="button" class="hc-res" role="option" data-art="' + s.id + '">' +
              '<span class="hc-res-top"><span class="hc-res-t">' + markText(s.t, q) + '</span>' +
              '<span class="hc-res-cat">' + escapeHtml(CATS[s.c] || '') + '</span></span>' +
              '<p class="hc-res-s">' + markText(snippet(s.b, q), q) + '</p></button>';
          });
        }
      } else {
        scored.forEach(function (x) {
          var s = x.sec;
          html += '<button type="button" class="hc-res" role="option" data-art="' + s.id + '">' +
            '<span class="hc-res-top"><span class="hc-res-t">' + markText(s.t, q) + '</span>' +
            '<span class="hc-res-cat">' + escapeHtml(CATS[s.c] || '') + '</span></span>' +
            '<p class="hc-res-s">' + markText(snippet(s.b, q), q) + '</p></button>';
        });
      }
      html += '<a class="hc-res-all" href="#/s/' + encodeURIComponent(q) + '">' +
        hcSeeAll(total) + ' ' + CHEV_SVG + '</a>';
      results.innerHTML = html;
      hcTranslateNow(results);
      results.hidden = false;
      input.setAttribute('aria-expanded', 'true');
      resButtons = Array.prototype.slice.call(results.querySelectorAll('.hc-res'));
      curIdx = 0;
      if (resButtons[0]) resButtons[0].classList.add('cur');
    }
    function renderEmpty(q, ex) {
      var ai = aiLabel(q);
      var aiHtml = ai ? '<div class="hc-ai-line"><span class="hc-ai-dot"></span>' + hcT('You mean:') + ' <b>' + escapeHtml(ai) + '</b></div>' : '';
      var sug = DATA.filter(function (sec) {
        var t = norm(sec.t);
        return ex.all.some(function (w) {
          return w.length > 2 && (t.indexOf(w) !== -1 || t.split(/\s+/).some(function (x) { return x.indexOf(w) === 0; }));
        });
      }).slice(0, 4);
      var html = '<div class="hc-empty-ill">' + ILL_SVG + '</div>' +
        '<div class="hc-empty-q">&ldquo;' + escapeHtml(q) + '&rdquo;</div>' +
        '<div class="hc-empty-t">' + hcT('No results found.') + '</div>' +
        '<div class="hc-empty-s">' + hcT('Try different or more general keywords.') + '</div>';
      if (aiHtml) html += aiHtml;
      if (sug.length) {
        html += '<div class="hc-sug-h">' + hcT('Maybe you meant:') + '</div>';
        sug.forEach(function (sg) {
          html += '<button type="button" class="hc-res" role="option" data-art="' + sg.id + '">' +
            '<span class="hc-res-top"><span class="hc-res-t">' + escapeHtml(sg.t) + '</span>' +
            '<span class="hc-res-cat">' + escapeHtml(CATS[sg.c] || '') + '</span></span></button>';
        });
      }
      html += '<div class="hc-sug-h">' + hcT('Still stuck?') + ' <a href="__BOTURL__" target="_blank" rel="noopener noreferrer">' + hcT('Ask in the bot') + '</a> ' + hcT('\u2014 a human answers every ticket.') + '</div>';
      results.innerHTML = html;
      hcTranslateNow(results);
      results.hidden = false;
      resButtons = Array.prototype.slice.call(results.querySelectorAll('.hc-res'));
      curIdx = resButtons.length ? 0 : -1;
      if (resButtons[0]) resButtons[0].classList.add('cur');
      input.setAttribute('aria-expanded', 'true');
    }
    function run() {
      var q = norm(input.value.trim());
      if (q.length < 2) { close(); return; }
      var ex = expand(q);
      var ranked;
      if (window.HelpAI) {
        ranked = window.HelpAI.scoreAll(q, DATA).map(function (x) { return { sec: x.doc, s: x.score }; });
        DATA.forEach(function (sec) {
          if (ranked.some(function (r) { return r.sec === sec; })) return;
          var s2 = score(sec, q, ex);
          if (s2 > 0) ranked.push({ sec: sec, s: s2 });
        });
        ranked.sort(function (a, b) { return b.s - a.s; });
      } else {
        ranked = DATA.map(function (sec) { return { sec: sec, s: score(sec, q, ex) }; })
          .filter(function (x) { return x.s > 0; })
          .sort(function (a, b) { return b.s - a.s; });
      }
      /* relevance floor: a single word that appears in every article
         ("post") must not make the whole help center a "result" */
      if (ranked.length) {
        var floor = Math.max(30, ranked[0].s * 0.5);
        ranked = ranked.filter(function (x) { return x.s >= floor; });
      }
      var scored = ranked.slice(0, 6);
      if (!scored.length) renderEmpty(q, ex); else render(q, ex, scored, ranked.length);
    }

    var timer = null;
    input.addEventListener('input', function () {
      clearTimeout(timer);
      timer = setTimeout(run, 130);
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); moveCursor(1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); moveCursor(-1); }
      else if (e.key === 'Enter') {
        e.preventDefault();
        var qraw = input.value.trim();
        if (qraw.length >= 2) {
          var dest = '#/s/' + encodeURIComponent(qraw);
          if (location.hash === dest) renderSearchPage(qraw); else location.hash = dest;
        }
      } else if (e.key === 'Escape') {
        input.value = ''; close(); input.blur();
      }
    });
    results.addEventListener('click', function (e) {
      var b = e.target.closest('.hc-res');
      if (b) location.href = 'a/' + b.getAttribute('data-art') + '/';
    });
    document.addEventListener('click', function (e) {
      var box = input.closest('.hc-search, .hc-hsearch');
      if (box && !(e.target.closest && box.contains(e.target))) close();
    });
  }

  var heroInput = document.getElementById('hcSearch');
  var heroResults = document.getElementById('hcResults');
  var headInput = document.getElementById('hcSearchH');
  var headResults = document.getElementById('hcResultsH');
  attachSearch(heroInput, heroResults);
  attachSearch(headInput, headResults);

  function closeAllResults() {
    if (heroResults) { heroResults.hidden = true; }
    if (headResults) { headResults.hidden = true; }
  }

  /* ---------------- full search results page (#/s/<query>) ---------------- */
  var searchList = document.getElementById('hcSearchList');
  var searchEmpty = document.getElementById('hcSearchEmpty');
  var searchQEl = document.getElementById('hcSearchQ');
  var searchMeta = document.getElementById('hcSearchMeta');
  var searchSug = document.getElementById('hcSearchSug');
  var CHEV_SVG = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9 18 15 12 9 6"/></svg>';
  var ILL_SVG = '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/><circle cx="10.5" cy="14" r="2.6"/><line x1="12.4" y1="15.9" x2="14.5" y2="18"/></svg>';

  function docHref(sec) { return sec.href ? sec.href : ('help/a/' + sec.id + '.html'); }
  function resultRow(sec, q) {
    return '<a class="hc-row" href="' + docHref(sec) + '"><span class="hc-row-t">' +
      markText(sec.t, q) + '</span><span class="hc-row-m">' +
      escapeHtml(CATS[sec.c] || '') + '</span>' + CHEV_SVG + '</a>';
  }

  function suggestionsFor(ex, cap) {
    var sug = DATA.filter(function (sec) {
      var t = norm(sec.t);
      return ex.all.some(function (w) {
        return w.length > 2 && (t.indexOf(w) !== -1 || t.split(/\s+/).some(function (x) { return x.indexOf(w) === 0; }));
      });
    }).slice(0, cap);
    if (!sug.length) sug = DATA.slice(0, cap);
    return sug.map(function (sg) {
      return '<a class="hc-row" href="a/' + sg.id + '/"><span class="hc-row-t">' +
        escapeHtml(sg.t) + '</span><span class="hc-row-m">' + escapeHtml(CATS[sg.c] || '') +
        '</span>' + CHEV_SVG + '</a>';
    }).join('');
  }

  var searchCat = 'all';
  function renderSearchFilters(hits, q) {
    var el = document.getElementById('hcSearchFilters');
    if (!el) return;
    var present = {};
    hits.forEach(function (x) { present[x.sec.c] = true; });
    var order = Object.keys(present).sort();
    if (order.length < 2) { el.hidden = true; el.innerHTML = ''; return; }
    el.hidden = false;
    var html = '<button type="button" class="hc-fchip' + (searchCat === 'all' ? ' on' : '') +
      '" data-fcat="all">All</button>';
    order.forEach(function (cid) {
      html += '<button type="button" class="hc-fchip' + (searchCat === cid ? ' on' : '') +
        '" data-fcat="' + escapeHtml(cid) + '">' + escapeHtml(CATS[cid] || cid) + '</button>';
    });
    el.innerHTML = html;
    hcTranslateNow(el);
    el.querySelectorAll('.hc-fchip').forEach(function (b) {
      b.addEventListener('click', function () {
        searchCat = b.getAttribute('data-fcat');
        renderSearchPage(q);
      });
    });
  }

  function renderSearchPage(q) {
    if (!searchList || !DATA || !STOP) return;
    q = String(q || '').trim().slice(0, 200);
    if (window.__blogSearchQ !== q) { window.__blogSearchQ = q; searchCat = 'all'; }
    if (searchQEl) searchQEl.textContent = q;
    if (headInput) headInput.value = q;
    document.title = hcSearchPrefix() + q + hcTitleSuffix();
    var ex = expand(norm(q));
    var hits;
    if (window.HelpAI) {
      hits = window.HelpAI.scoreAll(q, DATA).map(function (x) { return { sec: x.doc, s: x.score }; });
      DATA.forEach(function (sec) {
        if (hits.some(function (r) { return r.sec === sec; })) return;
        var s = score(sec, norm(q), ex);
        if (s > 0) hits.push({ sec: sec, s: s });
      });
      hits.sort(function (a, b) { return b.s - a.s; });
    } else {
      hits = DATA.map(function (sec) { return { sec: sec, s: score(sec, norm(q), ex) }; })
        .filter(function (x) { return x.s > 0; })
        .sort(function (a, b) { return b.s - a.s; });
    }
    if (hits.length) {
      var hfloor = Math.max(30, hits[0].s * 0.5);
      hits = hits.filter(function (x) { return x.s >= hfloor; });
    }
    hits = hits.slice(0, 40);
    renderSearchFilters(hits, q);
    if (searchMeta) searchMeta.textContent = hits.length
      ? (hcRuCount(hits.length, q) || (hits.length + ' result' + (hits.length > 1 ? 's' : '') + ' for “' + q + '”'))
      : hcT('0 results');
    if (hits.length) {
      if (searchEmpty) searchEmpty.hidden = true;
      searchList.hidden = false;
      if (searchSug) searchSug.innerHTML = '';
      hits = hits.filter(function (x) { return searchCat === 'all' || x.sec.c === searchCat; });
      var top = hits[0], rest = hits.slice(1);
      /* one clear winner gets a labeled hero card; the rest stay plain rows */
      var isClear = top.s >= 150 && (!rest.length || top.s >= rest[0].s + 50);
      var html = '';
      if (isClear) {
        html += '<a class="hc-best" href="' + docHref(top.sec) + '">' +
          '<span class="hc-best-label">' + hcT('Best result') + '</span>' +
          '<b>' + markText(top.sec.t, norm(q)) + '</b>' +
          '<span class="hc-best-cat">' + escapeHtml(CATS[top.sec.c] || '') + '</span>' +
          '<p>' + markText(snippet(top.sec.b, norm(q)), norm(q)) + '</p></a>';
        if (rest.length) html += '<div class="hc-sempty-h" style="max-width:760px;margin:0 auto 6px;font-size:.8rem;font-weight:700;color:var(--text-dim)">' + hcT('All results') + '</div>';
        html += rest.map(function (x) { return resultRow(x.sec, norm(q)); }).join('');
      } else {
        html = hits.map(function (x) { return resultRow(x.sec, norm(q)); }).join('');
      }
      searchList.innerHTML = html;
      hcTranslateNow(searchList);
    } else {
      searchList.hidden = true;
      searchList.innerHTML = '';
      if (searchEmpty) {
        searchEmpty.hidden = false;
        if (searchSug) searchSug.innerHTML = ex.words.length ? suggestionsFor(ex, 6) : suggestionsFor({ all: [] }, 6);
      }
    }
  }

  /* ---------------- sidebar collapse (desktop, persisted) ---------------- */
  var sideToggle = document.getElementById('hcSideToggle');
  var sideReveal = document.getElementById('hcSideReveal');
  function setSide(collapsed, persist) {
    document.documentElement.classList.toggle('hc-collapsed', !!collapsed);
    if (persist) { try { localStorage.setItem('fs-help-side', collapsed ? 'closed' : 'open'); } catch (e) {} }
  }
  if (sideToggle) sideToggle.addEventListener('click', function () {
    /* phones: the sidebar is a drawer — the ">" close button must close the
       DRAWER, not flip the desktop collapsed flag (which did nothing) */
    if (window.matchMedia('(max-width: 1020px)').matches) {
      document.body.classList.remove('hc-side-open');
      return;
    }
    setSide(true, true);
  });
  if (sideReveal) sideReveal.addEventListener('click', function () { setSide(false, true); });

  function focusSearch() {
    var onHome = !document.querySelector('.view[data-view="home"]') || !document.querySelector('.view[data-view="home"]').hidden;
    var target = onHome && heroInput ? heroInput : (headInput || heroInput);
    if (target) { target.focus(); target.select(); }
  }

  /* hero "S" button */
  var sBtn = document.getElementById('hcSBtn');
  if (sBtn) sBtn.addEventListener('click', function () {
    if (heroInput) { heroInput.focus(); heroInput.select(); }
  });

  /* keyboard shortcuts: S or Ctrl/Cmd+K = search, T = topics sidebar */
  document.addEventListener('keydown', function (e) {
    var el = document.activeElement;
    var tag = (el && el.tagName) || '';
    if (tag === 'INPUT' || tag === 'TEXTAREA' || (el && el.isContentEditable)) return;
    var mod = e.ctrlKey || e.metaKey || e.altKey;
    /* Settings > Hotkeys switches the whole set off: these keys stand down
       with every other shortcut, and the keycap hints disappear with them. */
    if (document.documentElement.getAttribute('data-keys') === 'off') return;
    var isK = (e.key === 'k' || e.key === 'K') && (e.ctrlKey || e.metaKey);
    if (isK) { e.preventDefault(); focusSearch(); return; }
    /* O = topics. Guard: ignore chords mid-recording in the hotkeys editor
       (its capture-phase handler stops them; this belt-and-suspenders check
       keeps a sequence like O then B from flipping the sidebar mid-chord). */
    var hk = window.FS_HK_RECORDING;
    if ((e.key === 'o' || e.key === 'O') && !mod && window.innerWidth > 860 && !hk) {
      e.preventDefault();
      setSide(!document.documentElement.classList.contains('hc-collapsed'), true);
      return;
    }
    /* 1-9: jump to the Nth topic in the sidebar (help center) */
    if (/^[1-9]$/.test(e.key) && !mod && window.innerWidth > 860 && !hk) {
      var sideNav = document.getElementById('hcSideNav');
      var item = sideNav && sideNav.children[e.key - 1];
      if (item) {
        e.preventDefault();
        item.click();
        return;
      }
    }
  });

  /* deep link support: help.html?q=... (used by the site SearchAction) */
  try {
    var qs = new URLSearchParams(location.search).get('q');
    if (qs && qs.trim()) {
      location.hash = '#/s/' + encodeURIComponent(qs.trim().slice(0, 200));
      history.replaceState(null, '', location.pathname);  /* keep the URL clean */
    }
  } catch (e) {}

  /* try-asking chips -> prefill + run search */
  document.addEventListener('click', function (e) {
    var chip = e.target.closest && e.target.closest('.hc-chip-q');
    if (!chip) return;
    e.preventDefault();
    var q = chip.getAttribute('data-q') || chip.textContent.trim();
    location.hash = '#/s/' + encodeURIComponent(q);
  });

  /* jump-to-section links inside articles (and the mobile Contents sheet) */
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('.hc-jump-n a, .hc-toc-list a');
    if (!a) return;
    var id = a.getAttribute('data-jid');
    var target = id && document.getElementById(id);
    if (!target) return;
    e.preventDefault();
    var pv = tocParts(a);
    closeToc(pv.sheet, pv.scrim);
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  /* mobile Contents sheet — fully delegated: every article view carries its
     own fab/sheet/scrim, so we always resolve them from the event target */
  function tocParts(el) {
    var view = el.closest && el.closest('.view[data-view="article"]');
    return view
      ? { sheet: view.querySelector('[data-toc-sheet]'), scrim: view.querySelector('[data-toc-scrim]') }
      : { sheet: null, scrim: null };
  }
  function openToc(sheet, scrim) {
    if (!sheet) return;
    sheet.hidden = false; scrim.hidden = false;
    void sheet.offsetWidth; /* reflow so unhide -> open animates */
    sheet.classList.add('open'); scrim.classList.add('open');
  }
  function closeToc(sheet, scrim) {
    if (!sheet || sheet.hidden) return;
    sheet.classList.remove('open'); scrim.classList.remove('open');
    setTimeout(function () { sheet.hidden = true; scrim.hidden = true; }, 400);
  }
  document.addEventListener('click', function (e) {
    var fab = e.target.closest && e.target.closest('[data-toc-fab]');
    if (fab) {
      e.preventDefault();
      var p = tocParts(fab);
      openToc(p.sheet, p.scrim);
      return;
    }
    if (e.target.closest && e.target.closest('[data-toc-close]')) {
      var p2 = tocParts(e.target);
      closeToc(p2.sheet, p2.scrim);
      return;
    }
    if (e.target.classList && e.target.classList.contains('hc-toc-scrim')) {
      var p3 = tocParts(e.target);
      closeToc(p3.sheet, p3.scrim);
    }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var view = document.querySelector('.view[data-view="article"]:not([hidden])');
    if (view) { var p = tocParts(view); closeToc(p.sheet, p.scrim); }
  });
  /* show the Contents pill only on article views that actually have sections */
  function syncTocFab() {
    var view = document.querySelector('.view[data-view="article"]:not([hidden])');
    var fab = view && view.querySelector('[data-toc-fab]');
    if (fab) fab.hidden = !view.querySelector('.hc-jump-pop a');
  }
  document.addEventListener('viewchange', syncTocFab);
  setTimeout(syncTocFab, 60);

  /* "Try asking": 3 random chips per visit instead of the full wall */
  (function () {
    var row = document.querySelector('.hc-try .hc-chiprow');
    if (!row) return;
    var kids = Array.prototype.slice.call(row.children);
    kids.sort(function () { return Math.random() - .5; });
    kids.forEach(function (c) { row.appendChild(c); });
    kids.slice(3).forEach(function (c) { c.hidden = true; });
  })();

  /* reading progress on article pages */
  function updateProgress() {
    if (!progressBar) return;
    var el = document.querySelector('.view[data-view="article"]:not([hidden]) .hc-art');
    if (!el) { progressBar.style.width = '0'; return; }
    var rect = el.getBoundingClientRect();
    var total = Math.max(1, el.offsetHeight - window.innerHeight * 0.6);
    var done = Math.min(1, Math.max(0, (80 - rect.top) / total));
    progressBar.style.width = (done * 100).toFixed(2) + '%';
  }
  window.addEventListener('scroll', updateProgress, { passive: true });
  window.addEventListener('resize', updateProgress);

  /* sticky header deepens once the page scrolls (Apple-style elevation) */
  var siteHeader = document.querySelector('header.site');
  function updateHead() {
    if (siteHeader) siteHeader.classList.toggle('scrolled', window.scrollY > 8);
  }
  updateHead();
  window.addEventListener('scroll', updateHead, { passive: true });
})();
'''


# -------------------------------------------------------------- rendering --
def render_faq(faq, link_href, link_label, aid=None, heading='Common questions'):
    if not faq:
        return ''
    out = ['<div class="hc-faq"><h2>' + esc(heading) + '</h2>']
    for i, f in enumerate(faq):
        chips = ''
        did = f' id="{aid}-q{i}"' if aid else ''
        if f['links']:
            chips = '<div class="hc-chips" style="margin-top:10px">' + ''.join(
                f'<a class="hc-chip" href="{link_href(l)}"><span>{esc(link_label(l))}</span>{svg("arrow-r")}</a>'
                for l in f['links']) + '</div>'
        out.append(f'<details{did}><summary>{esc_q(f["q"])}</summary>'
                   f'<div class="hc-fa">{text_to_html(f["a"])}{chips}</div></details>')
    out.append('</div>')
    return '\n'.join(out)


def render_home(groups, quick, n_articles):
    cards = []
    for g in groups:
        cat, kids = g['cat'], g['kids']
        icon = CAT_ICONS.get(cat['id'], DEFAULT_ICON)
        if not kids and art_eligible(cat):
            count_label = 'Guide'
        else:
            n_kids = len(kids) + (1 if art_eligible(cat) else 0)
            count_label = f'{n_kids} article{"s" if n_kids != 1 else ""}'
        prev = ''
        if kids:
            lines = ''.join(f'<span>{esc(k["title"])}</span>' for k in kids[:3])
            more = len(kids) - 3
            if more > 0:
                lines += f'<span>+{more} more</span>'
            prev = f'<span class="hc-cat-prev">{lines}</span>'
        cards.append(
            f'<a class="hc-cat hc-card" href="help/c/{esc(cat["id"])}">'
            f'<span class="hc-ic">{svg(icon)}</span>'
            f'<span class="hc-cat-t">{esc(cat["title"])}</span>'
            f'<span class="hc-cat-c">{count_label}</span>'
            f'<span class="hc-cat-d">{esc(CAT_DESC.get(cat["id"], DEFAULT_DESC))}</span>{prev}</a>')

    _feat_src = [g for g in groups if g['cat']['id'] != 'misc'][:4]
    _feat_sub = {'start': 'Connect and send your first post', 'scheduling': 'One-time and recurring posts', 'channels': 'Connect and manage channels', 'bots': 'Use your own sender bot', 'premium': 'Plans, Stars and payments', 'backup': 'Backups and migration'}
    feat_html = ''.join(f'<a href="help/c/{esc(g["cat"]["id"])}"><span class="hc-ic">{svg(CAT_ICONS.get(g["cat"]["id"], DEFAULT_ICON))}</span><b>{esc(g["cat"]["title"])}</b><span class="s">{esc(_feat_sub.get(g["cat"]["id"], "Guides and answers"))}</span></a>' for g in _feat_src)
    _band_src = [g for g in groups if g['cat']['id'] != 'misc'][4:10]
    band_html = ''.join(f'<a href="help/c/{esc(g["cat"]["id"])}"><b>{esc(g["cat"]["title"])}</b><span>{len(g["kids"])} articles</span></a>' for g in _band_src)
    quick_html = ''
    if quick:
        links = ''.join(f'<a href="help/a/{esc(nid)}.html">{esc(title)}</a>' for nid, title in quick)
        quick_html = f'<div class="hc-pop"><b>Popular:</b>{links}</div>'

    try_chips = ''.join(
        f'<button type="button" class="hc-chip hc-chip-q" data-q="{esc(q)}">{svg("search")}{esc(q)}</button>'
        for q in TRY_ASKING)
    try_html = (f'<div class="hc-try"><div class="hc-try-label">Try asking</div>'
                f'<div class="hc-chiprow">{try_chips}</div></div>') if TRY_ASKING else ''

    cta_html = (
        f'<div class="hc-cta"><span class="hc-ic">{svg("buoy")}</span>'
        f'<div class="hc-cta-t"><b>Still stuck?</b>'
        f'<span>Ask in Telegram &mdash; a human answers every ticket.</span></div>'
        f'<a class="btn btn-primary" href="{SUPPORT_URL}" target="_blank" rel="noopener noreferrer">{svg("send")}Ask in Telegram</a></div>')

    return f'''
      <section class="view" data-view="home">
        <div class="hc-docs-head">
          <span class="hc-kicker">{svg('book')} Fast Scheduler</span>
          <h1 class="hc-title">Help Center</h1>
          <p class="hc-sub">Everything about Fast Scheduler &mdash; scheduling, recurring posts, sender bots, channels, statistics and payments. Search it or browse by topic.</p>
          <div class="hc-search">
            {svg('search', 'sic')}
            <input id="hcSearch" type="search" role="combobox" aria-autocomplete="list" aria-haspopup="listbox" aria-expanded="false" aria-controls="hcResults" placeholder="Search articles&hellip;" aria-label="Search help topics" autocomplete="off" enterkeyhint="search">
            <button class="hc-sbtn" id="hcSBtn" type="button" aria-label="Search (Ctrl+K)" title="Search (Ctrl+K)">Ctrl K</button>
            <div class="hc-results" id="hcResults" role="listbox" aria-label="Search results" hidden></div>
          </div>
          {try_html}
          {quick_html}
        </div>
        <div class="hc-feat">{feat_html}</div>
        <div class="hc-band"><h2>Fast Scheduler platform</h2><p class="sub">Scheduling, delivery, bots, payments and tools — pick a section to dive in.</p><div class="hc-band-grid">{band_html}</div></div>
        {cta_html}
        <div class="hc-section-h" style="padding-top:26px"><h2>Browse by topic</h2><span>{n_articles} articles &middot; {len(groups)} categories</span></div>
        <div class="hc-grid">
          {''.join(cards)}
        </div>
      </section>'''


def render_category(g, groups, by_id):
    cat, kids = g['cat'], g['kids']
    icon = CAT_ICONS.get(cat['id'], DEFAULT_ICON)

    def link_href(lid):
        target = by_id.get(lid)
        if target and art_eligible(target) and lid not in WEB_DROPS:
            return f'a/{esc(lid)}'
        if target and target.get('title'):
            return f'c/{esc(lid)}'
        return '#/'

    def link_label(lid):
        target = by_id.get(lid)
        if target and target.get('title'):
            return target['title']
        return lid.replace('_', ' ').strip().title()

    rows = []
    if kids:
        if art_eligible(cat):
            rows.append(f'<a class="hc-row hc-row-lead" href="help/a/{esc(cat["id"])}.html">'
                        f'<span class="hc-row-t">Overview: {esc(cat["title"])}</span>'
                        f'<span class="hc-row-m">Start here</span>{svg("chev")}</a>')
        for n in kids:
            if not art_eligible(n):
                continue
            meta = f'{len(n["faq"])} Q&amp;A' if n['faq'] else 'Guide'
            rows.append(f'<a class="hc-row" href="help/a/{esc(n["id"])}.html">'
                        f'<span class="hc-row-t">{esc(n["title"])}</span>'
                        f'<span class="hc-row-m">{meta}</span>{svg("chev")}</a>')
    elif art_eligible(cat):
        # Single-guide category: surface its FAQ links as article rows, and
        # never leave the page without anything to read.
        seen = set()
        for f in cat['faq']:
            for lid in f['links']:
                if lid in seen or lid == cat['id']:
                    continue
                t = by_id.get(lid)
                if t and art_eligible(t) and lid not in WEB_DROPS:
                    seen.add(lid)
                    meta = f'{len(t["faq"])} Q&amp;A' if t['faq'] else 'Guide'
                    rows.append(f'<a class="hc-row" href="help/a/{esc(lid)}.html">'
                                f'<span class="hc-row-t">{esc(t["title"])}</span>'
                                f'<span class="hc-row-m">{meta}</span>{svg("chev")}</a>')
        if not rows:
            for o in groups:
                if o['cat']['id'] == cat['id'] or not o['kids']:
                    continue
                rows.append(f'<a class="hc-row" href="help/c/{esc(o["cat"]["id"])}">'
                            f'<span class="hc-row-t">{esc(o["cat"]["title"])}</span>'
                            f'<span class="hc-row-m">Category</span>{svg("chev")}</a>')

    intro = text_to_html(cat['content']) if cat['content'] else ''
    intro_html = f'<div class="hc-intro">{intro}</div>' if intro else ''
    faq_html = render_faq(cat['faq'], link_href, link_label) if (cat['faq'] and art_eligible(cat)) else ''

    others = ''.join(
        f'<a href="help/c/{esc(o["cat"]["id"])}">{esc(o["cat"]["title"])}</a>'
        for o in groups if o['cat']['id'] != cat['id'])

    n_label = f'{len(rows)} article{"s" if len(rows) != 1 else ""}' if rows else 'Guide'

    return f'''
      <section class="view" data-view="category" data-cat="{esc(cat["id"])}" hidden>
        <nav class="hc-crumbs" aria-label="Breadcrumb">
          <a href="#/">Help Center</a>{svg('chev')}
          <span aria-current="page">{esc(cat["title"])}</span>
        </nav>
        <header class="hc-cat-head">
          <span class="hc-ic">{svg(icon)}</span>
          <div>
            <h2>{esc(cat["title"])}</h2>
            <p>{n_label}</p>
          </div>
        </header>
        {intro_html}
        <div class="hc-section-h"><h2>All articles</h2><span>{n_label}</span></div>
        <div class="hc-list" data-list>
          {''.join(rows)}
        </div>
        <button type="button" class="hc-more" data-more hidden><span data-more-t>Show more</span><span data-less-t hidden>Show less</span></button>
        {faq_html}
        <div class="hc-others" data-others><span>Other categories:</span>{others}</div>
        <button type="button" class="hc-more" data-more hidden><span data-more-t>Show more</span><span data-less-t hidden>Show less</span></button>
      </section>'''


def faq_rail_html(faq, aid, href):
    items = []
    for i, f in enumerate(faq or []):
        q = re.sub(r'<[^>]+>', '', f.get('q', '')).strip()
        if q:
            items.append((aid + '-q' + str(i), q))
    if not items:
        return ''
    return ''.join(
        '<a href="' + href + '" data-faq-open="' + sid + '" data-rk="' + sid + '">' + esc(lbl) + '</a>'
        for sid, lbl in items)

def render_article(n, group, by_id, order_index):
    cat = group['cat']
    crumbs_self = (f'<a href="#/c/{esc(cat["id"])}">{esc(cat["title"])}</a>' if n['id'] != cat['id']
                   else f'<span aria-current="page">{esc(cat["title"])}</span>')
    if n['id'] != cat['id']:
        crumbs = (f'<nav class="hc-crumbs" aria-label="Breadcrumb"><a href="#/">Help Center</a>{svg("chev")}'
                  f'<a href="#/c/{esc(cat["id"])}">{esc(cat["title"])}</a>{svg("chev")}'
                  f'<span aria-current="page">{esc(n["title"])}</span></nav>')
    else:
        crumbs = (f'<nav class="hc-crumbs" aria-label="Breadcrumb"><a href="#/">Help Center</a>{svg("chev")}'
                  f'<span aria-current="page">{esc(n["title"])}</span></nav>')

    def link_href(lid):
        target = by_id.get(lid)
        if target and art_eligible(target):
            return f'#/a/{esc(lid)}'
        if target and target.get('title'):
            return f'#/c/{esc(lid)}'
        return '#/'

    def link_label(lid):
        target = by_id.get(lid)
        if target and target.get('title'):
            return target['title']
        return lid.replace('_', ' ').strip().title()

    if n.get('_raw_html'):
        body = n['content']
    else:
        body = text_to_html(n['content']) if n['content'] else ''
    faq_html = render_faq(n['faq'], link_href, link_label, n['id'])

    # "Jump to a section" box: anchor every <h3> and link to it (TikTok-style).
    jump_secs = []
    seen_secs = set()

    def _h3_sub(m):
        label = m.group(1)
        sid = 'sec-' + re.sub(r'[^a-z0-9]+', '-', re.sub(r'<[^>]+>', '', label).lower()).strip('-')
        while sid in seen_secs:
            sid += '-x'
        seen_secs.add(sid)
        jump_secs.append((sid, re.sub(r'<[^>]+>', '', label)))
        return f'<h3 id="{sid}">{label}</h3>'

    if '<h3>' in body:
        body = re.sub(r'<h3>(.*?)</h3>', _h3_sub, body, flags=re.S)
    toc_list = ''
    if jump_secs:
        parts = []
        for sid, lbl in jump_secs[:6]:
            parts.append(f'<a href="#/a/{esc(n["id"])}" data-jid="{sid}">{esc(lbl)}</a>')
        jump_html = ('<div class="hc-jump">'
                     '<div class="hc-jump-strip" tabindex="0" role="button" aria-label="Jump to a section">'
                     + svg('menu') + '<span class="vtxt">Sections</span></div>'
                     '<nav class="hc-jump-pop glass-pop" aria-label="Jump to a section">'
                     '<div class="hc-jump-head">Jump to a section</div>'
                     f'<div class="hc-jump-n">{"".join(parts)}</div>'
                     '</nav></div>')
        toc_list = ''.join(f'<li><a href="#/a/{esc(n["id"])}" data-jid="{esc(sid)}" data-toc-link>{esc(lbl)}</a></li>'
                           for sid, lbl in jump_secs[:6])
    else:
        jump_html = ''

    related = []
    rail_pairs = []
    seen = set()
    for f in n['faq']:
        for lid in f['links']:
            if lid in seen or lid == n['id']:
                continue
            target = by_id.get(lid)
            if not target or not (art_eligible(target) or target.get('title')):
                continue
            seen.add(lid)
            rail_pairs.append((link_href(lid), link_label(lid)))
            related.append(f'<a class="hc-chip" href="{link_href(lid)}"><span>{esc(link_label(lid))}</span>{svg("arrow-r")}</a>')
    related_html = ''
    if related:
        related_html = f'<div class="hc-related"><h2>Related topics</h2><div class="hc-chips">{"".join(related)}</div></div>'

    prev_n = order_index.get(('prev', n['id']))
    next_n = order_index.get(('next', n['id']))
    def _toc_navc(kind, node):
        if node:
            cls = 'prev' if kind == 'prev' else 'next'
            lbl = 'Previous' if kind == 'prev' else 'Up next'
            arrow = svg('arrow-l') if kind == 'prev' else svg('arrow-r')
            desc = ' '.join(re.sub(r'<[^>]+>', ' ', node.get('d') or node.get('b') or '').split())[:90]
            return (f'<a class="hc-toc-navc {cls}" href="#/a/{esc(node["id"])}" data-toc-nav>'
                    f'<small>{lbl}</small><b>{esc(node["title"])}</b>'
                    + (f'<span>{esc(desc)}&hellip;</span>' if desc else '') + arrow + '</a>')
        lbl = 'No previous article' if kind == 'prev' else 'No next article'
        return f'<span class="hc-toc-navc {kind} none"><small>{lbl}</small></span>'

    toc_prev_html = _toc_navc('prev', prev_n)
    toc_next_html = _toc_navc('next', next_n)

    pager = ['<nav class="hc-pager" aria-label="More articles">']
    if prev_n:
        pager.append(f'<a class="hc-card prev" href="#/a/{esc(prev_n["id"])}">{svg("arrow-l")}'
                     f'<span><small>Previous</small><b>{esc(prev_n["title"])}</b></span></a>')
    else:
        pager.append('<span></span>')
    if next_n:
        pager.append(f'<a class="hc-card next" href="#/a/{esc(next_n["id"])}">'
                     f'<span><small>Next</small><b>{esc(next_n["title"])}</b></span>{svg("arrow-r")}</a>')
    else:
        pager.append('<span></span>')
    pager.append('</nav>')
    pager_html = ''.join(pager) if (prev_n or next_n) else ''

    art_meta = ''
    if n['faq']:
        art_meta = (f'<div class="hc-art-meta"><a href="#/c/{esc(cat["id"])}">{esc(cat["title"])}</a>'
                    f'<span class="dot">{len(n["faq"])} Q&amp;A</span></div>')
    else:
        art_meta = (f'<div class="hc-art-meta"><a href="#/c/{esc(cat["id"])}">{esc(cat["title"])}</a></div>')
    tools_html = (f'<div class="hc-tools" data-tools>' + f'<button type="button" class="hc-tool" data-fs-btn aria-label="Fullscreen article" title="Fullscreen article">{svg("expand")}</button></div>')
    rail_secs = ''.join(
        f'<a href="#/a/{esc(n["id"])}" data-jid="{esc(sid)}" data-rk="{esc(sid)}">{esc(lbl)}</a>'
        for sid, lbl in jump_secs[:8])
    rail_faq = faq_rail_html(n['faq'], n['id'], f'#/a/{esc(n["id"])}')
    rail_rel = ''
    if rail_pairs:
        rail_rel = ('<div class="hc-rail-rel"><span>Related topics</span><nav>' +
                    ''.join(f'<a href="{h}">{esc(lbl)}</a>' for h, lbl in rail_pairs[:5]) +
                    '</nav></div>')
    rail_html = ''
    if rail_secs or rail_faq:
        rail_html = (f'<aside class="hc-rail" aria-label="On this page"><div class="hc-rail-t">On this page</div>'
                     f'<nav data-rail>{rail_secs}{rail_faq}</nav>{rail_rel}</aside>')
    fb_html = ''
    return f'''
      <section class="view" data-view="article" data-art="{esc(n["id"])}" hidden>
        <div class="hc-toolbar">{crumbs}{tools_html}</div>
        <div class="hc-doc">
        <article class="hc-art hc-card">
          <h2>{esc(n["title"])}</h2>
          {art_meta}
          <div class="hc-body">{body}</div>
          {faq_html}
          {related_html}
          {fb_html}
        </article>
        {rail_html}
        {jump_html}
        <button type="button" class="hc-toc-fab" data-toc-fab aria-label="Open contents" hidden>{svg('book')}<span>Contents</span></button>
        <div class="hc-toc-scrim" data-toc-scrim hidden></div>
        <div class="hc-toc-sheet" data-toc-sheet role="dialog" aria-modal="true" aria-label="Contents" hidden>
          <div class="hc-toc-head"><span>Contents</span><button type="button" class="icon-btn" data-toc-close aria-label="Close contents">{svg('close')}</button></div>
          <div class="hc-toc-nav">
            {toc_prev_html}
            <div class="hc-toc-navc cur"><small>Now reading</small><b>{esc(n["title"])}</b></div>
            {toc_next_html}
          </div>
          <ol class="hc-toc-list">{toc_list}</ol>
        </div>
        </div>
        {pager_html}
        <div class="hc-cta">
          <div><b>Still stuck?</b><p>The in-bot assistant answers the same questions &mdash; and a human reads every ticket.</p></div>
          <a class="btn" href="{BOT_URL}" target="_blank" rel="noopener noreferrer">{svg('send')} Ask in Telegram</a>
        </div>
      </section>'''


FAVICON = (
    '<link rel="icon" href="favicon.ico" sizes="any">\n'
    '  <link rel="icon" href="favicon.svg" type="image/svg+xml">\n'
    '  <link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">\n'
    '  <link rel="icon" href="icon-48.png" sizes="48x48" type="image/png">\n'
    '  <link rel="icon" href="icon-192.png" sizes="192x192" type="image/png">\n'
    '  <link rel="icon" href="icon-512.png" sizes="512x512" type="image/png">\n'
    '  <link rel="apple-touch-icon" href="apple-touch-icon.png" sizes="180x180">'
)


def favicon(rel=''):
    """Favicon links with a path prefix for pages below the site root."""
    pref = (rel.rstrip('/') + '/') if rel else ''
    return FAVICON.replace('href="', 'href="' + pref)


def build_page(nodes, help_sec):
    apply_web_model(help_sec)
    inject_seo_articles(help_sec)
    groups = build_groups(help_sec)

    # Articles that get their own page, in tree order.
    article_order = []
    for g in groups:
        for n in [g['cat']] + g['kids']:
            n['c'] = g['cat']['id']
            if n['id'] != 'misc' and art_eligible(n):
                article_order.append(n)
    for g in groups:
        if g['cat']['id'] == 'misc':
            for n in g['kids']:
                n['c'] = 'misc'
                if art_eligible(n):
                    article_order.append(n)

    by_id = {}
    for g in groups:
        for n in [g['cat']] + g['kids']:
            by_id[n['id']] = n

    order_index = {}
    for i, n in enumerate(article_order):
        if i > 0:
            order_index[('prev', n['id'])] = article_order[i - 1]
        if i < len(article_order) - 1:
            order_index[('next', n['id'])] = article_order[i + 1]

    quick = [(nid, by_id[nid]['title']) for nid in QUICK_LINK_IDS if nid in by_id and art_eligible(by_id[nid])][:5]
    if not quick:
        quick = [(n['id'], n['title']) for n in article_order[:5]]

    home_html = render_home(groups, quick, len(article_order))
    cats_html = '\n'.join(render_category(g, groups, by_id) for g in groups)
    # Article bodies live on their own static pages (help/a/<id>/) so the hub
    # no longer duplicates 345 guides and stays small and fast to paint.
    arts_html = ''
    # No per-article FAQPage JSON-LD inlined here. Google expects one FAQPage
    # per URL and treats ~100 of them as structured-data spam; it also cost
    # 92 KB of body markup. Every article here also has a static page
    # (help/a/<id>.html) whose <head> carries the same FAQPage markup
    # (build_static.py emits it). The hub declares itself a CollectionPage
    # with an ItemList of all articles instead — the schema Google recommends
    # for an index page, and an explicit statement of which URLs are canonical.

    side_payload = json.dumps([
        {'id': g['cat']['id'], 'title': g['cat']['title'],
         'n': len(g['kids']) + (1 if art_eligible(g['cat']) else 0),
         'icon': ICONS[CAT_ICONS.get(g['cat']['id'], DEFAULT_ICON)],
         'kids': [{'id': k['id'], 't': k['title']} for k in g['kids'] if art_eligible(k)][:8]}
        for g in groups if g['cat']['id'] != 'misc'], ensure_ascii=False)
    search_payload = build_search_json(article_order, groups)
    # Size: the search/sidebar payloads (~730 KB) and the hub app script
    # (~46 KB) used to inline here, pushing help.html past 3 MB. They now
    # ship as versioned external files; the hub HTML stays content-only.
    with open(os.path.join(REPO_ROOT, 'website', 'scripts', 'help-data.js'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('/* Generated by website/_build/build_help.py -- do not edit. */\n'
                'window.__HELP_SIDE=' + side_payload + ';window.__HELP_DATA=' + search_payload + ';\n')
    with open(os.path.join(REPO_ROOT, 'website', 'scripts', 'help-hub.js'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(JS.replace('__BOTURL__', SUPPORT_URL))
    year = datetime.date.today().year

    n_cats = len(groups)

    # Index-page schema: an explicit list of every article's canonical URL.
    # Google recommends this for hubs and it replaces the FAQPage mass that
    # used to sit in this page's <body>.
    HELP_INDEX_LD = json.dumps({
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        'name': 'Fast Scheduler Help Center',
        'url': 'https://fastscheduler.github.io/help.html',
        'description': ('Searchable Fast Scheduler help center: %d answers on '
                        'scheduling, recurring posts, sender bots, channels, '
                        'premium and payments.' % len(article_order)),
        'inLanguage': 'en',
        'isPartOf': {'@type': 'WebSite', 'name': 'Fast Scheduler',
                     'url': 'https://fastscheduler.github.io/'},
        'mainEntity': {
            '@type': 'ItemList',
            'numberOfItems': len(article_order),
            'itemListElement': [
                {'@type': 'ListItem', 'position': i, 'name': a['title'],
                 'url': 'https://fastscheduler.github.io/help/a/%s.html' % a['id']}
                for i, a in enumerate(article_order, 1)
            ],
        },
    }, ensure_ascii=False)

    BURGER = ('<button class="icon-btn hc-menu-btn" id="hcMenuBtn" aria-label="Open navigation" '
              'aria-controls="hcSideNav">%s</button>' % svg('menu'))
    HSEARCH = ('<div class="hc-hsearch">%s'
               '<input id="hcSearchH" type="search" role="combobox" aria-autocomplete="list" aria-haspopup="listbox" placeholder="Search articles" '
               'aria-label="Search help articles" autocomplete="off" aria-expanded="false" '
               'aria-controls="hcResultsH" enterkeyhint="search">'
               '<kbd>Ctrl K</kbd>'
               '<div class="hc-results" id="hcResultsH" role="listbox" '
               'aria-label="Search results" hidden></div></div>' % svg('search', 'sic'))
    MENU_INNER = (
      '<div class="gp-head">Settings</div>'
      '<button type="button" class="gp-row" aria-pressed="false" '
      'id="rowDark">%s<span>Dark mode</span><span class="io-switch" aria-hidden="true"></span></button>'
      '<button type="button" class="gp-row" aria-pressed="true" '
      'id="rowAnim">%s<span>Animations</span><span class="io-switch" aria-hidden="true"></span></button>'
      '<button type="button" class="gp-row" aria-pressed="true" '
      'id="rowFx">%s<span>Effects</span><span class="io-switch" aria-hidden="true"></span></button>'
      '<button type="button" class="gp-row" aria-pressed="true" '
      'id="rowKeys">%s<span>Hotkeys</span><span class="io-switch" aria-hidden="true"></span></button>'
      '<div class="gp-sep gp-reading" data-reading hidden></div>'
      '<div class="gp-head gp-reading" data-reading hidden>Reading</div>'
      '<button type="button" class="gp-row gp-reading" data-reading '
      'aria-pressed="true" data-rail-toggle hidden>%s<span>Article navigation</span>'
      '<span class="io-switch" aria-hidden="true"></span></button>'
      '<div class="gp-row gp-fonts" data-fonts>%s<span>Font size</span><span class="hc-fonts">'
      '<button type="button" data-font="s" aria-label="Small">A</button>'
      '<button type="button" data-font="m" aria-label="Default">A</button>'
      '<button type="button" data-font="l" aria-label="Large">A</button></span></div>'
      '<button type="button" class="gp-row gp-row-sub" id="rowKeysHelp">'
      '<svg viewBox="0 0 24 24" fill="none" stroke="none" aria-hidden="true" '
      'style="visibility:hidden;width:18px;height:18px"></svg><span class="gp-sub-label">See hotkeys</span>'
      '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
      '<polyline points="9 18 15 12 9 6"/></svg></button>'
      '<div class="gp-sep" role="separator"></div>'
      '<a class="gp-row" href="%s" target="_blank" rel="noopener noreferrer">'
      '%s<span>Support chat</span>%s</a>'
      % (svg('moon'), svg('zap'), svg('sparkles'), svg('keys'), svg('book'),
         svg('book'), SUPPORT_URL, svg('send'), svg('chev')))
    SITE_LD = site_entity_ld()
    NAV = unified_nav('.', BOT_URL, MENU_INNER, center_extra=HSEARCH,
                      brand_extra='<span class="hc-brand-help">Help Center</span>',
                      right_extra=BURGER)
    return f'''<!doctype html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://www.googletagmanager.com https://*.google-analytics.com https://*.analytics.google.com https://www.google.com; font-src 'self'; connect-src 'self' https://www.googletagmanager.com https://*.google-analytics.com https://*.analytics.google.com https://region1.google-analytics.com https://www.google.com; frame-src https://www.googletagmanager.com; object-src 'none'; form-action 'self'; base-uri 'self'; upgrade-insecure-requests">
  <meta name="theme-color" content="#1faa59">
  <meta name="color-scheme" content="light dark">
  <title>{fit_title("Help Center — Fast Scheduler for Telegram")}</title>
  <meta name="description" content="{esc(smart_desc("Searchable help center for Fast Scheduler: scheduling, recurring posts, sender bots, channels, statistics, premium and payments. %d answers, instantly searchable." % len(article_order)))}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://fastscheduler.github.io/help.html">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Help Center — Fast Scheduler for Telegram">
  <meta property="og:description" content="{len(article_order)} searchable help topics for the Fast Scheduler Telegram bot.">
  <meta property="og:url" content="https://fastscheduler.github.io/help.html">
  <meta property="og:image" content="https://fastscheduler.github.io/og-cover-v2.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Help Center — Fast Scheduler for Telegram">
  <meta name="twitter:description" content="{len(article_order)} searchable help topics for the Fast Scheduler Telegram bot.">
  <meta name="twitter:image" content="https://fastscheduler.github.io/og-cover-v2.png">
  {FAVICON}
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type": "ListItem", "position": 1, "name": "Fast Scheduler", "item": "https://fastscheduler.github.io/"}},
      {{"@type": "ListItem", "position": 2, "name": "Help Center", "item": "https://fastscheduler.github.io/help.html"}}
    ]
  }}
  </script>
  <script type="application/ld+json">{HELP_INDEX_LD}</script>
  {SITE_LD}
  <script>
    try {{
      var t = localStorage.getItem('theme');
      if (!t && window.matchMedia) t = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      if (t) document.documentElement.setAttribute('data-theme', t);
      if (localStorage.getItem('fs-motion') === 'off') document.documentElement.setAttribute('data-motion', 'off');
      if (localStorage.getItem('fs-fx') === 'off') document.documentElement.setAttribute('data-fx', 'off');
      if (localStorage.getItem('fs-hotkeys') === 'off') document.documentElement.setAttribute('data-keys', 'off');
      if (localStorage.getItem('fs-rail') === 'off') document.documentElement.classList.add('rail-off');
      if (localStorage.getItem('fs-help-side') === 'closed') document.documentElement.classList.add('hc-collapsed');
      if (localStorage.getItem('fs-help-wide') === 'on') document.documentElement.classList.add('hc-wide', 'hc-collapsed');
      /* hub only: article fullscreen never applies here (no exit toggle on the hub) */
      var _ff = localStorage.getItem('fs-font') || localStorage.getItem('fs-help-font');
      if (_ff) {{ document.documentElement.setAttribute('data-font', _ff); document.documentElement.setAttribute('data-hcfont', _ff); }}
      if (localStorage.getItem('fs-help-wide') === 'on') document.documentElement.classList.add('hc-wide');
      var _ff = localStorage.getItem('fs-font') || localStorage.getItem('fs-help-font');
      if (_ff) {{ document.documentElement.setAttribute('data-font', _ff); document.documentElement.setAttribute('data-hcfont', _ff); }}
    }} catch (e) {{}}
  </script>
  <link rel="preload" href="fonts/space-grotesk-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="styles/main.css?v=20261030a1">
  <link rel="stylesheet" href="styles/liquid-nav.css?v=20261007a1">
<link rel="stylesheet" href="styles/hotkeys-modal.css?v=20261006a1">
  <style>{CSS}
  </style>
</head>
<body class="help">
{NAV}
  <div class="hc-progress" id="hcProgress"></div>

  <main class="help-main" id="helpApp">
    <div class="wrap hc-shell">
      <button type="button" class="hc-side-reveal" id="hcSideReveal" aria-label="Show topics" title="Show topics (O)">{svg('book')}<span>Topics</span><kbd class="tab-kbd" aria-hidden="true">O</kbd></button>
      <aside class="hc-side" id="hcSide" aria-label="Help topics">
        <div class="hc-side-title">{svg('book')}<span>Help</span><button type="button" class="hc-side-x" id="hcSideToggle" aria-label="Hide sidebar" title="Hide sidebar (O)">{svg('chev')}<kbd class="tab-kbd" aria-hidden="true">O</kbd></button></div>
        <nav class="hc-nav" id="hcSideNav"></nav>
        <div class="hc-side-cta">
          <b>Can&rsquo;t find an answer?</b>
          <a class="btn btn-primary" href="{SUPPORT_URL}" target="_blank" rel="noopener noreferrer">{svg('send')} Ask in Telegram</a>
        </div>
      </aside>
      <div class="hc-scrim" id="hcScrim"></div>
      <div class="hc-content">
{home_html}
{cats_html}
{arts_html}
        <section class="view" data-view="search" hidden>
          <nav class="hc-crumbs" aria-label="Breadcrumb">
            <a href="#/">Help Center</a>{svg('chev')}
            <span aria-current="page">Search</span>
          </nav>
          <header class="hc-cat-head">
            <span class="hc-ic">{svg('search')}</span>
            <div>
              <h2>Search results</h2>
              <p id="hcSearchMeta"></p>
            </div>
          </header>
          <div class="hc-filters" id="hcSearchFilters" hidden></div>
          <div class="hc-list" id="hcSearchList" hidden></div>
          <div class="hc-sempty" id="hcSearchEmpty" hidden>
            <span class="hc-ic">{svg('search')}</span>
            <h2>No results found for &ldquo;<span id="hcSearchQ"></span>&rdquo;</h2>
            <p>Try other words &mdash; for example <i>recurring posts</i>, <i>sender bot</i> or <i>refund</i>.</p>
            <div class="hc-sug-h">Maybe you meant:</div>
            <div class="hc-list" id="hcSearchSug"></div>
          </div>
        </section>
        <section class="view" data-view="404" hidden>
          <div class="hc-404">
            <span class="hc-ic">{svg('help')}</span>
            <h2>Page not found</h2>
            <p>That topic doesn&rsquo;t exist (or moved). Try the search on the home page.</p>
            <a class="btn btn-primary" href="#/">{svg('home')} Back to Help Center</a>
          </div>
        </section>
      </div>
    </div>
  </main>

  <div class="hc-reel" data-reel hidden aria-hidden="true"><button type="button" data-reel-prev tabindex="-1"><span></span></button><button type="button" data-reel-cur tabindex="-1"><span></span></button><button type="button" data-reel-next tabindex="-1"><span></span></button></div>
  <a class="hc-fab" href="{SUPPORT_URL}" target="_blank" rel="noopener noreferrer" aria-label="Chat with support">{svg('message')}<span>Chat with us</span></a>

<noscript>
  <style>
    .view[hidden] {{ display: block !important; }}
    .hc-search, .hc-search .hc-sbtn, .hc-hsearch, .hc-pager, .hc-side, .hc-fab, .hc-progress {{ display: none !important; }}
  </style>
</noscript>

<footer class="site">
  <div class="wrap foot">
    <div class="links">
      <a href="index.html">Home</a>
      <a href="blog/index.html">Blog</a>
      <a href="legal/privacy.html">Privacy</a>
      <a href="legal/terms.html">Terms</a>
      <a href="legal/refundpolicy.html">Refunds</a>
      <a href="{BOT_URL}" target="_blank" rel="noopener noreferrer">Open Bot</a>
    </div>
    <div class="copy">&copy; {year} Fast Scheduler. All rights reserved.</div>
  </div>
</footer>

<script src="scripts/settings.js?v=20261005d1"></script>
  <script src="scripts/ru-chrome.js?v=20261006b1"></script><script src="scripts/lang.js?v=20261030a1"></script>
<script src="scripts/help-search.js?v=20261030a1"></script>
<script src="scripts/hotkeys-modal.js?v=20261006a1"></script>
<script src="scripts/hotkeys.js?v=20261005d1"></script>
<script src="scripts/scroll-jump.js?v=20261005a1"></script>
<script src="scripts/liquid-nav.js?v=20261005d1"></script>
<script src="scripts/help-data.js?v=20261022a1"></script>
<script src="scripts/help-ai.js?v=20261022a1"></script>
<script src="scripts/help-hub.js?v=20261022a4"></script>
<script src="scripts/site-footer.js?v=20261018g2"></script>
</body>
</html>'''


def main():
    help_sec, _ = load_help_tree()
    page = build_page({}, help_sec)
    with open(OUT_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write(page)
    n_articles = page.count('data-view="article"')
    n_cats = page.count('data-view="category"')
    print(f"[ok] wrote {OUT_PATH} ({n_cats} categories, {n_articles} articles)")


if __name__ == '__main__':
    main()
