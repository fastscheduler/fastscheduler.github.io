# Generates the Blog section for the Fast Scheduler site:
#   blog/index.html      - hub page listing every article, grouped by topic
#   blog/a/<id>.html     - one static page per article (unique title, description,
#                          canonical, OG/Twitter, BlogPosting + BreadcrumbList +
#                          FAQPage JSON-LD; sitemap handled by build_static.py)
# Sources: website/_build/blog_articles.py + blog_articles_b.py
# Pages use the SAME site chrome as the help center / legal pages:
# header with nav links + Help quick-search popover + settings menu,
# settings-driven theme, jump-to-top button, hotkeys, and a full footer.
# Safe to re-run (idempotent; prunes pages of removed articles).
import io
import json
import os
import re
import sys
import datetime as _dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build_help as bh                      # noqa: E402
from blog_articles import BLOG_ARTICLES      # noqa: E402
from blog_articles_b import BLOG_ARTICLES_B  # noqa: E402
from blog_articles_c import BLOG_ARTICLES_C  # noqa: E402
from blog_articles_d import BLOG_ARTICLES_D  # noqa: E402
from blog_articles_e import BLOG_ARTICLES_E  # noqa: E402
from blog_articles_f import BLOG_ARTICLES_F  # noqa: E402
from blog_articles_g import BLOG_ARTICLES_G  # noqa: E402
from blog_articles_h import BLOG_ARTICLES_H  # noqa: E402
from blog_articles_i import BLOG_ARTICLES_I  # noqa: E402
from blog_articles_j import BLOG_ARTICLES_J  # noqa: E402
from blog_articles_m import BLOG_ARTICLES_M  # noqa: E402

# Combined article list (source order = display order on the hub).
ARTICLES = (BLOG_ARTICLES + BLOG_ARTICLES_B + BLOG_ARTICLES_C +
            BLOG_ARTICLES_D + BLOG_ARTICLES_E + BLOG_ARTICLES_F +
            BLOG_ARTICLES_G + BLOG_ARTICLES_H + BLOG_ARTICLES_I +
            BLOG_ARTICLES_J +
            BLOG_ARTICLES_M)

# Optional per-article deep-dive sections (blog_extras.py). Merging happens
# HERE, at load time, so reading time, search indexing, JSON-LD articleBody,
# the TOC and the rendered page all automatically see the expanded content.
try:
    from blog_extras import EXTRA_SECTIONS, CONTENT_OVERRIDES
except ImportError:  # extras are optional
    EXTRA_SECTIONS, CONTENT_OVERRIDES = {}, {}
for _art in ARTICLES:
    if _art['id'] in CONTENT_OVERRIDES:
        _art['content'] = CONTENT_OVERRIDES[_art['id']]
    _x = EXTRA_SECTIONS.get(_art['id'])
    if _x:
        _art['content'] = _art['content'] + _x

SITE = 'https://fastscheduler.github.io'
OUT = os.path.dirname(HERE)   # .../website
BLOG_DIR = os.path.join(OUT, 'blog')
BLOG_A_DIR = os.path.join(BLOG_DIR, 'a')
BUILD_DATE = _dt.date.today().isoformat()

CATEGORIES = {
    'growth':   {'title': 'Growth',       'desc': 'Subscribers, swaps, discoverability and retention — the playbooks that compound.'},
    'content':  {'title': 'Content',      'desc': 'Formatting, calendars and content systems that keep a channel alive.'},
    'tools':    {'title': 'Bots & Tools', 'desc': 'The bot stack behind successful channels — scheduling, analytics, moderation.'},
    'platform': {'title': 'Platform',     'desc': 'How Telegram itself works: channels vs groups, bot safety, algorithms.'},
    'premium':  {'title': 'Premium & Safety', 'desc': 'Verification, Premium perks, Mini Apps — the platform layer behind channels.'},
    'money':    {'title': 'Monetization', 'desc': 'Ads, Stars, subscriptions and products — what pays, and when.'},
}

BOT_URL = 'https://t.me/FastSchedulerBot?start=start__blog'
BOT_URL_POST = 'https://t.me/FastSchedulerBot?start=start__blog_post'
SUPPORT_URL = bh.SUPPORT_URL
FAVICON = bh.FAVICON

# Same security headers as the help center's static pages (kept local so this
# builder never depends on build_static.py internals).
SECURITY_METAS = (
    '<meta name="referrer" content="strict-origin-when-cross-origin">\n'
    '<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; '
    'script-src \'self\' \'unsafe-inline\' https://www.googletagmanager.com; style-src \'self\' \'unsafe-inline\'; '
    'img-src \'self\' data: https://www.googletagmanager.com https://*.google-analytics.com https://*.analytics.google.com https://www.google.com; font-src \'self\'; connect-src \'self\' https://www.googletagmanager.com https://*.google-analytics.com https://*.analytics.google.com https://region1.google-analytics.com https://www.google.com; frame-src https://www.googletagmanager.com; '
    'object-src \'none\'; form-action \'self\'; base-uri \'self\'; upgrade-insecure-requests">'
)

NOFLASH = '''<script>
  try {
    var t = localStorage.getItem('theme');
    if (!t && window.matchMedia) t = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    if (t) document.documentElement.setAttribute('data-theme', t);
    if (localStorage.getItem('fs-motion') === 'off') document.documentElement.setAttribute('data-motion', 'off');
    if (localStorage.getItem('fs-fx') === 'off') document.documentElement.setAttribute('data-fx', 'off');
    if (localStorage.getItem('fs-hotkeys') === 'off') document.documentElement.setAttribute('data-keys', 'off');
    if (localStorage.getItem('fs-rail') === 'off') document.documentElement.classList.add('rail-off');
  } catch (e) {}
</script>'''


# ================================================================== CSS =====
BLOG_CSS = '''
    /* ===== Blog layout (uses main.css tokens + header/footer as-is) ===== */
    body.blog { --maxw: 1280px; }
    /* The mobile app-shell (fixed viewport, inner scroll) is a LEGAL-PAGES
       layout only. Blog pages must scroll the document normally on phones. */
    @media (max-width: 760px) {
      body.blog { display: block; height: auto; min-height: 100vh; overflow: visible; padding: 0; }
      body.blog main.legal { overflow: visible; padding: 0 0 30px; }
      body.blog footer.site { display: block; }
      html:has(body.blog) { height: auto; }
    }
    .blog-wrap { max-width: 1240px; margin: 0 auto; padding: 26px 28px 40px; }

    /* Breadcrumb sizing: help.html carries its own inline CSS for .hc-crumbs;
       blog pages only load main.css, so size the chevron icons here. */
    .hc-crumbs { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin: 0 0 18px; font-size: .88rem; }
    .hc-crumbs a { color: var(--text-dim); }
    .hc-crumbs a:hover { color: var(--green-strong); }
    .hc-crumbs svg { width: 14px; height: 14px; flex: none; color: var(--text-dim); }
    .hc-crumbs [aria-current="page"] { color: var(--text); font-weight: 650; }

    /* article body card, same material as .legal .doc */
    .blog-doc { background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--radius); box-shadow: var(--shadow-sm);
      padding: 36px 40px; }
    .blog-doc h1 { font-size: 2.05rem; margin: 0; letter-spacing: -.02em; line-height: 1.2; }
    .blog-moreq { margin: 20px 0 0; }
    .blog-moreq a { display: inline-flex; align-items: center; gap: 7px; font-size: .9rem;
      font-weight: 650; color: var(--green-strong); text-decoration: none;
      padding: 9px 15px; border: 1px solid color-mix(in srgb, var(--green) 35%, var(--border));
      border-radius: 999px; transition: border-color .18s, background .18s; }
    .blog-moreq a:hover { border-color: var(--green);
      background: color-mix(in srgb, var(--green) 7%, transparent); text-decoration: none; }
    .blog-moreq svg { width: 15px; height: 15px; }
    .blog-byline { color: var(--text-dim); font-size: .85rem; margin: 10px 0 0; }
    .blog-doc-cover { margin: 16px 0 4px; border-radius: 14px; overflow: hidden;
      border: 1px solid var(--border); }
    .blog-doc-cover img { display: block; width: 100%; height: auto; }
    .blog-doc .hc-body { margin-top: 16px; }
    .blog-doc .hc-body h3 { font-size: 1.1rem; margin: 26px 0 10px; color: var(--green-strong); }
    .blog-doc .hc-body p { color: var(--text); line-height: 1.7; margin: 0 0 14px; }
    .blog-doc .hc-body ul { padding-left: 22px; margin: 0 0 14px; }
    .blog-doc .hc-body li { color: var(--text); line-height: 1.7; margin-bottom: 6px; }
    .blog-doc .hc-body a { color: var(--green-strong); }
    .blog-doc .hc-body code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: .86em; background: var(--surface-2); padding: 1px 5px; border-radius: 6px; }

    /* ----- table of contents (desktop: side rail, mobile: collapsible) ----- */
    .blog-cols { display: grid; grid-template-columns: minmax(0, 860px) 220px; gap: 28px;
      align-items: start; justify-content: center; }
    .blog-toc { position: sticky; top: 88px; font-size: .85rem; }
    .blog-toc-t { font-size: .72rem; font-weight: 800; letter-spacing: .06em; text-transform: uppercase;
      color: var(--text-dim); margin: 4px 0 10px; }
    .blog-toc a { display: block; padding: 5px 10px; border-radius: 8px; color: var(--text-dim);
      border-left: 2px solid var(--border); line-height: 1.35; }
    .blog-toc a:hover { color: var(--green-strong); background: color-mix(in srgb, var(--green) 7%, transparent);
      text-decoration: none; }
    .blog-toc a.on { color: var(--green-strong); border-left-color: var(--green); font-weight: 650; }
    .blog-toc-back { margin-top: 12px; padding-top: 10px; border-top: 1px dashed var(--border); }

    /* mobile TOC: a <details> above the article */
    /* mobile Contents bottom sheet (legal-pages style) */
    .blog-toc-fab { position: fixed; left: 14px; bottom: calc(14px + env(safe-area-inset-bottom)); z-index: 96;
      display: none; align-items: center; gap: 7px; padding: 11px 16px; border-radius: 999px;
      border: 1px solid var(--border); background: var(--surface); color: var(--text);
      font: inherit; font-size: .88rem; font-weight: 700; cursor: pointer;
      box-shadow: var(--shadow); }
    .blog-toc-fab svg { width: 16px; height: 16px; color: var(--green-strong); }
    .blog-toc-scrim { position: fixed; inset: 0; z-index: 100; background: rgba(0,0,0,.45); opacity: 0; pointer-events: none; transition: opacity .3s; }
    .blog-toc-scrim.open { opacity: 1; pointer-events: auto; }
    .blog-toc-sheet { position: fixed; left: 0; right: 0; bottom: 0; z-index: 101; max-height: 76dvh;
      display: flex; flex-direction: column; padding: 10px 18px calc(14px + env(safe-area-inset-bottom));
      background: var(--surface); border: 1px solid var(--border); border-bottom: 0;
      border-radius: 18px 18px 0 0; box-shadow: 0 -12px 34px rgba(0,0,0,.28);
      transform: translateY(100%); visibility: hidden; transition: transform .38s cubic-bezier(.32,.72,.35,1), visibility 0s .38s; }
    .blog-toc-sheet.open { transform: none; visibility: visible; transition: transform .38s cubic-bezier(.32,.72,.35,1); }
    .blog-toc-head { display: flex; align-items: center; justify-content: space-between; padding: 8px 0 10px; font-weight: 800; font-size: 1.05rem; flex: none; }
    .blog-toc-nav { display: grid; grid-template-columns: 1fr 1.2fr 1fr; gap: 8px; margin: 0 0 12px; flex: none; }
    .blog-toc-navc { display: block; min-width: 0; padding: 9px 11px; border: 1px solid var(--border); border-radius: 12px;
      background: color-mix(in srgb, var(--surface-2) 55%, transparent); text-decoration: none; color: var(--text); position: relative; }
    .blog-toc-navc small { display: block; font-size: .66rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--text-dim); }
    .blog-toc-navc b { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; font-size: .8rem; line-height: 1.3; margin-top: 3px; }
    .blog-toc-navc svg { position: absolute; right: 8px; top: 50%; translate: 0 -50%; width: 14px; height: 14px; color: var(--text-dim); }
    a.blog-toc-navc:hover { text-decoration: none; border-color: var(--green); }
    .blog-toc-navc.cur { background: color-mix(in srgb, var(--green) 8%, transparent); border-color: color-mix(in srgb, var(--green) 35%, var(--border)); }
    .blog-toc-navc.cur b { -webkit-line-clamp: 3; }
    .blog-toc-navc.none { border-style: dashed; opacity: .6; }
    .blog-toc-list { flex: 1 1 auto; min-height: 0; overflow-y: auto; border-left: 2px dotted var(--border); margin: 4px 0 4px 6px; padding: 0 0 0 4px; }
    .blog-toc-list li { list-style: none; }
    .blog-toc-list a { display: block; padding: 9px 0 9px 16px; color: var(--text); font-weight: 650; font-size: .93rem; position: relative; }
    .blog-toc-list a::before { content: ''; position: absolute; left: -4px; top: 16px; width: 10px; height: 10px; border-radius: 50%; background: var(--surface); border: 2px solid var(--text-dim); box-sizing: border-box; }
    .blog-toc-list a:hover { color: var(--green-strong); text-decoration: none; }
    .blog-toc-empty { color: var(--text-dim); font-size: .9rem; padding: 6px 2px 10px; }
    @media (max-width: 640px) { .blog-toc-fab { display: inline-flex; } .blog-toc-fab[hidden] { display: none; } }
    @media (min-width: 641px) { .blog-toc-sheet, .blog-toc-scrim { display: none !important; } }
    .blog-toc-m { display: none; margin: 0 0 18px; background: var(--surface);
      border: 1px solid var(--border); border-radius: 14px; padding: 2px 16px; }
    .blog-toc-m summary { cursor: pointer; list-style: none; padding: 12px 0; font-weight: 750;
      font-size: .92rem; display: flex; justify-content: space-between; align-items: center; }
    .blog-toc-m summary::-webkit-details-marker { display: none; }
    .blog-toc-m summary::after { content: "+"; font-size: 1.2rem; color: var(--green-strong); }
    .blog-toc-m details[open] summary::after, .blog-toc-m[open] summary::after { transform: rotate(45deg); }
    .blog-toc-m summary svg { display: none; }
    .blog-toc-m nav { padding: 2px 0 12px; }
    .blog-toc-m a { display: block; padding: 7px 2px; color: var(--text-dim); font-size: .9rem; }
    .blog-toc-m a:hover { color: var(--green-strong); text-decoration: none; }

    @media (max-width: 1140px) {
      .blog-cols { grid-template-columns: minmax(0, 1fr); }
      .blog-toc { display: none; }
      .blog-toc-m { display: block; }
    }

    /* ===== hub: topic filter chips ===== */
    .blog-chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0 6px; }
    .blog-chip { font: inherit; font-size: .86rem; font-weight: 650; color: var(--text-dim);
      background: var(--surface); border: 1px solid var(--border); border-radius: 999px;
      padding: 8px 16px; cursor: pointer; transition: color .18s, border-color .18s, background .18s; }
    .blog-chip:hover { color: var(--green-strong);
      border-color: color-mix(in srgb, var(--green) 50%, transparent); }
    .blog-chip.on { color: #fff; background: var(--green-strong); border-color: var(--green-strong); }

    /* ===== hub: bento grid of article cards ===== */
    .blog-sec { margin-top: 34px; }
    .blog-sec h2 { margin: 0 0 4px; font-size: 1.35rem; letter-spacing: -.02em; color: var(--text); }
    .blog-sec-desc { color: var(--text-dim); margin: 0 0 16px; font-size: .95rem; }
    .bento { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; grid-auto-flow: dense;
      align-items: start; }
    .bcard { display: flex; flex-direction: column; min-width: 0; overflow: hidden;
      background: var(--surface); border: 1px solid var(--border); border-radius: 16px;
      color: var(--text); text-decoration: none;
      transition: border-color .2s ease, box-shadow .2s ease, transform .2s ease; }
    .bcard:hover { border-color: var(--green); box-shadow: var(--shadow-sm);
      text-decoration: none; transform: translateY(-2px); }
    .bcard-cover { display: block; aspect-ratio: 16 / 9; overflow: hidden; background: var(--surface-2); }
    .bcard-cover img { display: block; width: 100%; height: 100%; object-fit: cover;
      transition: transform .35s ease; }
    .bcard:hover .bcard-cover img { transform: scale(1.04); }
    .bcard-body { display: flex; flex-direction: column; gap: 8px; flex: 1; padding: 16px 18px 18px; }
    .bcard-body b { font-size: 1rem; line-height: 1.35; letter-spacing: -.01em; }
    .bcard-desc { color: var(--text-dim); font-size: .88rem; line-height: 1.5; }
    .bcard-meta { margin-top: 0; padding-top: 2px; font-size: .78rem; color: var(--text-dim); }
    .bcard-desc {
      display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
    .bcard.off { display: none; }

    /* search bar — sticky above the topic chips */
    .blog-search { position: sticky; top: 8px; z-index: 40; margin: 14px 0 2px; }
    .bsearch-row { display: flex; align-items: center; gap: 10px; padding: 12px 16px;
      background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
      box-shadow: var(--shadow-sm); transition: border-color .18s, box-shadow .18s; }
    .bsearch-row:focus-within { border-color: var(--green);
      box-shadow: 0 0 0 3px color-mix(in srgb, var(--green) 18%, transparent); }
    .bsearch-row svg { width: 18px; height: 18px; flex: none; color: var(--text-dim); }
    .bsearch-row input { flex: 1; min-width: 0; border: 0; outline: 0; background: transparent;
      font: inherit; font-size: .98rem; color: var(--text); }
    .bsearch-row input::placeholder { color: var(--text-dim); }
    .blog-search-kbd { font-family: inherit; font-size: .74rem; font-weight: 700;
      color: var(--text-dim); border: 1px solid var(--border); border-radius: 6px;
      padding: 2px 7px; background: var(--surface-2); }
    @media (max-width: 700px) { .blog-search-kbd { display: none; } }

    .blog-empty { margin: 26px 0; color: var(--text-dim); font-size: .95rem; }

    /* ---------- full search results view (help-center style) ---------- */
    .blog-results[hidden] { display: none; }
    .blog-results { margin-top: 26px; }
    .blog-res-head h2 { margin: 0; font-size: 1.5rem; letter-spacing: -.02em; color: var(--text); }
    .blog-res-head p { margin: 4px 0 0; color: var(--text-dim); font-size: .92rem; }
    .blog-filters { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0 18px; }
    .blog-fchip { font: inherit; font-size: .84rem; font-weight: 650; color: var(--text-dim);
      background: var(--surface); border: 1px solid var(--border); border-radius: 999px;
      padding: 7px 14px; cursor: pointer; transition: color .18s, border-color .18s, background .18s; }
    .blog-fchip:hover { color: var(--green-strong); border-color: color-mix(in srgb, var(--green) 50%, transparent); }
    .blog-fchip.on { color: #fff; background: var(--green-strong); border-color: var(--green-strong); }
    .blog-fchip .blog-fcount { font-size: .78em; font-weight: 650; opacity: .62; margin-left: 2px; }
    .blog-fchip.zero { opacity: .55; }
    /* result cards reuse .bcard sizing but without images */
    #blog-res-grid { grid-template-columns: repeat(3, 1fr); }
    .bcard-text .bcard-cover { display: none; }
    .bcard-text .bcard-body { padding: 18px 20px; }
    .bcard-text .bcard-desc { display: -webkit-box; -webkit-line-clamp: 4;
      -webkit-box-orient: vertical; overflow: hidden; }
    .bcard-text mark, .blog-results mark { background: color-mix(in srgb, #ffd84d 45%, transparent);
      color: inherit; border-radius: 3px; padding: 0 1px; }
    .blog-nores { padding: 40px 0; text-align: center; color: var(--text-dim); }
    @media (max-width: 1100px) { #blog-res-grid { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 700px) { #blog-res-grid { grid-template-columns: 1fr; } }

    @media (max-width: 1100px) { .bento { grid-template-columns: repeat(3, 1fr); } }
    @media (max-width: 940px) { .bento { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 700px) {
      .bento { grid-template-columns: 1fr; gap: 12px; }
      .s-lg, .s-md, .bsearch { grid-column: auto; }
      .bcard-desc { display: none !important; }
    }
    @media (max-width: 400px) {
      .bento { gap: 10px; }
      .bcard-body { padding: 14px 15px 16px; }
    }
    @media (hover: none) { .bcard:hover { transform: none; } }
    @media (prefers-reduced-motion: reduce) {
      .bcard, .bcard:hover { transition: none; transform: none; }
    }

    /* ===== components mirrored from help.html (blog pages don't load its
       inline CSS) ===== */
    .hc-chip {
      display: inline-flex; align-items: center; gap: 8px; font-size: .88rem; font-weight: 650;
      color: var(--text); background: var(--surface); border: 1px solid var(--border);
      padding: 9px 16px; border-radius: 999px; line-height: 1.3; max-width: 300px;
      transition: border-color .18s, color .18s; }
    .hc-chip svg { width: 15px; height: 15px; flex: none; color: var(--green-strong); }
    .hc-chip:hover { border-color: color-mix(in srgb, var(--green) 50%, transparent);
      color: var(--green-strong); text-decoration: none; }
    .hc-chips { display: flex; flex-wrap: wrap; gap: 8px; }
    .hc-related { margin-top: 26px; }
    .hc-related h2 { font-size: .9rem; font-weight: 650; color: var(--text-dim); margin: 14px 0 10px; }
    .hc-pager { max-width: 860px; margin: 16px auto 0; display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .hc-pager a { display: flex; align-items: center; gap: 12px; padding: 14px 17px; color: var(--text);
      background: var(--surface); border: 1px solid var(--border); border-radius: 16px;
      box-shadow: var(--shadow-sm); transition: border-color .2s; }
    .hc-pager a:hover { text-decoration: none; border-color: color-mix(in srgb, var(--green) 45%, var(--border)); }
    .hc-pager a.next { justify-content: flex-end; text-align: right; }
    .hc-pager a.next svg { order: 2; }
    .hc-pager svg { flex: none; width: 17px; height: 17px; color: var(--text-dim); }
    .hc-pager small { display: block; font-size: .78rem; font-weight: 650; color: var(--text-dim); }
    .hc-pager a span { min-width: 0; flex: 1 1 auto; }
    .hc-pager b { display: block; font-size: .9rem; margin-top: 2px; overflow: hidden;
      text-overflow: ellipsis; white-space: nowrap; max-width: 100%; }
    @media (max-width: 640px) {
      .hc-pager { gap: 9px; }
      .hc-pager a { padding: 12px 13px; gap: 9px; }
      .hc-pager b { font-size: .84rem; }
      .hc-pager svg { width: 15px; height: 15px; }
    }
    .hc-faq { margin-top: 26px; border-top: 1px solid var(--border); padding-top: 6px; }
    .hc-faq h2 { font-size: .9rem; font-weight: 650; color: var(--text-dim); margin: 14px 0 4px; }
    .hc-faq details { border-bottom: 1px dashed var(--border); }
    .hc-faq details:last-child { border-bottom: 0; }
    .hc-faq summary code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: .86em; background: var(--surface-2); padding: 1px 5px; border-radius: 6px; }
    .hc-faq summary { cursor: pointer; list-style: none; padding: 13px 0; font-weight: 650; font-size: .95rem;
      display: flex; justify-content: space-between; gap: 14px; align-items: center; }
    .hc-faq summary::-webkit-details-marker { display: none; }
    .hc-faq summary::after { content: "+"; font-size: 1.3rem; color: var(--green-strong);
      transition: transform .25s; flex: none; }
    .hc-faq details[open] summary::after { transform: rotate(45deg); }
    .hc-fa { padding: 0 0 16px; }
    .hc-fa p { margin: 0 0 8px; color: var(--text-dim); font-size: .92rem; line-height: 1.65; }
    .hc-cta {
      max-width: 860px; margin: 16px auto 20px; padding: 22px 26px; border-radius: 18px;
      display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap;
      background: var(--green-strong); color: #fff; }
    .hc-cta b { font-size: 1.02rem; }
    .hc-cta p { margin: 3px 0 0; font-size: .88rem; opacity: .92; }
    .hc-cta .btn { flex: none; background: #fff; color: var(--green-strong); border: 0; }
    .hc-cta .btn:hover { background: #f0fff7; }
    .hc-cta svg { width: 16px; height: 16px; }

    /* hub hero — explicit colors: blog pages don't get help.html's inline
       .doc heading rules, and main.css scopes some heading colors to
       .legal .doc, which the hub's plain header doesn't match. */
    .blog-hero { padding: 8px 0 6px; }
    .blog-hero h1 { font-size: clamp(1.8rem, 4.5vw, 2.6rem); margin: 0 0 10px; letter-spacing: -.03em; color: var(--text); }
    .blog-hero .lead { color: var(--text-dim); font-size: 1.02rem; line-height: 1.6; max-width: 640px; margin: 0 0 6px; }
    .blog-sec h2 { color: var(--text); }
    .blog-doc h1 { color: var(--text); }

    /* settings menu help popover reuses .help-menu rules from main.css */
'''


def strip_html(html):
    txt = re.sub(r'<[^>]+>', ' ', html or '')
    return ' '.join(txt.split())


def jsonld(obj):
    return ('<script type="application/ld+json">'
            + json.dumps(obj, ensure_ascii=False) + '</script>')


def breadcrumb_ld(items):
    ents = [{'@type': 'ListItem', 'position': i, 'name': n, 'item': u}
            for i, (n, u) in enumerate(items, 1)]
    return jsonld({'@context': 'https://schema.org', '@type': 'BreadcrumbList',
                   'itemListElement': ents})


def page_head(title, desc, canonical, extra_ld='', og_type='article'):
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#1faa59">
<meta name="color-scheme" content="light dark">
{SECURITY_METAS}
<title>{bh.esc(title)}</title>
<meta name="description" content="{bh.esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<link rel="canonical" href="{canonical}">
<link rel="describedby" href="https://fastscheduler.github.io/llms.txt">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Fast Scheduler">
<meta property="og:title" content="{bh.esc(title)}">
<meta property="og:description" content="{bh.esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/og-cover-v2.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{bh.esc(title)}">
<meta name="twitter:description" content="{bh.esc(desc)}">
<meta name="twitter:image" content="{SITE}/og-cover-v2.png">
{FAVICON}
{extra_ld}'''


# ------------------------------------------------------------------ chrome --
def header(rel):
    """Same structure as the legal pages' header (build_site._nav): brand,
    nav links, Help quick-search popover, settings menu, Open Bot CTA."""
    return f'''<header class="site">
  <div class="wrap nav">
    <a class="brand" href="{rel}/index.html" aria-label="Fast Scheduler — home"><span class="brand-mark">{bh.svg('calendar')}</span><span class="brand-full">Fast Scheduler</span></a>
    <a class="nav-link" href="{rel}/blog/index.html">{bh.svg('megaphone')} Blog</a>
    <a class="nav-link" href="{rel}/help.html">{bh.svg('book')} Help Center</a>
    <a class="btn btn-primary nav-cta" data-cta-short="Open" href="{BOT_URL}" target="_blank" rel="noopener noreferrer">{bh.svg('send')}<span>Open Bot</span></a>
    <span class="settings-wrap">
      <button type="button" class="icon-btn" id="settingsBtn" aria-haspopup="menu" aria-expanded="false" aria-label="Settings" data-hk="settings dark anim fx keys">{bh.svg('gear')}</button>
      <div class="glass-pop" id="settingsMenu" role="menu" aria-label="Settings">
        <div class="gp-head">Settings</div>
        <button type="button" class="gp-row" role="menuitemcheckbox" aria-checked="false" id="rowDark">{bh.svg('moon')}<span>Dark mode</span><span class="io-switch" aria-hidden="true"></span></button>
        <button type="button" class="gp-row" role="menuitemcheckbox" aria-checked="true" id="rowAnim">{bh.svg('zap')}<span>Animations</span><span class="io-switch" aria-hidden="true"></span></button>
        <button type="button" class="gp-row" role="menuitemcheckbox" aria-checked="true" id="rowFx">{bh.svg('sparkles')}<span>Effects</span><span class="io-switch" aria-hidden="true"></span></button>
        <button type="button" class="gp-row" role="menuitemcheckbox" aria-checked="true" id="rowKeys">{bh.svg('keys')}<span>Hotkeys</span><span class="io-switch" aria-hidden="true"></span></button>
        <button type="button" class="gp-row gp-row-sub" id="rowKeysHelp" role="menuitem"><svg viewBox="0 0 24 24" fill="none" stroke="none" aria-hidden="true" style="visibility:hidden;width:18px;height:18px"></svg><span class="gp-sub-label">See hotkeys</span><svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9 18 15 12 9 6"/></svg></button>
        <div class="gp-sep" role="separator"></div>
        <span class="site-menu-wrap"><a class="gp-row site-menu-row" role="menuitem" href="{rel}/help.html">{bh.svg('book')}<span>Help</span>{bh.svg('chev')}</a>
          <div class="glass-pop site-menu-pop help-menu" id="siteMenu" role="menu" aria-label="Help center quick search">
            <form class="help-search" id="helpSearchForm" role="search">
              {bh.svg('search', 'sic')}
              <input type="search" id="helpSearchInput" placeholder="Search the help center…" autocomplete="off" aria-label="Search the help center">
            </form>
            <div class="help-recent">
              <div class="help-recent-title" id="helpRecentTitle">Popular articles</div>
              <div class="help-recent-list" id="helpRecentList"></div>
            </div>
            <a class="gp-row help-menu-open" role="menuitem" href="{rel}/help.html">{bh.svg('book')}<span>Open Help Center</span>{bh.svg('chev')}</a>
          </div>
        </span>
        <a class="gp-row" role="menuitem" href="{rel}/blog/index.html">{bh.svg('megaphone')}<span>Blog</span></a>
        <a class="gp-row" role="menuitem" href="{SUPPORT_URL}" target="_blank" rel="noopener noreferrer">{bh.svg('send')}<span>Support chat</span></a>
      </div>
    </span>
  </div>
</header>'''


def footer(rel):
    return f'''<footer class="site">
  <div class="wrap foot">
    <span class="copy">© 2026 Fast Scheduler — free Telegram scheduling bot</span>
    <nav class="links" aria-label="Site">
      <a href="{rel}/index.html">Home</a>
      <a href="{rel}/blog/index.html">Blog</a>
      <a href="{rel}/help.html">Help Center</a>
      <a href="{rel}/legal/terms.html">Terms</a>
      <a href="{rel}/legal/privacy.html">Privacy</a>
      <a href="{rel}/legal/refundpolicy.html">Refunds</a>
    </nav>
  </div>
</footer>'''


def page_shell(title_html, body, rel='..', extra_js='', body_cls='blog'):
    """rel: prefix for assets from the page location (blog/ and blog/a/)."""
    return f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
{NOFLASH}
{title_html}
<link rel="preload" href="{rel}/fonts/space-grotesk-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{rel}/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{rel}/styles/main.css?v=20261013m3">
<link rel="stylesheet" href="{rel}/styles/hotkeys-modal.css?v=20261006a1">
<style>{BLOG_CSS}
  </style>
</head>
<body class="{body_cls}">
<a class="skip-link" href="#main">Skip to main content</a>
{header(rel)}
<main class="legal" id="main">
{body}
</main>
{footer(rel)}
<script src="{rel}/scripts/theme.js?v=20260930a1"></script>
<script src="{rel}/scripts/settings.js"></script>
  <script src="{rel}/scripts/lang.js?v=20261001a1"></script>
<script src="{rel}/scripts/help-search.js?v=20260930a1"></script>
<script src="{rel}/scripts/hotkeys-modal.js?v=20261006a1"></script>
<script src="{rel}/scripts/hotkeys.js?v=20260930a1"></script>
<script src="{rel}/scripts/scroll-jump.js?v=20260930a1"></script>
{extra_js}
</body>
</html>'''


HELP_PICKS = [
    ('tg_best_posting_times',
     'The Best Times to Post in Telegram (and How to Test Them Properly)'),
    ('tg_channels_explained',
     'Telegram Channels vs Groups vs Bots: The Difference That Actually Matters'),
]


def related_for(art):
    """Cross-links: same-category siblings (no help-center links here — the
    blog is editorial content and shouldn't route readers into support docs)."""
    rows = [(b['id'], b['title'], 'blog') for b in ARTICLES
            if b is not art and b['category'] == art['category']][:6]
    chips = ''.join(
        f'<a class="hc-chip" href="{rid + ".html"}">'
        f'<span>{bh.esc(t)}</span>{bh.svg("arrow-r")}</a>'
        for rid, t, kind in rows)
    return (f'<div class="hc-related"><h2>Keep reading</h2>'
            f'<div class="hc-chips">{chips}</div></div>')


def faq_ld(art):
    if not art.get('faq'):
        return ''
    ents = [{'@type': 'Question', 'name': ' '.join(strip_html(f['q']).split()),
             'acceptedAnswer': {'@type': 'Answer',
                                'text': ' '.join(strip_html(f['a']).split())}}
            for f in art['faq']]
    return jsonld({'@context': 'https://schema.org', '@type': 'FAQPage',
                   'mainEntity': ents})


def headings_of(content):
    """The h3s of an article, with slug ids — drives the table of contents."""
    out = []
    for m in re.finditer(r'<h3>(.*?)</h3>', content):
        txt = strip_html(m.group(1))
        slug = 's-' + re.sub(r'[^a-z0-9]+', '-', txt.lower()).strip('-')[:60]
        out.append((slug, txt))
    return out


def with_heading_ids(content, heads):
    for slug, txt in heads:
        content = content.replace(f'<h3>{txt}</h3>', f'<h3 id="{slug}">{txt}</h3>', 1)
    return content


def toc_html(heads, rel_prefix=''):
    if len(heads) < 3:
        return ''
    links = ''.join(f'<a href="#{slug}">{bh.esc(txt)}</a>' for slug, txt in heads)
    return (f'<nav class="blog-toc" aria-label="On this page">'
            f'<div class="blog-toc-t">On this page</div>{links}'
            f'<div class="blog-toc-back"><a href="{rel_prefix}../index.html">← All articles</a></div>'
            f'</nav>')


def toc_mobile(heads, art=None, prev_a=None, next_a=None):
    """Mobile Contents bottom sheet (legal-pages style): a floating pill
    opens a sheet with the section list plus prev / current / next article."""
    links = ''.join(f'<a href="#{slug}">{bh.esc(txt)}</a>' for slug, txt in heads)
    list_html = (f'<ol class="blog-toc-list">{links}</ol>' if links
                 else '<p class="blog-toc-empty">This article has no sections.</p>')

    def cell(kind, node):
        if node:
            lbl = 'Previous' if kind == 'prev' else 'Up next'
            arrow = bh.svg('arrow-l') if kind == 'prev' else bh.svg('arrow-r')
            href = node['id'] + '.html'
            return (f'<a class="blog-toc-navc {kind}" href="{href}">'
                    f'<small>{lbl}</small><b>{bh.esc(node["title"])}</b>{arrow}</a>')
        lbl = 'No previous article' if kind == 'prev' else 'No next article'
        return f'<span class="blog-toc-navc {kind} none"><small>{lbl}</small></span>'

    cur = bh.esc(art['title']) if art else ''
    return f'''<button type="button" class="blog-toc-fab" data-blog-toc-fab aria-label="Open contents" hidden>{bh.svg('book')}<span>Contents</span></button>
<div class="blog-toc-scrim" data-blog-toc-scrim hidden></div>
<div class="blog-toc-sheet" data-blog-toc-sheet role="dialog" aria-modal="true" aria-label="Contents" hidden>
  <div class="blog-toc-head"><span>Contents</span><button type="button" class="icon-btn" data-blog-toc-close aria-label="Close contents">{bh.svg('close')}</button></div>
  <div class="blog-toc-nav">
    {cell('prev', prev_a)}
    <div class="blog-toc-navc cur"><small>Now reading</small><b>{cur}</b></div>
    {cell('next', next_a)}
  </div>
  {list_html}
</div>'''


TOC_JS = '''<script>
/* Mobile Contents sheet: pill opens/closes, scrim + Esc + link tap close. */
(function () {
  'use strict';
  function parts() {
    return {
      sheet: document.querySelector('[data-blog-toc-sheet]'),
      scrim: document.querySelector('[data-blog-toc-scrim]')
    };
  }
  function open(scrim, sheet) {
    if (!sheet) return;
    sheet.hidden = false; scrim.hidden = false;
    void sheet.offsetWidth;
    sheet.classList.add('open'); scrim.classList.add('open');
  }
  function close(scrim, sheet) {
    if (!sheet || sheet.hidden) return;
    sheet.classList.remove('open'); scrim.classList.remove('open');
    setTimeout(function () { sheet.hidden = true; scrim.hidden = true; }, 400);
  }
  document.addEventListener('click', function (e) {
    var p = parts();
    if (e.target.closest && e.target.closest('[data-blog-toc-fab]')) { e.preventDefault(); open(p.scrim, p.sheet); return; }
    if (e.target.closest && e.target.closest('[data-blog-toc-close]')) { close(p.scrim, p.sheet); return; }
    if (e.target.classList && e.target.classList.contains('blog-toc-scrim')) { close(p.scrim, p.sheet); return; }
    if (p.sheet && !p.sheet.hidden && e.target.closest && e.target.closest('.blog-toc-list a')) close(p.scrim, p.sheet);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var p = parts();
    close(p.scrim, p.sheet);
  });
  /* show the pill once the reader scrolls into the article */
  var fab = document.querySelector('[data-blog-toc-fab]');
  if (fab) {
    var shown = false;
    window.addEventListener('scroll', function () {
      if (!shown && window.scrollY > 420) { shown = true; fab.hidden = false; }
    }, { passive: true });
  }
})();
/* Blog TOC: scroll-spy for the desktop rail + smooth anchor scrolling. */
(function () {
  'use strict';
  var links = Array.prototype.slice.call(document.querySelectorAll('.blog-toc a[href^="#"]'));
  if (links.length) {
    var map = {};
    links.forEach(function (a) {
      var el = document.getElementById(a.getAttribute('href').slice(1));
      if (el) map[el.id] = a;
    });
    var current = null;
    var ticking = false;
    function update() {
      ticking = false;
      var best = null;
      links.forEach(function (a) {
        var el = document.getElementById(a.getAttribute('href').slice(1));
        if (el && el.getBoundingClientRect().top <= 120) best = a;
      });
      if (best !== current) {
        if (current) current.classList.remove('on');
        current = best;
        if (current) current.classList.add('on');
      }
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    update();
  }
  /* smooth scroll respects the site's Animations switch + reduced motion */
  document.querySelectorAll('.blog-toc a[href^="#"], .blog-toc-m a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var el = document.getElementById(a.getAttribute('href').slice(1));
      if (!el) return;
      e.preventDefault();
      var off = el.getBoundingClientRect().top + window.pageYOffset - 76;
      var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches ||
                   document.documentElement.getAttribute('data-motion') === 'off';
      window.scrollTo({ top: off, behavior: reduce ? 'auto' : 'smooth' });
      try { history.replaceState(null, '', a.getAttribute('href')); } catch (err) {}
      var m = document.querySelector('.blog-toc-m');
      if (m && m.open) m.open = false;
    });
  });
})();
</script>'''


def fmt_date(d):
    try:
        dt = _dt.date.fromisoformat(d)
        return '%s %d, %d' % (dt.strftime('%B'), dt.day, dt.year)
    except Exception:
        return d


# ------------------------------------------------------------------ hub ----
CAT_ICON = {'growth': 'gauge', 'content': 'book', 'tools': 'bot',
            'platform': 'globe', 'money': 'crown'}
COVER_COLORS = {
    'growth':   ('#3e9d76', '#1d5c44'),
    'content':  ('#6d7ff3', '#3d3f86'),
    'tools':    ('#4f8cc9', '#2b4a72'),
    'premium':  ('#9b6ef3', '#5a3b96'),
    'platform': ('#4aa9c9', '#275a6e'),
    'money':    ('#d9a441', '#8a6420'),
}


def _hash(s):
    h = 0
    for ch in s:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return h


def reading_minutes(art):
    """Honest reading time: average adult reads ~200 wpm of mixed prose.
    Counts the body text (headings included — readers skim them too) and
    FAQ answers, which live in art['faq']. Minimum 1 minute."""
    words = len(strip_html(art['content']).split())
    for f in art.get('faq') or []:
        words += len(strip_html(f['q'] + ' ' + f['a']).split())
    return max(1, round(words / 200))


def size_for(art, i):
    # Uniform grid: every card the same size -> no half-empty rows anywhere.
    return 'sm'


# Real photo covers, downloaded from Unsplash (royalty-free) into blog/img/
# at build time. Fallback: the generated SVG gradient, so builds never break
# when a photo is missing.

def _search_docs():
    """Full-text search index for the blog (used by the hub's results view
    and exported for the help center's unified search)."""
    docs = []
    for a in ARTICLES:
        body = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', a['content'])).strip()
        faq = ' '.join((re.sub(r'<[^>]+>', ' ', f['q']) + ' ' + re.sub(r'<[^>]+>', ' ', f['a']))
                       for f in a.get('faq') or []).strip()
        docs.append({'id': a['id'], 'c': a['category'], 't': a['title'],
                     'd': a['description'], 'b': body, 'f': faq})
    return json.dumps(docs, ensure_ascii=False)


def cover_url(a):
    """<id>.jpg when the photo exists in blog/img, else the generated SVG."""
    p = os.path.join(BLOG_DIR, 'img', a['id'] + '.jpg')
    return ('img/%s.jpg' % a['id']) if os.path.isfile(p) \
        else ('img/%s.svg' % a['id'])


def cover_svg(art):
    c1, c2 = COVER_COLORS.get(art['category'], ('#4bb98b', '#256d4f'))
    h = _hash(art['id'])
    icon = bh.ICONS[CAT_ICON.get(art['category'], 'book')]
    x1, y1 = 90 + h % 200, 70 + (h >> 3) % 110
    r1 = 80 + (h >> 5) % 70
    x2, y2 = 640 - (h >> 7) % 180, 330 + (h >> 9) % 70
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450">'
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/>'
        '</linearGradient></defs>'
        '<rect width="800" height="450" fill="url(#g)"/>'
        '<g fill="none" stroke="rgba(255,255,255,.16)" stroke-width="1.5">'
        f'<circle cx="{x1}" cy="{y1}" r="{r1}"/>'
        f'<circle cx="{x2}" cy="{y2}" r="{r1 + 45}"/>'
        f'<circle cx="{x2}" cy="{y1 + 30}" r="{r1 // 2}" fill="rgba(255,255,255,.07)" stroke="none"/>'
        '</g>'
        '<g transform="translate(340,165) scale(5)" stroke="rgba(255,255,255,.92)" fill="none" '
        f'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">{icon}</g>'
        '</svg>')


def card_html(a, size, minutes):
    desc = a['description']
    if len(desc) > 140:
        desc = desc[:140].rstrip() + '…'
    hay = bh.esc((a['title'] + ' ' + a['description'] + ' ' +
                  strip_html(a['content'])).lower())
    return (f'<a class="bcard s-{size}" href="a/{bh.esc(a["id"])}.html" data-search="{hay}">'
            f'<span class="bcard-cover"><img src="{bh.esc(cover_url(a))}" alt="{bh.esc(a["title"])}" '
            f'width="900" height="506" loading="lazy"></span>'
            f'<span class="bcard-body"><b>{bh.esc(a["title"])}</b>'
            f'<span class="bcard-desc">{bh.esc(desc)}</span>'
            f'<span class="bcard-meta">{minutes} min read · {fmt_date(a["date"])}</span>'
            f'</span></a>')


SEARCH_BAR = ('<div class="blog-search" id="blog-search-bar">'
              '<div class="bsearch-row">' + bh.svg('search') +
              '<input id="blog-q" type="search" placeholder="Search the blog — titles, topics, tools…" '
              'autocomplete="off" spellcheck="false">'
              '<kbd class="blog-search-kbd" aria-hidden="true">S</kbd></div>'
              '</div>')

HUB_JS = '''<script>
/* Blog search: Enter opens a help-style results view (no live filtering).
   Ranking via window.HelpAI (scripts/help-ai.js): typo tolerance, synonyms,
   intent matching — the same engine the help center uses. */
(function () {
  var q = document.getElementById('blog-q');
  if (!q) return;
  var bar = document.getElementById('blog-search-bar'),
      chips = [].slice.call(document.querySelectorAll('.blog-chip')),
      secs = [].slice.call(document.querySelectorAll('.blog-sec')),
      view = document.getElementById('blog-results'),
      grid = document.getElementById('blog-res-grid'),
      meta = document.getElementById('blog-res-meta'),
      title = document.getElementById('blog-res-title'),
      filtersEl = document.getElementById('blog-res-filters'),
      backBtn = document.getElementById('blog-results-back');
  var CATS = {};
  chips.forEach(function (c) { CATS[c.getAttribute('data-cat')] = c.textContent.trim(); });
  var CAT_ORDER = ['all', 'growth', 'content', 'tools', 'premium', 'platform', 'money'];
  var DOCS = [];
  try { DOCS = JSON.parse(document.getElementById('blogSearchData').textContent); } catch (e) {}
  DOCS.forEach(function (d) { d.intent = d.c; });
  var state = { q: '', cat: 'all' };

  function esc(x) {
    return String(x == null ? '' : x).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function mark(raw, term) {
    if (!term) return esc(raw);
    var out = '', low = String(raw).toLowerCase(), i = 0, idx;
    while ((idx = low.indexOf(term, i)) !== -1) {
      out += esc(raw.slice(i, idx)) + '<mark>' + esc(raw.slice(idx, idx + term.length)) + '</mark>';
      i = idx + term.length;
    }
    return out + esc(raw.slice(i));
  }
  function snippet(text, term) {
    var low = String(text).toLowerCase(), i = low.indexOf(term);
    if (i === -1) return String(text).slice(0, 150) + '…';
    var startT = Math.max(0, i - 50);
    return (startT > 0 ? '…' : '') + text.slice(startT, startT + 160) + '…';
  }

  function runSearch() {
    var raw = q.value.trim();
    state.q = raw.toLowerCase();
    state.cat = 'all';
    if (!raw) { showHub(); return; }
    var hits;
    if (window.HelpAI) {
      var ranked = window.HelpAI.scoreAll(raw, DOCS).map(function (x) { return { doc: x.doc, s: x.score }; });
      var seen = {};
      ranked.forEach(function (r) { seen[r.doc.id] = true; });
      DOCS.forEach(function (d) {
        if (seen[d.id]) return;
        var low = (d.t + ' ' + d.d + ' ' + d.b + ' ' + d.f).toLowerCase();
        if (low.indexOf(state.q) !== -1) ranked.push({ doc: d, s: 10 });
      });
      hits = ranked.filter(function (r) { return r.s > 0; })
        .sort(function (a, b) { return b.s - a.s; }).map(function (r) { return r.doc; });
    } else {
      hits = DOCS.filter(function (d) {
        var low = (d.t + ' ' + d.d + ' ' + d.b + ' ' + d.f).toLowerCase();
        return state.q.split(/\s+/).every(function (w) { return low.indexOf(w) !== -1; });
      });
    }
    renderResults(hits, raw);
  }

  function renderResults(hits, raw) {
    secs.forEach(function (s) { s.style.display = 'none'; });
    chips.forEach(function (c) { c.classList.remove('on'); });
    chips.forEach(function (c) { c.style.display = 'none'; });
    view.hidden = false;
    window.scrollTo(0, 0);
    title.textContent = 'Search results';
    meta.textContent = hits.length
      ? hits.length + ' result' + (hits.length > 1 ? 's' : '') + ' for “' + raw + '”'
      : '0 results for “' + raw + '”';
    var counts = { all: hits.length };
    hits.forEach(function (h) { counts[h.c] = (counts[h.c] || 0) + 1; });
    var fhtml = '';
    CAT_ORDER.forEach(function (cid) {
      var n = counts[cid] || 0;
      var label = (cid === 'all' ? 'All topics' : (CATS[cid] || cid));
      fhtml += '<button type="button" class="blog-fchip' + (cid === state.cat ? ' on' : '') +
        (n === 0 ? ' zero' : '') + '" data-fcat="' + cid + '">' + esc(label) +
        ' <span class="blog-fcount">' + n + '</span></button>';
    });
    filtersEl.innerHTML = fhtml;
    filtersEl.querySelectorAll('.blog-fchip').forEach(function (b) {
      b.addEventListener('click', function () {
        state.cat = b.getAttribute('data-fcat');
        filtersEl.querySelectorAll('.blog-fchip').forEach(function (x) {
          x.classList.toggle('on', x.getAttribute('data-fcat') === state.cat);
        });
        paintGrid(hits, raw);
      });
    });
    paintGrid(hits, raw);
    try { history.replaceState(null, '', '#q=' + encodeURIComponent(raw)); } catch (e) {}
    window.scrollTo(0, 0);
  }

  function paintGrid(hits, raw) {
    var shown = hits.filter(function (h) { return state.cat === 'all' || h.c === state.cat; });
    if (!hits.length) {
      grid.innerHTML = '<p class="blog-nores">No articles found for “' + esc(raw) +
        '”. Try a different search — or pick a topic above.</p>';
      return;
    }
    if (!shown.length) {
      grid.innerHTML = '<p class="blog-nores">No ' + esc((CATS[state.cat] || '').toLowerCase()) +
        ' articles match “' + esc(raw) + '” — try another topic.</p>';
      return;
    }
    grid.innerHTML = shown.map(function (d) {
      return '<a class="bcard bcard-text" href="a/' + esc(d.id) + '.html">' +
        '<span class="bcard-body"><b>' + mark(d.t, state.q) + '</b>' +
        '<span class="bcard-desc">' + mark(snippet(d.d + ' ' + d.b, state.q), state.q) + '</span>' +
        '<span class="bcard-meta">' + esc(CATS[d.c] || '') + '</span></span></a>';
    }).join('');
  }

  function showHub() {
    view.hidden = true;
    bar.style.display = '';
    chips.forEach(function (c) { c.style.display = ''; });
    secs.forEach(function (s) { s.style.display = ''; });
    try { history.replaceState(null, '', location.pathname); } catch (e) {}
    window.scrollTo(0, 0);
  }

  /* category chips still filter the hub sections directly */
  chips.forEach(function (ch) {
    ch.addEventListener('click', function () {
      chips.forEach(function (c) { c.classList.toggle('on', c === ch); });
      var cat = ch.getAttribute('data-cat') || 'all';
      secs.forEach(function (s) {
        s.style.display = (cat === 'all' || s.getAttribute('data-cat') === cat) ? '' : 'none';
      });
    });
  });

  /* Enter-only search; Esc or the breadcrumb returns to the hub */
  q.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { e.preventDefault(); runSearch(); }
    if (e.key === 'Escape') { q.value = ''; showHub(); q.blur(); }
  });
  if (backBtn) backBtn.addEventListener('click', function (e) { e.preventDefault(); showHub(); });

  /* deep links: #q=<query> opens results; #cat=<id> pre-selects a chip */
  function applyHash() {
    var h = location.hash || '';
    if (h.indexOf('#q=') === 0) {
      var query = '';
      try { query = decodeURIComponent(h.slice(3)).replace(/\+/g, ' '); } catch (err) {}
      if (query) { q.value = query; runSearch(); return true; }
    }
    if (h.indexOf('#cat=') === 0) {
      var cid = h.slice(5);
      var chip = chips.filter(function (c) { return c.getAttribute('data-cat') === cid; })[0];
      if (chip) { chip.click(); window.scrollTo(0, 0); return true; }
    }
    return false;
  }
  window.addEventListener('hashchange', function () { applyHash(); });
  if (!applyHash()) {
    /* a stray hash (or leftover #q= after navigating back) shouldn't leave a
       broken half-searched page: restore the plain hub view */
    q.value = '';
    showHub();
    chips.forEach(function (c) { c.classList.toggle('on', c.getAttribute('data-cat') === 'all'); });
  }
})();
</script>'''


def build_hub(groups):
    n = sum(len(k) for k in groups.values())
    ntopics = len([c for c in groups if groups[c]])
    lead = ('Field notes on growing Telegram channels — written for channel owners, '
            'not for search engines. No fluff, no “10 hacks” lists: just what works, '
            'from people who schedule posts for a living.')
    order = ('growth', 'content', 'tools', 'premium', 'platform', 'money')
    chips = ''.join(
        f'<button type="button" class="blog-chip{" on" if cid == "all" else ""}" '
        f'data-cat="{cid}">{bh.esc(label)}</button>'
        for cid, label in
        [('all', 'All topics')] + [(c, CATEGORIES[c]['title']) for c in order if groups.get(c)])
    secs = []
    # Monetization reading order: overview first, then rails, then selling.
    MONET_ORDER = ['monetize-telegram-channel', 'telegram-crypto-payments',
                   'telegram-paid-subscriptions', 'telegram-affiliate-marketing',
                   'telegram-stars-for-channel-owners', 'sell-products-in-telegram',
                   'telegram-sponsorships', 'telegram-channel-for-crypto-signals']
    mo = groups.get('money')
    if mo:
        mo.sort(key=lambda a: MONET_ORDER.index(a['id']) if a['id'] in MONET_ORDER else 99)
    for cid in order:
        arts = groups.get(cid)
        if not arts:
            continue
        meta = CATEGORIES[cid]
        cards = [card_html(a, size_for(a, i), reading_minutes(a))
                 for i, a in enumerate(arts)]
        secs.append(
            f'<section class="blog-sec" data-cat="{cid}"><h2>{bh.esc(meta["title"])}</h2>'
            f'<p class="blog-sec-desc">{bh.esc(meta["desc"])}</p>'
            f'<div class="bento">{"".join(cards)}</div></section>')

    body = f'''<div class="blog-wrap">
  <nav class="hc-crumbs" aria-label="Breadcrumb"><a href="../index.html">Fast Scheduler</a>{bh.svg('chev')}<span aria-current="page">Blog</span></nav>
  <header class="blog-hero">
    <h1>Blog</h1>
    <p class="lead">{lead}</p>
    <p class="blog-byline">New pieces added regularly.</p>
  </header>
  {SEARCH_BAR}
  <div class="blog-chips">{chips}</div>
  {''.join(secs)}
  <section id="blog-results" class="blog-results" hidden>
    <nav class="hc-crumbs" aria-label="Breadcrumb"><a href="#" id="blog-results-back">Blog</a>{bh.svg('chev')}<span aria-current="page">Search</span></nav>
    <header class="blog-res-head">
      <h2 id="blog-res-title">Search results</h2>
      <p id="blog-res-meta"></p>
    </header>
    <div class="blog-filters" id="blog-res-filters"></div>
    <div class="bento" id="blog-res-grid"></div>
  </section>
  <div class="hc-cta"><div><b>Own a Telegram channel?</b><p>The scheduling bot this blog is written around — free to start, runs your whole publishing pipeline.</p></div>
  <a class="btn btn-primary" href="{BOT_URL}" target="_blank" rel="noopener noreferrer">{bh.svg('send')} Open Fast Scheduler</a></div>
</div>'''
    title = 'Blog — Growing Telegram Channels: Guides & Field Notes | Fast Scheduler'
    desc = ('In-depth guides on Telegram channel growth, content systems, bots and '
            f'monetization. New guides from the Fast Scheduler team.')
    canonical = f'{SITE}/blog/'
    ld = jsonld({
        '@context': 'https://schema.org', '@type': 'Blog',
        'name': 'Fast Scheduler Blog',
        'description': desc, 'url': canonical,
        'publisher': {'@type': 'Organization', 'name': 'Fast Scheduler', 'url': SITE},
        'blogPost': [{'@type': 'BlogPosting', 'headline': a['title'],
                      'url': f'{SITE}/blog/a/{a["id"]}.html',
                      'image': f'{SITE}/blog/img/{a["id"]}.jpg',
                      'datePublished': a['date']} for a in ARTICLES],
    })
    head = page_head(title, desc, canonical, extra_ld=ld + '\n' + breadcrumb_ld([
        ('Fast Scheduler', SITE + '/'), ('Blog', canonical)]), og_type='website')
    search_json = _search_docs()
    data_tag = f'<script id="blogSearchData" type="application/json">{search_json}</script>'
    ai_tag = '<script src="../scripts/help-ai.js?v=20260930a1"></script>'
    return page_shell(head, body, extra_js=data_tag + ai_tag + HUB_JS)


# -------------------------------------------------------------- articles ---
def build_articles():
    for art in ARTICLES:
        cid = art['category']
        cat = CATEGORIES.get(cid, {'title': 'Blog'})
        canon = f'{SITE}/blog/a/{art["id"]}.html'
        ld_post = jsonld({
            '@context': 'https://schema.org', '@type': 'BlogPosting',
            'headline': art['title'], 'description': art['description'],
            'articleBody': strip_html(art['content'])[:8000],
            'articleSection': cat['title'],
            'author': {'@type': 'Organization', 'name': 'Fast Scheduler', 'url': SITE},
            'publisher': {'@type': 'Organization', 'name': 'Fast Scheduler', 'url': SITE,
                          'logo': {'@type': 'ImageObject', 'url': SITE + '/og-cover-v2.png'}},
            'image': f'{SITE}/blog/img/{art["id"]}.jpg',
            'mainEntityOfPage': canon,
            'datePublished': art['date'], 'dateModified': art['date'],
            'isPartOf': {'@type': 'Blog', 'name': 'Fast Scheduler Blog', 'url': SITE + '/blog/'},
        })
        ld_bread = breadcrumb_ld([
            ('Fast Scheduler', SITE + '/'),
            ('Blog', SITE + '/blog/'),
            (art['title'], canon),
        ])
        head = page_head(art['title'] + ' — Fast Scheduler Blog', art['description'], canon,
                         extra_ld=ld_post + '\n' + ld_bread + (faq_ld(art) or ''))

        heads = headings_of(art['content'])
        mins = reading_minutes(art)
        content = with_heading_ids(art['content'], heads)
        _i = ARTICLES.index(art)
        prev_a = ARTICLES[_i - 1] if _i > 0 else None
        next_a = ARTICLES[_i + 1] if _i < len(ARTICLES) - 1 else None
        crumbs = (f'<nav class="hc-crumbs" aria-label="Breadcrumb">'
                  f'<a href="../index.html">Blog</a>{bh.svg("chev")}'
                  f'<span aria-current="page">{bh.esc(art["title"])}</span></nav>')
        body = f'''<div class="blog-cols">
  <div>
    {crumbs}
    {toc_mobile(heads, art, prev_a, next_a)}
    <article class="blog-doc">
      <h1>{bh.esc(art['title'])}</h1>
      <p class="blog-byline">{cat["title"]} · {fmt_date(art["date"])} · {mins} min read · Fast Scheduler team</p>
      <figure class="blog-doc-cover"><img src="../img/{art['id']}.jpg" alt="{bh.esc(art['title'])}" width="1200" height="675" loading="eager" onerror="this.parentNode.style.display='none'"></figure>
      <div class="hc-body">{content}</div>
      {('<div class="hc-faq"><h2>Common questions</h2>' + ''.join(
          f'<details><summary>{bh.esc_q(f["q"])}</summary><div class="hc-fa"><p>{bh.esc(f["a"])}</p></div></details>'
          for f in art['faq']) + '</div>') if art.get('faq') else ''}
      <div class="blog-moreq"><a href="../index.html#cat={bh.esc(art['category'])}">More on this topic{bh.svg('arrow-r')}</a></div>
      {related_for(art)}
    </article>
    <nav class="hc-pager" aria-label="More articles"><a class="hc-card next" href="../index.html"><span><small>All articles</small><b>Back to the Blog</b></span>{bh.svg("arrow-r")}</a></nav>
    <div class="hc-cta"><div><b>Posting on a schedule?</b><p>Fast Scheduler batch-schedules weeks of Telegram posts in one chat — free to start, posts from your own bot.</p></div>
    <a class="btn" href="{BOT_URL_POST}" target="_blank" rel="noopener noreferrer">{bh.svg('send')} Try Fast Scheduler</a></div>
  </div>
  {toc_html(heads)}
</div>'''
        html = page_shell(head, body, rel='../..', extra_js=TOC_JS)
        io.open(os.path.join(BLOG_A_DIR, art['id'] + '.html'), 'w',
                encoding='utf-8', newline='\n').write(html)


def main():
    os.makedirs(BLOG_A_DIR, exist_ok=True)
    groups = {}
    for a in ARTICLES:
        groups.setdefault(a['category'], []).append(a)

    io.open(os.path.join(BLOG_DIR, 'index.html'), 'w', encoding='utf-8',
            newline='\n').write(build_hub(groups))

    # generated preview covers (royalty-free: drawn at build time, no external assets)
    img_dir = os.path.join(BLOG_DIR, 'img')
    os.makedirs(img_dir, exist_ok=True)
    for art in ARTICLES:
        io.open(os.path.join(img_dir, art['id'] + '.svg'), 'w', encoding='utf-8',
                newline='\n').write(cover_svg(art))
    build_articles()

    # prune stale article pages from removed articles
    valid = {a['id'] + '.html' for a in ARTICLES}
    for fn in os.listdir(BLOG_A_DIR):
        if fn.endswith('.html') and fn not in valid:
            os.remove(os.path.join(BLOG_A_DIR, fn))

    # export the blog search index for the help center's unified search
    io.open(os.path.join(HERE, '_blog_search_data.json'), 'w', encoding='utf-8').write(_search_docs())
    print(f'[ok] blog: {len(ARTICLES)} article pages + hub at blog/index.html')


if __name__ == '__main__':
    main()
