"""Build the marketing website assets from the bot's single source of truth.

Run from the repo root:

    python website/_build/build_site.py

It:
  1. Reads plan limits + prices from ``src/core/plans.py`` and ``src/core/config.py``
     and writes them to ``website/scripts/site-config.js`` (so the site and bot
     never drift).
  2. Converts ``docs/privacy.md``, ``docs/terms.md`` and ``docs/refundpolicy.md``
     into styled HTML pages under ``website/legal/``.
"""

import os
import re
import sys
import json
import datetime
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

from src.core.config import (  # noqa: E402
    PREMIUM_PRICE_MONTHLY_CENTS,
    PREMIUM_PRICE_YEARLY_CENTS,
    PREMIUM_DISCOUNT_3M_PERCENT,
    PREMIUM_DISCOUNT_6M_PERCENT,
    MAIN_BOT_USERNAME,
)
from src.core.plans import (  # noqa: E402
    FREE_LIMITS,
    PREMIUM_LIMITS,
    LIMIT_LABELS,
    format_limit_value,
    MEDIA_STORAGE_ENABLED,
    get_comparison_kwargs,
    STORAGE_ROW_LABELS,
    STORAGE_MARKER,
)

import markdown  # noqa: E402
import site_i18n as _i18n  # noqa: E402

_TOOLS = os.path.join(REPO_ROOT, 'tools')
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)
import legal_versions as _lv  # noqa: E402

WEBSITE_DIR = os.path.join(REPO_ROOT, 'website')
_BUILD_DIR = os.path.join(WEBSITE_DIR, '_build')
if _BUILD_DIR not in sys.path:
    sys.path.insert(0, _BUILD_DIR)
import build_help as _bh  # noqa: E402  (shared entity/JSON-LD helpers)
LEGAL_DIR = os.path.join(WEBSITE_DIR, 'legal')
DOCS_DIR = os.path.join(REPO_ROOT, 'docs')
SCRIPTS_DIR = os.path.join(WEBSITE_DIR, 'scripts')

BOT_USERNAME = MAIN_BOT_USERNAME.lstrip('@')
MAIL = os.getenv('SITE_MAIL', 'support@fastestschedule.com')

# Limits surfaced on the pricing page, in display order.
DISPLAY_ORDER = [
    'channels', 'bots', 'scheduled_messages', 'recurring_messages',
    'daily_messages', 'media_storage_count', 'media_items_total',
    'max_video_size_mb', 'multi_schedule', 'statistics', 'leaderboard',
    'backup_export', 'search', 'calendar',
]


def money(cents: int) -> str:
    return f"${cents / 100:.2f}"


def build_prices():
    monthly = PREMIUM_PRICE_MONTHLY_CENTS
    yearly = PREMIUM_PRICE_YEARLY_CENTS
    yearly_monthly = yearly / 12  # cents
    savings = round((1 - (yearly_monthly / monthly)) * 100)
    # Prepaid terms use the same discount engine as the bot: percent off
    # N x monthly, single-sourced from src.core.config (env-driven).
    d3 = PREMIUM_DISCOUNT_3M_PERCENT
    d6 = PREMIUM_DISCOUNT_6M_PERCENT
    m3 = int(round(monthly * 3 * (1.0 - d3 / 100.0)))
    m6 = int(round(monthly * 6 * (1.0 - d6 / 100.0)))
    return {
        'monthlyCents': monthly,
        'yearlyCents': yearly,
        'm3Cents': m3, 'm3DiscountPercent': int(d3),
        'm6Cents': m6, 'm6DiscountPercent': int(d6),
        'monthlyUSD': money(monthly),
        'm3USD': money(m3),
        'm6USD': money(m6),
        'yearlyUSD': money(yearly),
        'yearlyMonthlyEquivalentUSD': money(yearly_monthly),
        'savingsPercent': savings,
    }


def build_plans():
    rows = []
    for key in DISPLAY_ORDER:
        label = LIMIT_LABELS.get(key, key)
        fv = FREE_LIMITS.get(key)
        pv = PREMIUM_LIMITS.get(key)
        rows.append({
            'key': key,
            'label': label,
            'free': format_limit_value(fv),
            'premium': format_limit_value(pv),
            'freeIncluded': bool(fv),
            'premiumIncluded': bool(pv),
        })
    return rows


def _comparison_filled():
    """Return premium_comparison_rich with all plan-limit + price placeholders filled.

    The plan-limit values come from ``get_comparison_kwargs()`` (single source of
    truth in plans.py), so editing a limit updates the bot AND the website.
    When Media Storage is disabled, its rows/bonuses are stripped here so the
    site reflects the toggle automatically.
    """
    en = _load_en()
    rich = en.get('premium_comparison_rich') or (en.get('premium', {}) or {}).get('comparison_rich', '')
    monthly = PREMIUM_PRICE_MONTHLY_CENTS / 100
    yearly = PREMIUM_PRICE_YEARLY_CENTS / 100
    saved = monthly * 12 - yearly
    months_free = int(round(saved / monthly)) if monthly else 0
    percent = round(saved / (monthly * 12) * 100) if monthly else 0
    savings_text = f"{months_free} MONTHS FREE - Save {percent}%" if saved > 0 else ""
    kwargs = get_comparison_kwargs(dash_empty=True)
    _support_bot = os.getenv('SUPPORT_BOT_USERNAME', 'FastSchedulerSupport_bot').lstrip('@')
    _support_url = f'https://t.me/{_support_bot}?start=help_premium'
    kwargs.update(
        monthly_label=f"${monthly:.2f}/month",
        yearly_label=f"${yearly:.2f}/year",
        yearly_savings=savings_text,
        reports_free=kwargs['limit_report_schedules_free'],
        reports_prem=kwargs['limit_report_schedules_prem'],
        support_url=_support_url,
    )
    try:
        rich = rich.format(**kwargs)
    except Exception:
        pass
    # Keep storage rows in the HTML at all times; visibility is controlled at
    # runtime by the live storage state (data-feature="storage" + main.js fetch).
    # Just strip the @@STORAGE@@ markers so the table text is clean.
    rich = rich.replace(STORAGE_MARKER, '')
    return rich


def _cell(text):
    """Return (clean_value, included) for a comparison-table cell."""
    included = True
    if '❌' in text:
        included = False
    working = text.replace('✅', '').replace('❌', '').replace('⭐', '')
    working = re.sub(r'^\?\s*', '', working).strip()
    if working in ('', '?'):
        # Bare ✅ / ❌ with no text → "Yes" / "No".
        working = 'Yes' if '✅' in text else 'No'
    if 'Forbidden' in working:
        included = False
    return working, included


def parse_comparison_rows():
    """Parse premium_comparison_rich into plan-card rows (same set as the table).

    This is the single source for both the pricing cards and the comparison
    table, so they always list exactly the same features.
    """
    rich = _comparison_filled()
    rows = []
    table_lines = [ln for ln in rich.splitlines() if ln.strip().startswith('|')]
    # table_lines[0] = header, table_lines[1] = alignment row
    for ln in table_lines[2:]:
        cells = [c.strip() for c in ln.strip().strip('|').split('|')]
        if len(cells) < 3:
            continue
        label = re.sub(r'\*\*', '', cells[0]).strip()
        if not label or label.lower() == 'feature':
            continue
        if label == 'Price':
            continue  # price is shown separately on the cards
        free_val, free_inc = _cell(cells[1])
        prem_val, prem_inc = _cell(cells[2])
        rows.append({
            'label': label,
            'free': free_val,
            'premium': prem_val,
            'freeIncluded': free_inc,
            'premiumIncluded': prem_inc,
            'storage': label in STORAGE_ROW_LABELS,
        })
    return rows


def _load_en():
    path = os.path.join(REPO_ROOT, 'translations', 'en.json')
    with open(path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def _placeholders():
    """Editable values surfaced in the legal docs. Edit them in site-config.js."""
    return {
        'OPERATOR_LEGAL_NAME': os.getenv('OPERATOR_LEGAL_NAME', 'Fast Scheduler'),
        'OPERATOR_REGISTERED_ADDRESS': os.getenv('OPERATOR_REGISTERED_ADDRESS', '—'),
        'COMPANY_REGISTRATION_NUMBER': os.getenv('COMPANY_REGISTRATION_NUMBER', '—'),
        'PRIVACY_CONTACT_EMAIL': os.getenv('PRIVACY_CONTACT_EMAIL', 'privacy@fastestschedule.com'),
        'SUPPORT_TELEGRAM_HANDLE_OR_LINK': os.getenv('SUPPORT_TG', '@FastSchedulerBot'),
        'WEBSITE': os.getenv('WEBSITE_URL', 'https://fastscheduler.github.io'),
        'CONTACT_EMAIL': os.getenv('CONTACT_EMAIL', 'support@fastestschedule.com'),
        'LEGAL_CONTACT_EMAIL': os.getenv('LEGAL_CONTACT_EMAIL', 'legal@fastestschedule.com'),
        'GOVERNING_JURISDICTION': os.getenv('GOVERNING_JURISDICTION', 'your jurisdiction'),
        'JURISDICTION_VENUE': os.getenv('JURISDICTION_VENUE', 'local courts'),
        'RESPONSE_WINDOW_EG_5_BUSINESS_DAYS': os.getenv('RESPONSE_WINDOW', '5 business days'),
        'EG_5_10_BUSINESS_DAYS': '5–10 business days',
        'EG_7_BUSINESS_DAYS': '7 business days',
        'DATE': datetime.date.today().strftime('%B %d, %Y'),
        'KV_NAMESPACES': 'your Cloudflare account',
    }


def _tag_storage_rows(html):
    """Add ``data-feature="storage"`` to comparison rows that belong to Media Storage.

    ``main.js`` then hides those rows when storage is disabled at runtime.
    """
    def repl(m):
        tr = m.group(0)
        first = re.search(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.S)
        if not first:
            return tr
        label = re.sub(r'<[^>]+>', '', first.group(1)).replace('**', '').strip()
        if label in STORAGE_ROW_LABELS:
            return tr.replace('<tr>', '<tr data-feature="storage">', 1)
        return tr
    return re.sub(r'<tr>.*?</tr>', repl, html, flags=re.S)


def build_comparison():
    """Render the bot's premium comparison (premium_comparison_rich) to HTML.

    Emoji (✅/❌/⭐) are replaced with SVG icons at build time so the page
    never ships emoji; leftover "?" placeholders become an em dash. Storage rows
    are tagged so they can be hidden when Media Storage is disabled.
    """
    html = markdown.markdown(_comparison_filled(), extensions=['tables', 'fenced_code'])
    html = (html
            .replace('✅', _svg_icon('check'))
            .replace('❌', _svg_icon('x'))
            .replace('⭐', _svg_icon('star'))
            .replace('? ', '')
            .replace('?', '—'))
    return _tag_storage_rows(html)


def write_site_config():
    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    prices = build_prices()
    plans = parse_comparison_rows()
    placeholders = _placeholders()
    comparison_html = build_comparison()
    _m = PREMIUM_PRICE_MONTHLY_CENTS / 100
    _y = PREMIUM_PRICE_YEARLY_CENTS / 100
    _saved = _m * 12 - _y
    _months_free = int(round(_saved / _m)) if _m else 0
    savings_text = f"{_months_free} MONTHS FREE - Save {prices['savingsPercent']}%"
    # Render placeholders/comparison as JS string literals (escape backticks/backslashes).
    ph_js = json.dumps(placeholders, ensure_ascii=False)
    comp_js = json.dumps(comparison_html, ensure_ascii=False)
    rows_js = json.dumps(plans, ensure_ascii=False)
    js = f"""// AUTO-GENERATED by website/_build/build_site.py — do not edit by hand.
// Source of truth: src/core/plans.py, src/core/config.py, translations/en.json
window.SITE_CONFIG = {{
  botUsername: "{BOT_USERNAME}",
  mail: "{MAIL}",
  mediaStorageEnabled: {MEDIA_STORAGE_ENABLED},
  prices: {{
    monthlyCents: {prices['monthlyCents']},
    m3Cents: {prices['m3Cents']}, m3DiscountPercent: {prices['m3DiscountPercent']},
    m6Cents: {prices['m6Cents']}, m6DiscountPercent: {prices['m6DiscountPercent']},
    yearlyCents: {prices['yearlyCents']},
    monthlyUSD: "{prices['monthlyUSD']}",
    m3USD: "{prices['m3USD']}", m6USD: "{prices['m6USD']}",
    yearlyUSD: "{prices['yearlyUSD']}",
    yearlyMonthlyEquivalentUSD: "{prices['yearlyMonthlyEquivalentUSD']}",
    savingsPercent: {prices['savingsPercent']},
    savingsText: "{savings_text}"
  }},
  plans: {{
    free: {{ label: "Free", priceMonthly: "$0", priceYearly: "$0" }},
    premium: {{
      label: "Premium",
      priceMonthly: "{prices['monthlyUSD']}",
      priceYearly: "{prices['yearlyUSD']}",
      priceYearlyMonthly: "{prices['yearlyMonthlyEquivalentUSD']}",
      savingsPercent: {prices['savingsPercent']}
    }},
    rows: {plans!r}
  }},
  placeholders: {ph_js},
  comparisonHTML: {comp_js},
  comparisonRows: {rows_js}
}};
"""
    # Make the JS valid: convert Python repr (True/False/None) to JS.
    # Use word boundaries so real strings like "Attribute" are never mangled.
    js = re.sub(r'\bTrue\b', 'true', js)
    js = re.sub(r'\bFalse\b', 'false', js)
    js = re.sub(r'\bNone\b', 'null', js)
    path = os.path.join(SCRIPTS_DIR, 'site-config.js')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(js)
    print(f"[ok] wrote {path}")

    # Emit the live storage state file the bot also writes on every toggle. This
    # gives the website a correct initial value (matching the build default) so
    # main.js can reflect Media Storage state before the first admin toggle.
    try:
        state_path = os.path.join(WEBSITE_DIR, 'storage_state.json')
        with open(state_path, 'w', encoding='utf-8') as f:
            # Public file: boolean flag only. No timestamps, sources, or
            # metadata - anything else in here is visible to every visitor.
            json.dump(
                {
                    'mediaStorageEnabled': bool(MEDIA_STORAGE_ENABLED),
                },
                f, ensure_ascii=False, indent=2,
            )
        print(f"[ok] wrote {state_path}")
    except Exception as e:
        print(f"[skip] storage_state.json: {e}")


ICONS = {
    'gear': '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33h0a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51h0a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v0a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
    'sparkles': '<path d="M12 3l1.9 5.8a2 2 0 0 0 1.3 1.3L21 12l-5.8 1.9a2 2 0 0 0-1.3 1.3L12 21l-1.9-5.8a2 2 0 0 0-1.3-1.3L3 12l5.8-1.9a2 2 0 0 0 1.3-1.3z"/>',
    'keys':      '<rect x="2" y="6" width="20" height="12" rx="2.5"/><path d="M6.5 10h.01M10.5 10h.01M14.5 10h.01M18 10h.01M8 13.5h8"/>',
    'book': '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    'chev': '<polyline points="9 18 15 12 9 6"/>',
    'home': '<path d="M3 11l9-8 9 8M5 10v10h14V10"/>',
    'star': '<path d="M12 2l3 7h7l-5.5 4.5L18 21l-6-4-6 4 1.5-7.5L3 9h7z"/>',
    'tag': '<path d="M3 3h8l9 9-8 8-9-9zM7 7a1.5 1.5 0 110-3 1.5 1.5 0 010 3z"/>',
    'mail': '<path d="M3 5h18v14H3zM3 7l9 6 9-6"/>',
    'scale': '<path d="M12 3v18M6 21h12M5 7h14l-2 6H7zM12 3l-7 4 7 4 7-4z"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M19 5l-1.5 1.5M6.5 17.5L5 19"/>',
    'moon': '<path d="M21 13A9 9 0 1111 3a7 7 0 0010 10z"/>',
    'check': '<path d="M5 13l4 4L19 7"/>',
    'rocket': '<path d="M5 15c-2 2-3 7-3 7s5-1 7-3M9 11a8 8 0 018-8c2 0 3 1 3 3a8 8 0 01-8 8l-3-3zM14 9a1.5 1.5 0 110-3 1.5 1.5 0 010 3z"/>',
    'calendar': '<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M3 9h18M8 2v4M16 2v4"/>',
    'repeat': '<path d="M17 2l4 4-4 4M3 11V9a4 4 0 014-4h14M7 22l-4-4 4-4M21 13v2a4 4 0 01-4 4H3"/>',
    'channels': '<path d="M3 6h18v12H3zM7 10h6M7 14h4"/>',
    'media': '<path d="M3 5h18v14H3zM3 16l5-5 4 4 3-3 6 6"/><circle cx="8" cy="9" r="1.5"/>',
    'chart': '<path d="M4 20V4M4 20h16M8 16v-5M12 16V8M16 16v-9"/>',
    'shield': '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>',
    'bolt': '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
    'send': '<path d="M22 2L11 13M22 2l-7 20-4-9-9-4z"/>',
    'search': '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>',
    'arrow': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'lock': '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/>',
    'x': '<path d="M6 6l12 12M18 6L6 18"/>',
}


def svg(name, cls=''):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')


def _svg_icon(name):
    """Full <svg> markup for a yes/no/star cell icon used in the comparison table."""
    cls = {'check': 'yes', 'x': 'no', 'star': 'star'}.get(name, name)
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{ICONS[name]}</svg>')


BOT_DEEP_LINK = f'https://t.me/{BOT_USERNAME}'

def _ui(lang, key, **fmt):
    """A legal-page UI string from translations/website/<lang>.json."""
    return _i18n.t(lang, 'legal', 'ui', key, **fmt)


RU_MONTHS = ('января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
             'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря')


def fmt_date(iso, lang='en'):
    """2026-10-26 -> 'October 26, 2026' / '26 октября 2026'."""
    y, mo, d = (int(x) for x in iso.split('-'))
    if lang == 'ru':
        return '%d %s %d' % (d, RU_MONTHS[mo - 1], y)
    return datetime.date(y, mo, d).strftime('%B %d, %Y').replace(' 0', ' ')


def _alt_links(doc):
    """hreflang cluster for the pair of documents, identical in both."""
    en = 'https://fastscheduler.github.io/legal/%s.html' % doc
    ru = 'https://fastscheduler.github.io/ru/legal/%s.html' % doc
    return ('<link rel="alternate" hreflang="en" href="%s">\n'
            '<link rel="alternate" hreflang="ru" href="%s">\n'
            '<link rel="alternate" hreflang="x-default" href="%s">\n'
            % (en, ru, en))


def _legal_tabs(current, lang):
    """The three document tabs, one template for every language."""
    out = []
    for name in ('privacy', 'terms', 'refundpolicy'):
        cls = 'doc-tab active' if name == current else 'doc-tab'
        out.append('<a class="%s" href="%s.html">%s</a>'
                   % (cls, name, _ui(lang, 'tab_' + name)))
    return ''.join(out)


def _legal_nav(current, lang='en'):
    """The shared navbar with the document tabs in its centre slot.

    Built from bh.unified_nav() — the same component the help centre and the
    blog use — so the legal chrome cannot drift from the rest of the site.
    """
    pre = '..' if lang == 'en' else '../..'          # asset prefix
    t = lambda k: _ui(lang, k)                        # noqa: E731
    tabs = ('<nav class="doc-tabs" aria-label="%s">%s</nav>'
            % (t('docs_aria'), _legal_tabs(current.replace('.html', ''), lang)))
    cta = ('<a class="btn btn-primary nav-cta has-tip" data-cta-short="%s" '
           'data-tip="%s" href="%s?start=start__legal" target="_blank" '
           'rel="noopener noreferrer">%s<span>%s</span>'
           '<kbd class="tab-kbd" aria-hidden="true">B</kbd></a>'
           % (_bh.tr('open_short', lang), t('cta_tip'), BOT_DEEP_LINK,
              svg('send'), _bh.tr('open_bot', lang)))
    return _bh.unified_nav(pre, BOT_DEEP_LINK, _bh.settings_menu(_bh.SUPPORT_URL, lang),
                           center_extra=tabs, cta_html=cta, lang=lang,
                           with_search=False)


def _legal_footer(lang='en'):
    t = lambda k: _bh.tr(k, lang)                     # noqa: E731
    return f'''
<footer class="site">
  <div class="wrap foot">
    <div class="links">
      <a href="../index.html">{t('footer_home')}</a>
      <a href="../blog/index.html">{t('blog')}</a>
      <a href="../help.html">{t('help_center')}</a>
      <a href="privacy.html">{t('footer_privacy')}</a>
      <a href="terms.html">{t('footer_terms')}</a>
      <a href="refundpolicy.html">{t('footer_refunds')}</a>
      <a href="{BOT_DEEP_LINK}" target="_blank" rel="noopener noreferrer">{t('footer_open')}</a>
    </div>
    <div class="copy">{t('footer_copy')}</div>
  </div>
</footer>'''


CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline' "
       "https://www.googletagmanager.com; style-src 'self' 'unsafe-inline'; "
       "img-src 'self' data: https://www.googletagmanager.com "
       "https://*.google-analytics.com https://*.analytics.google.com "
       "https://www.google.com; font-src 'self'; connect-src 'self' "
       "https://www.googletagmanager.com https://*.google-analytics.com "
       "https://*.analytics.google.com https://region1.google-analytics.com "
       "https://www.google.com; frame-src https://www.googletagmanager.com; "
       "object-src 'none'; form-action 'self'; base-uri 'self'; "
       "upgrade-insecure-requests")

LEGAL_JS = r'''/* C = toggle the Contents sidebar (desktop only) */
(function () {
  /* C = show/hide the Contents panel. FS_KEYS (settings.js) owns the site-wide
     Hotkeys switch and the "never fire while typing" rule, exactly as it does
     for the rail, the jump button and the help center; the inline checks are
     the fallback for a page that does not load settings.js. */
  document.addEventListener('keydown', function (e) {
    if (window.innerWidth <= 860) return;
    if (e.key !== 'c' && e.key !== 'C') return;
    var K = window.FS_KEYS;
    if (K) {
      if (!K.allow(e)) return;
    } else {
      if (document.documentElement.getAttribute('data-keys') === 'off') return;
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      var el = document.activeElement;
      var tag = (el && el.tagName) || '';
      if (tag === 'INPUT' || tag === 'TEXTAREA' || (el && el.isContentEditable)) return;
    }
    var tab = document.getElementById('tocSideTab');
    if (!tab) return;
    e.preventDefault();
    tab.click();
  });
})();
</script>
<script>
(function () {
  var burger = document.getElementById('tocBurger');
  var sheet = document.getElementById('tocSheet');
  var overlay = document.getElementById('tocOverlay');
  var closeBtn = document.getElementById('tocClose');
  if (!burger || !sheet || !overlay) return;
  function openSheet() { sheet.classList.add('open'); overlay.classList.add('open'); sheet.scrollTop = 0; }
  function closeSheet() { sheet.classList.remove('open'); overlay.classList.remove('open'); }
  burger.addEventListener('click', openSheet);
  /* Contents sidebar show/hide arrow tab (desktop) */
  var tocSideTab = document.getElementById('tocSideTab');
  if (tocSideTab) {
    try { if (localStorage.getItem('fs-legal-toc') === 'off') document.documentElement.classList.add('toc-side-off'); } catch (e) {}
    tocSideTab.addEventListener('click', function () {
      var off = document.documentElement.classList.toggle('toc-side-off');
      tocSideTab.setAttribute('aria-label', off ? 'Show contents' : 'Hide contents');
      tocSideTab.title = off ? 'Show contents (C)' : 'Hide contents (C)';
      try { localStorage.setItem('fs-legal-toc', off ? 'off' : 'on'); } catch (e) {}
    });
  }
  if (closeBtn) closeBtn.addEventListener('click', closeSheet);
  overlay.addEventListener('click', closeSheet);
  sheet.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', closeSheet); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeSheet(); });
  var dragY = null, dragDy = 0;
  sheet.addEventListener('touchstart', function (e) {
    var listBox = sheet.querySelector('#tocLists');
    var scrolled = listBox ? listBox.scrollTop : sheet.scrollTop;
    if (scrolled <= 0 && e.touches.length === 1) dragY = e.touches[0].clientY;
  }, { passive: true });
  sheet.addEventListener('touchmove', function (e) {
    if (dragY === null) return;
    dragDy = e.touches[0].clientY - dragY;
    if (dragDy > 0) {
      sheet.style.transition = 'none';
      sheet.style.transform = 'translateY(' + dragDy + 'px)';
    }
  }, { passive: true });
  sheet.addEventListener('touchend', function () {
    sheet.style.transition = '';
    sheet.style.transform = '';
    if (dragDy > 110) closeSheet();
    dragY = null;
    dragDy = 0;
  });
  var spyLinks = Array.prototype.slice.call(document.querySelectorAll('.toc-side a[href^="#"], .toc-sheet a[href^="#"]'));
  var spyById = {};
  spyLinks.forEach(function (a) {
    var id = a.getAttribute('href').slice(1);
    (spyById[id] = spyById[id] || []).push(a);
  });
  function keepVisible(box, el) {
    try {
      var b = box.getBoundingClientRect(), r = el.getBoundingClientRect();
      if (r.top < b.top + 8) box.scrollTop -= (b.top + 8 - r.top);
      else if (r.bottom > b.bottom - 8) box.scrollTop += (r.bottom - (b.bottom - 8));
    } catch (e) {}
  }
  /* Pill + mood state lives OUTSIDE setActive: it used to be declared inside
     setActive, which runs on every scroll tick — that re-registered a fresh
     scroll listener each tick (listener pile-up => pill lag/jitter). */
  var sideNav = document.querySelector('.toc-side nav');
  var tocPill = document.getElementById('tocPill');
  function placePill() {
    if (!sideNav || !tocPill) return;
    var link = sideNav.querySelector('li a.active');
    if (!link) { tocPill.classList.remove('on'); return; }
    var base = tocPill.offsetParent;
    if (!base) { tocPill.classList.remove('on'); return; }
    var top = 0, left = 0, el = link;
    while (el && el !== base) { top += el.offsetTop || 0; left += el.offsetLeft || 0; el = el.offsetParent; }
    var w = link.offsetWidth, tx = 0;
    try {
      var lr = link.getBoundingClientRect();
      var r = document.createRange();
      r.selectNodeContents(link);
      var rects = r.getClientRects();
      var minL = Infinity, maxR = -Infinity;
      for (var i = 0; i < rects.length; i++) {
        var q = rects[i];
        if (q.width < 1) continue;
        if (q.left < minL) minL = q.left;
        if (q.right > maxR) maxR = q.right;
      }
      if (maxR > minL) { tx = minL - lr.left; w = maxR - minL; }
    } catch (e) {}
    tocPill.classList.add('on');
    tocPill.style.height = (link.offsetHeight + 8) + 'px';
    tocPill.style.width = (w + 20) + 'px';
    tocPill.style.transform = 'translate(' + (left + tx - 10) + 'px,' + (top - 4) + 'px)';
  }
  function pillMood(mood) {
    if (!sideNav) return;
    if (sideNav.getAttribute('data-mood') !== mood) sideNav.setAttribute('data-mood', mood);
  }
  var lastSY = 0, lastST = 0, sVel = 0, calmT = null;
  if (typeof window !== 'undefined' && window.addEventListener) {
    lastSY = window.scrollY || 0;
    window.addEventListener('scroll', function () {
      var now = (window.performance && performance.now()) ? performance.now() : Date.now();
      var y = window.scrollY || 0;
      var v = Math.abs(y - lastSY) / Math.max(1, now - lastST);
      lastSY = y;
      lastST = now;
      sVel = sVel * 0.65 + v * 0.35;
      pillMood(sVel > 1.1 ? 'fast' : 'calm');
      if (calmT) clearTimeout(calmT);
      calmT = setTimeout(function () { pillMood('calm'); }, 280);
    }, { passive: true });
    window.addEventListener('resize', function () { placePill(); });
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () { placePill(); });
    }
  }
  function setActive(id) {
    spyLinks.forEach(function (a) { a.classList.toggle('active', a.getAttribute('href') === '#' + id); });
    document.querySelectorAll('.toc-sheet li.active, .toc-side li.active').forEach(function (el) { el.classList.remove('active'); });
    (spyById[id] || []).forEach(function (a) {
      if (a.parentElement && a.parentElement.tagName === 'LI') a.parentElement.classList.add('active');
    });
    var sideLink = sideNav ? sideNav.querySelector('a[href="#' + id + '"]') : null;
    if (sideLink) keepVisible(sideNav, sideLink);
    var sheet = document.getElementById('tocSheet');
    var listsBox = sheet ? sheet.querySelector('#tocLists') : null;
    var sheetLink = listsBox ? listsBox.querySelector('a[href="#' + id + '"]') : null;
    if (sheetLink && listsBox) keepVisible(listsBox, sheetLink);
    placePill();
  }
  var spyHeads = Array.prototype.slice.call(document.querySelectorAll('.legal .doc h2[id]'));
  var spyLastRun = 0;
  function spyOnScroll() {
    var cur = null;
    for (var i = 0; i < spyHeads.length; i++) {
      if (spyHeads[i].getBoundingClientRect().top <= 90) cur = spyHeads[i].id;
      else break;
    }
    if (!cur && (window.scrollY || 0) < 400 && spyHeads.length) cur = spyHeads[0].id;
    if (cur) setActive(cur);
  }
  function onScrollTick() {
    var now = Date.now();
    if (now - spyLastRun < 120) return;
    spyLastRun = now;
    spyOnScroll();
  }
  window.addEventListener('scroll', onScrollTick, { passive: true });
  var scroller = document.querySelector('main.legal');
  if (scroller) scroller.addEventListener('scroll', onScrollTick, { passive: true });
  window.addEventListener('resize', function () { spyOnScroll(); });
  spyOnScroll();
  var seg = document.querySelector('.seg');
  var listsWrap = document.getElementById('tocLists');
  if (seg && listsWrap) {
    var segLists = Array.prototype.slice.call(listsWrap.querySelectorAll('[data-toc]'));
    var segCur = parseInt(seg.getAttribute('data-active') || '0', 10);
    seg.querySelectorAll('.seg-opt').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var next = parseInt(btn.getAttribute('data-idx') || '0', 10);
        if (next === segCur) return;
        if (listsWrap.classList.contains('swap-l') || listsWrap.classList.contains('swap-r')) return;
        var dir = next > segCur ? 1 : -1;
        seg.setAttribute('data-active', String(next));
        seg.querySelectorAll('.seg-opt').forEach(function (b) {
          b.classList.toggle('active', b === btn);
        });
        listsWrap.classList.add(dir > 0 ? 'swap-l' : 'swap-r');
        setTimeout(function () {
          segLists.forEach(function (ol) {
            if (ol.getAttribute('data-toc-idx') === String(next)) ol.removeAttribute('hidden');
            else ol.setAttribute('hidden', '');
          });
          listsWrap.classList.remove('swap-l', 'swap-r');
          void listsWrap.offsetWidth;
          listsWrap.classList.add('swap-in');
          setTimeout(function () { listsWrap.classList.remove('swap-in'); }, 280);
        }, 170);
        segCur = next;
      });
    });
  }
})();'''


def legal_page(title, body_html, updated, cta_url, toc_box, toc_side, sheet_html,
               card_a, card_b, see_also, doc='', modified='', lang='en'):
    """The one legal-document template. ``lang`` only swaps strings and paths."""
    slug = doc.replace('.md', '.html') if doc else ''
    t = lambda k, **f: _ui(lang, k, **f)              # noqa: E731
    pre = '..' if lang == 'en' else '../..'
    root = 'https://fastscheduler.github.io'
    canon = f'{root}/legal/{slug}' if lang == 'en' else f'{root}/ru/legal/{slug}'
    ldesc = _i18n.doc(lang, slug.replace('.html', '')).get('meta') or title
    ldesc = _fit(ldesc)
    _page = {
        '@type': 'WebPage', '@id': canon, 'url': canon,
        'name': f'{title} — Fast Scheduler', 'description': ldesc,
        'inLanguage': lang,
        'isPartOf': {'@id': _bh.WEBSITE_ID},
        'about': {'@type': 'SoftwareApplication', 'name': 'Fast Scheduler',
                  'applicationCategory': 'BusinessApplication',
                  'operatingSystem': 'Telegram',
                  'url': 'https://fastscheduler.github.io/'},
    }
    if modified:
        _page['dateModified'] = modified
    _graph = [
        _page,
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Fast Scheduler',
             'item': 'https://fastscheduler.github.io/'},
            {'@type': 'ListItem', 'position': 2, 'name': t('docs_aria'),
             'item': f'{root}/legal/privacy.html'},
            {'@type': 'ListItem', 'position': 3, 'name': title, 'item': canon}]},
    ]
    if doc == 'refundpolicy.html' and lang == 'en':
        _graph.append({
            '@type': 'FAQPage',
            'mainEntity': [
                {'@type': 'Question',
                 'name': 'Can I get a refund for Fast Scheduler Premium?',
                 'acceptedAnswer': {'@type': 'Answer', 'text':
                     'Premium is paid with Telegram Stars. Refunds are discretionary and '
                     'limited to 7 days from that specific payment. Email '
                     'fastschedulebot@gmail.com with the transaction ID and Telegram username.'}},
                {'@type': 'Question',
                 'name': 'How long do I have to request a Fast Scheduler refund?',
                 'acceptedAnswer': {'@type': 'Answer', 'text':
                     'Each Stars payment has its own 7-day window counted from the charge date. '
                     'After 7 days that payment is not refundable, unless Fast Scheduler failed '
                     'to deliver the paid feature.'}},
                {'@type': 'Question',
                 'name': 'How do I cancel Fast Scheduler Premium?',
                 'acceptedAnswer': {'@type': 'Answer', 'text':
                     'Open /premium in @FastSchedulerBot and cancel. Cancelling stops the next '
                     'charge; the current paid period is not refunded.'}},
            ],
        })
    ldjson = json.dumps({
        '@context': 'https://schema.org', '@graph': _graph,
    }, ensure_ascii=False)
    js = (LEGAL_JS.replace('__SHOW__', t('show_contents'))
                  .replace('__HIDE__', t('hide_contents'))
                  .replace('__SHOW_KEY__', t('show_contents_key'))
                  .replace('__HIDE_KEY__', t('hide_contents_key')))
    return f'''<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, interactive-widget=resizes-content, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<title>{title} — Fast Scheduler</title>
<meta name="description" content="{ldesc}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<link rel="canonical" href="{canon}">
{_alt_links(slug.replace('.html', ''))}<meta property="og:type" content="article">
<meta property="og:site_name" content="Fast Scheduler">
<meta property="og:title" content="{title} — Fast Scheduler">
<meta property="og:description" content="{ldesc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="https://fastscheduler.github.io/og-cover-v2.png">
<meta property="og:locale" content="{"en_US" if lang == "en" else "ru_RU"}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title} — Fast Scheduler">
<meta name="twitter:description" content="{ldesc}">
<meta name="twitter:image" content="https://fastscheduler.github.io/og-cover-v2.png">
<script type="application/ld+json">{ldjson}</script>
{_bh.site_entity_ld()}
<script>
  try {{
    var t = localStorage.getItem('theme');
    if (!t && window.matchMedia) {{
      t = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }}
    if (t) document.documentElement.setAttribute('data-theme', t);
    if (localStorage.getItem('fs-motion') === 'off') document.documentElement.setAttribute('data-motion', 'off');
    if (localStorage.getItem('fs-fx') === 'off') document.documentElement.setAttribute('data-fx', 'off');
    if (localStorage.getItem('fs-hotkeys') === 'off') document.documentElement.setAttribute('data-keys', 'off');
    if (localStorage.getItem('fs-rail') === 'off') document.documentElement.classList.add('rail-off');
    var _ffs = localStorage.getItem('fs-font') || localStorage.getItem('fs-help-font') || localStorage.getItem('fs-blog-font');
    if (_ffs) {{ document.documentElement.setAttribute('data-font', _ffs); }}
  }} catch (e) {{}}
</script>
<link rel="stylesheet" href="{pre}/styles/main.css?v=20261026c4">
<link rel="stylesheet" href="{pre}/styles/liquid-nav.css?v=20261007a1">
<link rel="stylesheet" href="{pre}/styles/hotkeys-modal.css?v=20261006a1">
<link rel="stylesheet" href="{pre}/styles/mobile-fix.css?v=20261026c8">
</head>
<body class="legal">
{GLASS_DEFS}
{_legal_nav(doc, lang)}
<main class="wrap legal">
  <div class="legal-layout">
    <aside class="toc-side"><nav aria-label="{t('contents')}" id="tocSideNav" data-mood="calm"><p class="toc-title">{t('contents')}</p><span class="toc-pill" id="tocPill" aria-hidden="true"></span>{toc_side}</nav></aside>
    <button type="button" class="toc-side-tab" id="tocSideTab" aria-label="{t('hide_contents')}" aria-keyshortcuts="c" title="{t('hide_contents_key')}">{svg('chev')}<kbd class="tab-kbd" aria-hidden="true">C</kbd></button>
    <div class="legal-main">
  <article class="doc">
    <h1>{title}</h1>
    <p class="updated">{t('last_updated', date=updated)}</p>
    {see_also}
    {toc_box}
    {body_html}
  </article>
  <div class="page-nav">
    {card_a}
    {card_b}
  </div>
    </div>
  </div>
</main>
{sheet_html}
{_legal_footer(lang)}
<script src="{pre}/scripts/settings.js?v=20261005d1"></script>
  <script src="{pre}/scripts/lang.js?v=20261007a1"></script>
<script src="{pre}/scripts/hotkeys-modal.js?v=20261006a1"></script>
<script src="{pre}/scripts/hotkeys.js?v=20261005d1"></script>
<script src="{pre}/scripts/scroll-jump.js?v=20260930a1"></script>
<script src="{pre}/scripts/help-search.js?v=20261022a3"></script>
<script src="{pre}/scripts/main.js?v=20260930a1"></script>
<script src="{pre}/scripts/liquid-nav.js?v=20261005d1"></script>
<script>
{js}
</script>
<script src="{pre}/scripts/site-footer.js?v=20261018g2"></script>
</body>
</html>'''


def _fit(s, limit=155):
    """Word-boundary trim for legal meta descriptions."""
    s = re.sub(r'\s+', ' ', s or '').strip()
    if len(s) <= limit:
        return s
    cut = s[:limit]
    sp = cut.rfind(' ')
    if sp >= limit * 0.55:
        cut = cut[:sp]
    return cut.rstrip(' ,;:-')


def _source_mtime(path):
    """ISO date of the last commit that touched a legal source doc.

    write_legal() used datetime.date.today(), so every rebuild claimed the
    policies were revised that day. Google reads dateModified as a freshness
    claim; it should reflect the text, not the build.
    """
    try:
        out = subprocess.run(
            ['git', 'log', '-1', '--format=%cs', '--', path],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=20).stdout.strip()
        if re.match(r'^\d{4}-\d{2}-\d{2}$', out):
            return out
    except Exception:
        pass
    return datetime.date.today().isoformat()


LEGAL_PAGES = {
    'privacy': ('privacy.md', 'privacy.html', 'legal_privacy'),
    'terms': ('terms.md', 'terms.html', 'legal_terms'),
    'refundpolicy': ('refundpolicy.md', 'refundpolicy.html', 'legal_refund'),
}

# Fixed order for the mobile page switcher: Privacy | Refunds | Terms.
SWITCHER_ORDER = ['privacy', 'refundpolicy', 'terms']

# Liquid-glass displacement map (progressive enhancement): Chromium applies the
# SVG-filter refraction on top of the plain blur fallback, which older browsers
# keep. feTurbulence keeps this dependency-free (no binary blobs in the repo).
GLASS_DEFS = ''


def _switcher_html(current_doc, lang='en'):
    opts = []
    for i, d in enumerate(SWITCHER_ORDER):
        cls = 'seg-opt active' if d == current_doc else 'seg-opt'
        opts.append(f'<button type="button" class="{cls}" data-idx="{i}">{_ui(lang, "tab_" + d)}</button>')
    active = SWITCHER_ORDER.index(current_doc) if current_doc in SWITCHER_ORDER else 0
    return f'<div class="seg" data-active="{active}"><span class="seg-pill" aria-hidden="true"></span>{"".join(opts)}</div>'


def _sheet_lists_html(current_doc, all_tocs):
    parts = []
    for d in SWITCHER_ORDER:
        items = all_tocs.get(d, [])
        lis = []
        for hid, label in items:
            href = f'#{hid}' if d == current_doc else f"{LEGAL_PAGES[d][1]}#{hid}"
            tip = label.replace('"', '&quot;')
            lis.append(f'<li><a href="{href}" title="{tip}">{label}</a></li>')
        hidden = '' if d == current_doc else ' hidden'
        parts.append(f'<ol data-toc data-toc-idx="{SWITCHER_ORDER.index(d)}"{hidden}>' + ''.join(lis) + '</ol>')
    return f'<div class="toc-lists" id="tocLists">{"".join(parts)}</div>'


def _toc_items(body_html):
    """Extract (id, label) for every h2 (ids come from the markdown toc ext)."""
    items = []
    for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', body_html, re.S):
        label = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if label:
            items.append((m.group(1), label))
    return items


def _toc_list(items):
    out = []
    for hid, label in items:
        tip = label.replace('"', '&quot;')
        out.append(f'<li><a href="#{hid}" title="{tip}">{label}</a></li>')
    return '<ol>' + ''.join(out) + '</ol>'


def _page_card(out, title, desc, lang='en'):
    return (
        f'<a class="page-card" href="{out}">'
        f'<span class="page-kicker">{_ui(lang, "continue_reading")}</span>'
        f'<span class="page-title">{title}</span>'
        f'<span class="page-desc">{desc}</span>'
        f'<span class="page-go">{_ui(lang, "read")} {svg("arrow")}</span></a>'
    )


def write_legal():
    """Render the legal documents for every locale from the same template.

    Before this, /ru/legal/*.html came from a separate hand-written builder:
    it kept its own date, its own (older) version switcher without the check
    icon, and none of the later features ever reached it. Both trees are now one
    function call apart, and the only differences left are translated strings
    (translations/website/*.json) and the document text (docs/ vs docs/ru/).
    """
    sources = {}
    for lang in ('en', 'ru'):
        if lang == 'en':
            out_dir, docs_dir = LEGAL_DIR, DOCS_DIR
        else:
            out_dir = os.path.join(WEBSITE_DIR, 'ru', 'legal')
            docs_dir = os.path.join(REPO_ROOT, 'docs', 'ru')
        os.makedirs(out_dir, exist_ok=True)

        rendered = {}
        for name, (src_md, _out, _src) in LEGAL_PAGES.items():
            src = os.path.join(docs_dir, src_md)
            if not os.path.exists(src):
                print(f"[skip] missing {src}")
                continue
            with open(src, 'r', encoding='utf-8-sig') as f:
                text = f.read()
            text = re.sub(r'\[\[([^\]]+)\]\]', r'<span data-ph="\1">[[\1]]</span>', text)
            html = markdown.markdown(text, extensions=['tables', 'fenced_code', 'nl2br', 'toc'])
            html = html.replace('<ul>', '<ol>').replace('</ul>', '</ol>')
            html = html.replace('<table>', '<div class="table-scroll"><table>')
            html = html.replace('</table>', '</table></div>')
            rendered[name] = html
            sources[name] = src
        all_tocs = {d: _toc_items(h) for d, h in rendered.items()}

        for name, (_src_md, out, cta_source) in LEGAL_PAGES.items():
            if name not in rendered:
                continue
            html = rendered[name]
            src_date = _source_mtime(sources[name])
            meta = _i18n.doc(lang, name)
            title = meta.get('title') or name
            updated = fmt_date(src_date, lang)
            items = _toc_items(html)
            toc_list = _toc_list(items)
            toc_box = (f'<nav class="toc-box" aria-label="{_ui(lang, "contents")}">'
                       f'<p class="toc-title">{_ui(lang, "contents")}</p>{toc_list}</nav>' if items else '')
            toc_side = toc_list
            cta_url = f'{BOT_DEEP_LINK}?start=start__{cta_source}'
            others = [(LEGAL_PAGES[d][1], _i18n.doc(lang, d).get('title') or d,
                       _i18n.doc(lang, d).get('description') or '')
                      for d in LEGAL_PAGES if d != name]
            sheet_html = ''
            if items:
                sheet_html = (
                    f'<div class="toc-overlay" id="tocOverlay"></div>'
                    f'<aside class="toc-sheet" id="tocSheet" role="dialog" aria-modal="true" aria-label="{_ui(lang, "contents")}">'
                    f'<div class="sheet-grab" aria-hidden="true"></div>'
                    f'<div class="toc-sheet-head"><span>{_ui(lang, "contents")}</span>'
                    f'<button class="icon-btn" id="tocClose" aria-label="{_ui(lang, "close_contents")}">{svg("x")}</button></div>'
                    f'{_switcher_html(name, lang)}'
                    f'{_sheet_lists_html(name, all_tocs)}'
                    f'</aside>'
                    f'<div class="toc-bar"><a class="toc-bar-cta" href="{cta_url}" target="_blank" rel="noopener noreferrer">{svg("send")}<span>{_ui(lang, "open_bot")}</span></a>'
                    f'<button class="toc-burger" id="tocBurger" aria-label="{_ui(lang, "open_contents")}">'
                    f'{svg("menu")}<span>{_ui(lang, "contents")}</span></button></div>'
                )
            (o1, t1, d1), (o2, t2, d2) = others[0], others[1]
            card_a, card_b = _page_card(o1, t1, d1, lang), _page_card(o2, t2, d2, lang)
            see_also = (f'<p class="see-also">{_ui(lang, "see_also")} <a href="{o1}">{t1}</a> · '
                        f'<a href="{o2}">{t2}</a></p>')
            page = legal_page(title, html, updated, cta_url, toc_box, toc_side, sheet_html,
                              card_a, card_b, see_also, doc=out, modified=src_date, lang=lang)
            page = _lv.stamp_html(page, name, lang)
            with open(os.path.join(out_dir, out), 'w', encoding='utf-8') as f:
                f.write(page)
            print(f"[ok] wrote {os.path.join(out_dir, out)}")


if __name__ == '__main__':
    write_site_config()
    write_legal()
    print("Done.")
