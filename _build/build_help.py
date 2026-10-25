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
    'schedule_text', 'schedule_review', 'schedule_one_time',      # folded into Scheduling overview
    'schedule_location', 'schedule_poll_quiz', 'schedule_sticker',
    'schedule_voice', 'schedule_animation', 'schedule_album',
    'schedule_caption', 'schedule_video', 'schedule_document',    # folded into media/advanced articles
    'gs_step1', 'gs_step2', 'gs_step3',                           # folded into Getting Started
    'ms_search', 'ms_from_storage_help',                          # folded into storage guides
    'schedule_edit', 'schedule_delete',                           # folded into Edit/Delete Messages
    'language_sync',                                              # folded into Changing Language
    'timezone_auto', 'timezone_detect', 'timezone_examples',      # folded into timezone guides
    'language_help',                                              # folded into Changing Language
    'website_help', 'website_premium', 'help_about',              # meta pages, not articles
    'website_tour',                                               # meta page, not an article
    'commands_help',                                              # folded into Command List
    'bot_webhook', 'payment_webhook',                             # infra details — no user action
    'bot_isolated', 'security_isolation',                         # architecture notes
    'legal_cookie',                                               # 2-line stub
    'support_hours', 'support_priority',                          # folded into Response Time
    'mt_storage', 'ts_storage',                                   # 2-line stubs, folded into Manage Storage
}
WEB_MERGE_CHILDREN = {
    'scheduling': ['schedule_one_time', 'schedule_text', 'schedule_media', 'schedule_video',
                   'schedule_album', 'schedule_poll', 'schedule_forward', 'schedule_caption',
                   'formatting', 'schedule_review', 'edit', 'delete', 'recurring',
                   'multichannel', 'schedule_advanced'],
    'edit': ['schedule_edit', 'delete'],
    'delete': ['schedule_delete'],
    'schedule_media': ['schedule_album', 'schedule_caption'],
    'schedule_video': ['schedule_animation', 'schedule_voice'],
    'schedule_advanced': ['schedule_location', 'schedule_poll_quiz', 'schedule_sticker',
                          'schedule_voice', 'schedule_animation'],
    'timezone': ['timezone_set', 'timezone_detect', 'timezone_list', 'timezone_examples'],
    'timezone_set': ['timezone_auto'],
    'timezone_list': ['timezone_examples'],
    'language': ['language_change', 'language_list', 'language_sync', 'language_add', 'language_help'],
    'language_change': ['language_help'],
    'edit': ['delete'],
    'bots': ['bot_add', 'bot_manage', 'sender_bot_management', 'bot_permissions', 'bot_sender',
             'bot_status', 'bot_stats', 'bot_webhook', 'bot_rotate', 'bot_remove', 'bot_fleet',
             'bot_isolated'],
    'media_storage': ['storage_use_case', 'ms_boxes', 'ms_save', 'ms_manage', 'ms_limits',
                      'limit_media', 'media_retention', 'storage_lifecycle', 'mt_storage',
                      'ts_storage', 'ms_premium'],
    'ms_save': ['ms_from_storage_help'],
    'ms_manage': ['ms_search'],
    'search': ['search_messages', 'search_filter', 'search_delete'],
    'getting_started': ['getting_started', 'connect_channel', 'connect_bot', 'onboarding_step1',
                        'onboarding_step2', 'start_account', 'start_schedule', 'start_tips'],
    'start': ['getting_started', 'start_account', 'start_schedule', 'start_tips', 'glossary',
              'setdate', 'advertising'],
    # Category with no bot-side children: the web edition groups the
    # personalisation guides here so the card is not empty.
    'config': ['language_change', 'timezone_set', 'signature', 'setdate'],
    'commands': ['commands_list', 'commands_schedule', 'commands_search', 'commands_premium',
                 'commands_referral', 'commands_settings', 'commands_language', 'commands_help'],
    'help': ['help_about', 'website_help', 'website_premium', 'website_tour'],
}
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
    # Legal & Terms: the website already has full legal pages (website/legal/*)
    # linked from the footer — the help-center duplicate was removed.
    for k in list(help_sec):
        if k == 'legal' or k.startswith('legal_'):
            help_sec.pop(k, None)
    root = help_sec.get('root')
    if isinstance(root, dict):
        root['children'] = [c for c in (root.get('children') or []) if c != 'legal']
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
    return (f'<svg{cls_attr} viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{ICONS[name]}</svg>')


def esc(text):
    return html_mod.escape(str(text), quote=True)


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
        'description': strip_storage(node.get('description', '') or ''),
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
    blocks = re.split(r'\n\s*\n', text)
    out = []
    for block in blocks:
        if 'table-scroll' in block:
            out.append(block.strip())
            continue
        lines = [ln.strip() for ln in block.split('\n') if ln.strip()]
        bullets = [ln for ln in lines if ln.startswith(('\u2022', '-', '*'))]
        if bullets and len(bullets) == len(lines):
            items = ''.join('<li>%s</li>' % re.sub(r'^[\u2022\-*]\s*', '', ln) for ln in bullets)
            out.append('<ul>%s</ul>' % items)
        else:
            out.append('<p>%s</p>' % '<br>'.join(lines))
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
        body = re.sub(r'<[^>]+>', ' ', n['content'])
        desc = (n.get('description') or ' '.join(body.split())[:160])
        sections.append({'id': n['id'], 'c': n.get('c', ''), 't': n['title'], 'b': body, 'f': faq, 'd': desc})
    sections += _blog_search_docs()
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
    .view h1:focus { outline: none; } /* a11y focus target, ring is visual noise */
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
      box-shadow: var(--shadow-sm); transition: border-color .2s, color .2s;
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
      width: 100%; height: 40px; padding: 0 42px 0 37px; font: inherit; font-size: .9rem; color: var(--text);
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
    .hc-sug-h { padding: 10px 16px 4px; font-size: .8rem; font-weight: 700; color: var(--text-dim); }
    .hc-sug-h a { color: var(--green-strong); }
    /* "Best result" split: one clear winner gets a labeled hero card, the
       rest stay compact rows below it */
    .hc-res-sec {
      padding: 10px 16px 5px; font-size: .7rem; font-weight: 800;
      letter-spacing: .07em; text-transform: uppercase; color: var(--text-dim);
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
      font-size: .72rem; font-weight: 700; letter-spacing: .08em;
      text-transform: uppercase; color: var(--text-dim);
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
    .hc-chip:hover { border-color: color-mix(in srgb, var(--green) 50%, transparent); color: var(--green-strong); transform: translateY(-1px); box-shadow: var(--shadow-sm); text-decoration: none; }

    /* ---------- browse by topic ---------- */
    .hc-section-h { display: flex; align-items: baseline; gap: 12px; margin: 48px 0 2px; }
    .hc-section-h h2 { font-size: 1.42rem; letter-spacing: -.02em; margin: 0; }
    .hc-section-h span { color: var(--text-dim); font-size: .88rem; }

    .hc-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; padding: 16px 0 8px; }
    @media (max-width: 1020px) { .hc-grid { grid-template-columns: 1fr 1fr; } }
    @media (max-width: 640px)  { .hc-grid { grid-template-columns: 1fr; } }
    .hc-grid > .hc-cat, .hc-list > .hc-row { min-width: 0; }
    .hc-cat { display: block; padding: 18px; color: var(--text); transition: transform .2s, border-color .2s, box-shadow .2s; }
    .hc-cat:hover { text-decoration: none; transform: translateY(-3px); border-color: color-mix(in srgb, var(--green) 45%, var(--border)); box-shadow: var(--shadow); }
    .hc-cat-head { display: flex; align-items: center; gap: 13px; }
    .hc-ic {
      flex: none; width: 46px; height: 46px; border-radius: 13px; display: grid; place-items: center;
      color: var(--green-strong);
      background: color-mix(in srgb, var(--green) 10%, transparent);
      border: 1px solid color-mix(in srgb, var(--green) 22%, transparent);
    }
    .hc-ic svg { width: 22px; height: 22px; }
    .hc-cat-t { font-weight: 800; font-size: .98rem; letter-spacing: -.01em; }
    .hc-cat-c { display: block; font-size: .78rem; color: var(--text-dim); margin-top: 1px; }
    .hc-cat-go { margin-left: auto; color: var(--text-dim); transition: transform .2s, color .2s; }
    .hc-cat-go svg { width: 17px; height: 17px; display: block; }
    .hc-cat:hover .hc-cat-go { color: var(--green-strong); transform: translateX(3px); }
    .hc-cat-prev { margin: 13px 0 0; padding: 11px 0 0; border-top: 1px dashed var(--border); display: flex; flex-direction: column; gap: 5px; }
    .hc-cat-prev span { font-size: .82rem; color: var(--text-dim); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .hc-cat-prev span::before { content: ""; display: inline-block; width: 5px; height: 5px; border-radius: 50%; background: color-mix(in srgb, var(--green) 55%, transparent); margin: 2px 8px 2px 2px; vertical-align: 2px; }

    .hc-home-cta { margin: 40px 0 20px; }

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
    .hc-cat-head h1 { margin: 0; font-size: clamp(1.55rem, 3.4vw, 2.15rem); letter-spacing: -.025em; }
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
    .hc-art > h1 { margin: 0; font-size: clamp(1.65rem, 3.6vw, 2.25rem); letter-spacing: -.025em; line-height: 1.15; }
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
    .hc-toc-navc small { display: block; font-size: .66rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--text-dim); }
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
    .hc-faq summary::after {
      content: "+"; flex: none; font-size: 1.35rem; font-weight: 500; line-height: 1;
      color: var(--green-strong); transition: transform .25s;
    }
    .hc-faq details[open] summary::after { transform: rotate(45deg); }
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

    .hc-pager { max-width: 860px; margin: 16px auto 0; display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
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
      transition: background .18s, box-shadow .22s, color .18s;
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
    }

    /* ---------- 404 ---------- */
    .hc-404 { text-align: center; padding: 90px 0 110px; }
    .hc-404 .hc-ic { margin: 0 auto 18px; width: 60px; height: 60px; border-radius: 18px; }
    .hc-404 .hc-ic svg { width: 28px; height: 28px; }
    .hc-404 h1 { margin: 0 0 8px; font-size: 1.8rem; }
    .hc-404 p { color: var(--text-dim); margin: 0 0 22px; }

    /* ---------- header density on small screens ---------- */
    @media (max-width: 900px) {
      .hc-hsearch { width: auto; flex: 1; min-width: 0; max-width: none; }
      .hc-hsearch kbd { display: none; }
      .hc-brand-help { display: none; }
      .nav-cta span { display: none; }
      .nav-cta { padding: 0 12px; }
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
    /* articles never move under the cursor — depth only */
    .hc-card:hover { box-shadow: var(--shadow); }
    @media (hover: none) {
      .hc-card:active { transform: scale(.985); transition: transform .12s; }
      /* the article card never shrinks on tap: pressing any link inside it made
         the whole page visibly go small then big on navigation */
      .hc-art:active { transform: none; transition: none; }
    }
    .hc-card:hover .hc-ic { transform: rotate(-6deg) scale(1.08); }
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
  try { DATA = JSON.parse(document.getElementById('helpData').textContent); } catch (e) {}
  var SIDE = [];
  try { SIDE = JSON.parse(document.getElementById('helpSide').textContent); } catch (e) {}
  var CATS = {};
  SIDE.forEach(function (c) { CATS[c.id] = c.title; });
  CATS.blog = 'Blog';
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
  }

  function navigate() {
    var r = parseHash();
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
    document.title = r.view === 'search' ? (t + ' — Fast Scheduler Help') :
      (t ? (t + ' — Fast Scheduler Help') : 'Help Center — Fast Scheduler for Telegram');
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
    try { document.dispatchEvent(new CustomEvent('viewchange', { detail: { view: r.view, id: r.id } })); } catch (e) {}
    /* setTimeout, not requestAnimationFrame: rAF can be throttled to never
       inside embedded webviews, which left the search page permanently blank */
    if (r.view === 'search') setTimeout(function () { renderSearchPage(r.id); }, 0);
    document.body.classList.remove('hc-side-open');
    updateProgress();
    if (el) {
      var h1 = el.querySelector('h1');
      if (h1) { h1.setAttribute('tabindex', '-1'); h1.focus({ preventScroll: true }); }
    }
  }

  window.addEventListener('hashchange', navigate);
  navigate();

  /* ---------------- sidebar ---------------- */
  function buildSidebar() {
    if (!sideNav) return;
    var html = '<a class="hc-nav-item" id="hcSideHome" href="#/">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 11l9-8 9 8M5 10v10h14V10"/></svg>' +
      '<span>Help Center home</span></a>';
    SIDE.forEach(function (c) {
      html += '<a class="hc-nav-item" data-cat="' + c.id + '" href="#/c/' + c.id + '">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + c.icon + '</svg>' +
        '<span>' + c.title + '</span><span class="n">' + c.n + '</span></a>';
      if (c.kids && c.kids.length) {
        html += '<div class="hc-subnav" id="hc-sub-' + c.id + '"><div class="hc-subnav-in">';
        c.kids.forEach(function (k) { html += '<a href="#/a/' + k.id + '">' + k.t + '</a>'; });
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
    function render(q, ex, scored) {
      var html = '';
      /* "You mean" is an empty-state aid only — when there are results, the
         Best result card speaks for itself. */
      var top = scored[0], rest = scored.slice(1);
      /* a section split only makes sense when one result clearly dominates */
      var isClear = top.s >= 150 && (!rest.length || top.s >= rest[0].s + 50);
      if (isClear) {
        html += '<div class="hc-res-sec">Best result</div>';
        html += '<button type="button" class="hc-res hc-res-best" role="option" data-art="' + top.sec.id + '">' +
          '<span class="hc-res-top"><span class="hc-res-t">' + markText(top.sec.t, q) + '</span>' +
          '<span class="hc-res-cat">' + escapeHtml(CATS[top.sec.c] || '') + '</span></span>' +
          '<p class="hc-res-s">' + markText(snippet(top.sec.b, q), q) + '</p></button>';
        if (rest.length) {
          html += '<div class="hc-res-sec">More results</div>';
          rest.forEach(function (x) {
            var s = x.sec;
            html += '<button type="button" class="hc-res" role="option" data-art="' + s.id + '">' +
              '<span class="hc-res-top"><span class="hc-res-t">' + markText(s.t, q) + '</span>' +
              '<span class="hc-res-cat">' + escapeHtml(CATS[s.c] || '') + '</span></span></button>';
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
      results.innerHTML = html;
      results.hidden = false;
      input.setAttribute('aria-expanded', 'true');
      resButtons = Array.prototype.slice.call(results.querySelectorAll('.hc-res'));
      curIdx = 0;
      if (resButtons[0]) resButtons[0].classList.add('cur');
    }
    function renderEmpty(q, ex) {
      var ai = aiLabel(q);
      var aiHtml = ai ? '<div class="hc-ai-line"><span class="hc-ai-dot"></span>You mean: <b>' + escapeHtml(ai) + '</b></div>' : '';
      var sug = DATA.filter(function (sec) {
        var t = norm(sec.t);
        return ex.all.some(function (w) {
          return w.length > 2 && (t.indexOf(w) !== -1 || t.split(/\s+/).some(function (x) { return x.indexOf(w) === 0; }));
        });
      }).slice(0, 4);
      var html = '<div class="hc-empty">No exact match for \u201c' + escapeHtml(q) + '\u201d.</div>';
      if (aiHtml) html += aiHtml;
      if (sug.length) {
        html += '<div class="hc-sug-h">Maybe you meant:</div>';
        sug.forEach(function (sg) {
          html += '<button type="button" class="hc-res" role="option" data-art="' + sg.id + '">' +
            '<span class="hc-res-top"><span class="hc-res-t">' + escapeHtml(sg.t) + '</span>' +
            '<span class="hc-res-cat">' + escapeHtml(CATS[sg.c] || '') + '</span></span></button>';
        });
      }
      html += '<div class="hc-sug-h">Still stuck? <a href="__BOTURL__" target="_blank" rel="noopener noreferrer">Ask in the bot</a> \u2014 a human answers every ticket.</div>';
      results.innerHTML = html;
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
      var scored = ranked.slice(0, 8);
      if (!scored.length) renderEmpty(q, ex); else render(q, ex, scored);
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
      if (b) location.hash = '#/a/' + b.getAttribute('data-art');
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
  var CHEV_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9 18 15 12 9 6"/></svg>';

  function docHref(sec) { return sec.href ? sec.href : ('#/a/' + sec.id); }
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
      return '<a class="hc-row" href="#/a/' + sg.id + '"><span class="hc-row-t">' +
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
    var order = Object.keys(present).sort(function (a, b) {
      if (a === 'blog') return -1; if (b === 'blog') return 1; return 0; });
    if (order.length < 2) { el.hidden = true; el.innerHTML = ''; return; }
    el.hidden = false;
    var html = '<button type="button" class="hc-fchip' + (searchCat === 'all' ? ' on' : '') +
      '" data-fcat="all">All</button>';
    order.forEach(function (cid) {
      html += '<button type="button" class="hc-fchip' + (searchCat === cid ? ' on' : '') +
        '" data-fcat="' + escapeHtml(cid) + '">' + escapeHtml(CATS[cid] || cid) + '</button>';
    });
    el.innerHTML = html;
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
    document.title = 'Search: ' + q + ' — Fast Scheduler Help';
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
    hits = hits.slice(0, 40);
    renderSearchFilters(hits, q);
    if (searchMeta) searchMeta.textContent = hits.length
      ? hits.length + ' result' + (hits.length > 1 ? 's' : '') + ' for “' + q + '”'
      : '0 results';
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
          '<span class="hc-best-label">Best result</span>' +
          '<b>' + markText(top.sec.t, norm(q)) + '</b>' +
          '<span class="hc-best-cat">' + escapeHtml(CATS[top.sec.c] || '') + '</span>' +
          '<p>' + markText(snippet(top.sec.b, norm(q)), norm(q)) + '</p></a>';
        if (rest.length) html += '<div class="hc-sempty-h" style="width:100%;max-width:760px;margin:0 auto 6px;text-align:left;grid-column:1/-1;font-size:.8rem;font-weight:700;color:var(--text-dim)">All results</div>';
        html += rest.map(function (x) { return resultRow(x.sec, norm(q)); }).join('');
      } else {
        html = hits.map(function (x) { return resultRow(x.sec, norm(q)); }).join('');
      }
      searchList.innerHTML = html;
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
    var isS = (e.key === 's' || e.key === 'S') && !mod;
    if (isK || isS) { e.preventDefault(); focusSearch(); return; }
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
    if (fab) fab.hidden = !view.querySelector('.hc-toc-list a');
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
def render_faq(faq, link_href, link_label):
    if not faq:
        return ''
    out = ['<div class="hc-faq"><h2>Common questions</h2>']
    for f in faq:
        chips = ''
        if f['links']:
            chips = '<div class="hc-chips" style="margin-top:10px">' + ''.join(
                f'<a class="hc-chip" href="{link_href(l)}"><span>{esc(link_label(l))}</span>{svg("arrow-r")}</a>'
                for l in f['links']) + '</div>'
        out.append(f'<details><summary>{esc_q(f["q"])}</summary>'
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
            f'<a class="hc-cat hc-card" href="#/c/{esc(cat["id"])}">'
            f'<span class="hc-cat-head"><span class="hc-ic">{svg(icon)}</span>'
            f'<span><span class="hc-cat-t">{esc(cat["title"])}</span>'
            f'<span class="hc-cat-c">{count_label}</span></span>'
            f'<span class="hc-cat-go">{svg("arrow-r")}</span></span>{prev}</a>')

    quick_html = ''
    if quick:
        links = ''.join(f'<a href="#/a/{esc(nid)}">{esc(title)}</a>' for nid, title in quick)
        quick_html = f'<div class="hc-quick"><span>Popular:</span>{links}</div>'

    try_chips = ''.join(
        f'<button type="button" class="hc-chip hc-chip-q" data-q="{esc(q)}">{svg("search")}{esc(q)}</button>'
        for q in TRY_ASKING)
    try_html = (f'<div class="hc-try"><div class="hc-try-label">Try asking</div>'
                f'<div class="hc-chiprow">{try_chips}</div></div>') if TRY_ASKING else ''

    return f'''
      <section class="view" data-view="home">
        <div class="hc-hero">
          <span class="hc-kicker">{svg('book')} Help Center</span>
          <h1>How can we <span class="grad">help</span>?</h1>
          <p class="hc-sub">Guides, answers and fixes for Fast Scheduler &mdash; scheduling, recurring posts, sender bots, channels, statistics and payments. Search it or browse by topic.</p>
          <div class="hc-search">
            {svg('search', 'sic')}
            <input id="hcSearch" type="search" placeholder="Search articles&hellip;" aria-label="Search help topics" autocomplete="off" aria-expanded="false" aria-controls="hcResults" enterkeyhint="search">
            <button class="hc-sbtn" id="hcSBtn" type="button" aria-label="Search (press S)" title="Search (press S)">S</button>
            <div class="hc-results" id="hcResults" role="listbox" aria-label="Search results" hidden></div>
          </div>
          {try_html}
        </div>
        <div class="hc-section-h" style="padding-top:44px"><h2>Browse by topic</h2><span>{n_articles} articles &middot; {len(groups)} categories</span></div>
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
            return f'#/a/{esc(lid)}'
        if target and target.get('title'):
            return f'#/c/{esc(lid)}'
        return '#/'

    def link_label(lid):
        target = by_id.get(lid)
        if target and target.get('title'):
            return target['title']
        return lid.replace('_', ' ').strip().title()

    rows = []
    if kids:
        if art_eligible(cat):
            rows.append(f'<a class="hc-row hc-row-lead" href="#/a/{esc(cat["id"])}">'
                        f'<span class="hc-row-t">Overview: {esc(cat["title"])}</span>'
                        f'<span class="hc-row-m">Start here</span>{svg("chev")}</a>')
        for n in kids:
            if not art_eligible(n):
                continue
            meta = f'{len(n["faq"])} Q&amp;A' if n['faq'] else 'Guide'
            rows.append(f'<a class="hc-row" href="#/a/{esc(n["id"])}">'
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
                    rows.append(f'<a class="hc-row" href="#/a/{esc(lid)}">'
                                f'<span class="hc-row-t">{esc(t["title"])}</span>'
                                f'<span class="hc-row-m">{meta}</span>{svg("chev")}</a>')
        if not rows:
            for o in groups:
                if o['cat']['id'] == cat['id'] or not o['kids']:
                    continue
                rows.append(f'<a class="hc-row" href="#/c/{esc(o["cat"]["id"])}">'
                            f'<span class="hc-row-t">{esc(o["cat"]["title"])}</span>'
                            f'<span class="hc-row-m">Category</span>{svg("chev")}</a>')

    intro = text_to_html(cat['content']) if cat['content'] else ''
    intro_html = f'<div class="hc-intro">{intro}</div>' if intro else ''
    faq_html = render_faq(cat['faq'], link_href, link_label) if (cat['faq'] and art_eligible(cat)) else ''

    others = ''.join(
        f'<a href="#/c/{esc(o["cat"]["id"])}">{esc(o["cat"]["title"])}</a>'
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
            <h1>{esc(cat["title"])}</h1>
            <p>{n_label}</p>
          </div>
        </header>
        {intro_html}
        <div class="hc-section-h"><h2>All articles</h2><span>{n_label}</span></div>
        <div class="hc-list">
          {''.join(rows)}
        </div>
        {faq_html}
        <div class="hc-others"><span>Other categories:</span>{others}</div>
      </section>'''


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
    faq_html = render_faq(n['faq'], link_href, link_label)

    # Anchor every <h3> so the "On this page" rail and Contents sheet can link to it.
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

    if n.get('_raw_html'):
        body = re.sub(r'<h3>(.*?)</h3>', _h3_sub, body, flags=re.S)
    toc_list = ''
    if jump_secs:
        toc_list = ''.join(f'<li><a href="#/a/{esc(n["id"])}" data-jid="{esc(sid)}" data-toc-link>{esc(lbl)}</a></li>'
                           for sid, lbl in jump_secs[:6])

    related = []
    seen = set()
    for f in n['faq']:
        for lid in f['links']:
            if lid in seen or lid == n['id']:
                continue
            target = by_id.get(lid)
            if not target or not (art_eligible(target) or target.get('title')):
                continue
            seen.add(lid)
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

    return f'''
      <section class="view" data-view="article" data-art="{esc(n["id"])}" hidden>
        {crumbs}
        <article class="hc-art hc-card">
          <h1>{esc(n["title"])}</h1>
          <div class="hc-body">{body}</div>
          {faq_html}
          {related_html}
        </article>
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
        {pager_html}
        <div class="hc-cta">
          <div><b>Still stuck?</b><p>The in-bot assistant answers the same questions &mdash; and a human reads every ticket.</p></div>
          <a class="btn" href="{BOT_URL}" target="_blank" rel="noopener noreferrer">{svg('send')} Ask in Telegram</a>
        </div>
      </section>'''


FAVICON = (
    '<link rel="icon" href="{rel}/favicon.ico" sizes="any">\n'
    '  <link rel="icon" href="{rel}/favicon.svg" type="image/svg+xml">\n'
    '  <link rel="icon" href="{rel}/favicon-32.png" sizes="32x32" type="image/png">\n'
    '  <link rel="icon" href="{rel}/icon-48.png" sizes="48x48" type="image/png">\n'
    '  <link rel="icon" href="{rel}/favicon-16.png" sizes="16x16" type="image/png">\n'
    '  <link rel="icon" href="{rel}/brand-logo.png" sizes="256x256" type="image/png">\n'
    '  <link rel="apple-touch-icon" href="{rel}/apple-touch-icon.png" sizes="180x180">\n'
    '  <link rel="manifest" href="{rel}/site.webmanifest">'
)


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
    arts_html = '\n'.join(
        render_article(n, next(g for g in groups if n in g['kids'] or n is g['cat'] or n['id'] == g['cat']['id']),
                       by_id, order_index)
        + article_faq_ld(n)
        for n in article_order)

    side_payload = json.dumps([
        {'id': g['cat']['id'], 'title': g['cat']['title'],
         'n': len(g['kids']) + (1 if art_eligible(g['cat']) else 0),
         'icon': ICONS[CAT_ICONS.get(g['cat']['id'], DEFAULT_ICON)],
         'kids': [{'id': k['id'], 't': k['title']} for k in g['kids'] if art_eligible(k)][:8]}
        for g in groups if g['cat']['id'] != 'misc'], ensure_ascii=False)
    search_payload = build_search_json(article_order, groups)
    year = datetime.date.today().year
    n_cats = len(groups)

    return f'''<!doctype html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#1faa59">
  <meta name="color-scheme" content="light dark">
  <title>Help Center — Fast Scheduler for Telegram</title>
  <meta name="description" content="Searchable help center for Fast Scheduler: scheduling, recurring posts, sender bots, channels, statistics, premium and payments. {len(article_order)} answers, instantly searchable.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://fastscheduler.github.io/help.html">
  <link rel="describedby" href="https://fastscheduler.github.io/llms.txt">
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
    }} catch (e) {{}}
  </script>
  <link rel="preload" href="fonts/space-grotesk-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="styles/main.css?v=20261013m3">
  <link rel="stylesheet" href="styles/lang.css?v=20261001a1"">
  <link rel="stylesheet" href="styles/liquid-nav.css?v=20260930a1">
<link rel="stylesheet" href="styles/hotkeys-modal.css?v=20261006a1">
  <style>{CSS}
  </style>
</head>
<body class="help">
  <a class="skip-link" href="#helpApp">Skip to main content</a>
<header class="site">
  <div class="wrap nav">
      <button class="icon-btn hc-menu-btn" id="hcMenuBtn" aria-label="Open navigation" aria-controls="hcSideNav">{svg('menu')}</button>
      <a class="brand brand-text" href="index.html" aria-label="Fast Scheduler — home"><span class="brand-mark">{svg('calendar')}</span><span class="brand-full">Fast Scheduler</span><span class="hc-brand-help">Help Center</span></a>
      <div class="hc-hsearch">
        {svg('search', 'sic')}
        <input id="hcSearchH" type="search" placeholder="Search articles" aria-label="Search help articles" autocomplete="off" aria-expanded="false" aria-controls="hcResultsH" enterkeyhint="search">
        <kbd>S</kbd>
        <div class="hc-results" id="hcResultsH" role="listbox" aria-label="Search results" hidden></div>
      </div>
      <a class="btn btn-primary nav-cta" data-cta-short="Open" href="{BOT_URL}" target="_blank" rel="noopener noreferrer">{svg('send')}<span>Open Bot</span></a>
      <span class="settings-wrap">
        <button type="button" class="icon-btn" id="settingsBtn" aria-haspopup="menu" aria-expanded="false" aria-label="Settings" data-hk="settings dark anim fx keys">{svg('gear')}</button>
        <div class="glass-pop" id="settingsMenu" role="menu" aria-label="Settings">
          <div class="gp-head">Settings</div>
          <button type="button" class="gp-row" role="menuitemcheckbox" aria-checked="false" id="rowDark">{svg('moon')}<span>Dark mode</span><span class="io-switch" aria-hidden="true"></span></button>
          <button type="button" class="gp-row" role="menuitemcheckbox" aria-checked="true" id="rowAnim">{svg('zap')}<span>Animations</span><span class="io-switch" aria-hidden="true"></span></button>
          <button type="button" class="gp-row" role="menuitemcheckbox" aria-checked="true" id="rowFx">{svg('sparkles')}<span>Effects</span><span class="io-switch" aria-hidden="true"></span></button>
          <button type="button" class="gp-row" role="menuitemcheckbox" aria-checked="true" id="rowKeys">{svg('keys')}<span>Hotkeys</span><span class="io-switch" aria-hidden="true"></span></button>
          <button type="button" class="gp-row gp-row-sub" id="rowKeysHelp" role="menuitem"><svg viewBox="0 0 24 24" fill="none" stroke="none" aria-hidden="true" style="visibility:hidden;width:18px;height:18px"></svg><span class="gp-sub-label">See hotkeys</span><svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9 18 15 12 9 6"/></svg></button>
          <div class="gp-sep" role="separator"></div>
          <span class="site-menu-wrap"><a class="gp-row site-menu-row" role="menuitem" href="index.html">{svg('home')}<span>Main site</span>{svg('chev')}</a>
            <div class="glass-pop site-menu-pop help-menu" id="siteMenu" role="menu" aria-label="Help center quick search">
              <form class="help-search" id="helpSearchForm" role="search">
                {svg('search', 'sic')}
                <input type="search" id="helpSearchInput" placeholder="Search the help center…" autocomplete="off" aria-label="Search the help center">
              </form>
              <div class="help-recent">
                <div class="help-recent-title" id="helpRecentTitle">Popular articles</div>
                <div class="help-recent-list" id="helpRecentList"></div>
              </div>
              <a class="gp-row help-menu-open" role="menuitem" href="index.html">{svg('home')}<span>Open main site</span>{svg('chev')}</a>
            </div>
          </span>
          <a class="gp-row" role="menuitem" href="https://t.me/FastSchedulerSupport_bot" target="_blank" rel="noopener noreferrer">{svg('send')}<span>Support chat</span>{svg('chev')}</a>
        </div>
      </span>
    </div>
  </header>
  <div class="hc-progress" id="hcProgress"></div>

  <main class="help-main" id="helpApp">
    <div class="wrap hc-shell">
      <button type="button" class="hc-side-reveal" id="hcSideReveal" aria-label="Show topics" title="Show topics (O)">{svg('book')}<span>Topics</span><kbd class="tab-kbd" aria-hidden="true">O</kbd></button>
      <aside class="hc-side" id="hcSide" aria-label="Help topics">
        <div class="hc-side-title">{svg('book')}<span>All topics</span><button type="button" class="hc-side-x" id="hcSideToggle" aria-label="Hide sidebar" title="Hide sidebar (O)">{svg('chev')}<kbd class="tab-kbd" aria-hidden="true">O</kbd></button></div>
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
              <h1>Search results</h1>
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
            <h1>Page not found</h1>
            <p>That topic doesn&rsquo;t exist (or moved). Try the search on the home page.</p>
            <a class="btn btn-primary" href="#/">{svg('home')} Back to Help Center</a>
          </div>
        </section>
      </div>
    </div>
  </main>

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

<script id="helpSide" type="application/json">{side_payload}</script>
<script id="helpData" type="application/json">{search_payload}</script>
<script src="scripts/settings.js?v=20260930a1"></script>
  <script src="scripts/lang.js?v=20261001a1"></script>
<script src="scripts/help-search.js?v=20260930a1"></script>
<script src="scripts/hotkeys-modal.js?v=20261006a1"></script>
<script src="scripts/hotkeys.js?v=20260930a1"></script>
<script src="scripts/scroll-jump.js?v=20260930a1"></script>
<script src="scripts/liquid-nav.js?v=20260930a1"></script>
<script src="scripts/help-ai.js?v=20260930a1"></script>
<script>{JS.replace('__BOTURL__', SUPPORT_URL)}</script>
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
