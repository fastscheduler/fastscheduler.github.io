# Generates the full crawlable SEO layer for GitHub Pages:
#   help/a/<id>.html   - one static page per help article (unique title, description,
#                        canonical, OG/Twitter, TechArticle + BreadcrumbList + FAQPage JSON-LD)
#   help/c/<id>.html   - category hub pages (topic clusters + internal linking)
#   sitemap.xml        - every URL
#   llms.txt           - curated map for AI answer engines (llmstxt.org v2 format)
#   llms-full.txt      - complete article corpus as plain markdown (AI/RAG retrieval)
#   og-cover-v2.png       - 1200x630 social preview (PIL)
#   404.html           - branded soft-404
#   .nojekyll          - skip Jekyll on GitHub Pages
# Also injects security + canonical metas into index/help/legal pages.
# Run AFTER build_help.py.  Safe to re-run (idempotent).
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import build_help as bh          # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from src.core.config import (  # noqa: E402
    PREMIUM_PRICE_MONTHLY_CENTS,
    PREMIUM_PRICE_YEARLY_CENTS,
)

# Shared component CSS extracted from help.html's inline <style>: the static
# help pages (help/a, help/c) render the same .hc-* components (crumbs, chips,
# pager, FAQ, CTA…) as help.html but only load main.css, which doesn't define
# them — without this the pages render with giant unsized SVG icons and
# unstyled cards. Regenerate via the extractor if help.html's CSS changes.
try:
    with io.open(os.path.join(HERE, '_hc_component_css.txt'), encoding='utf-8') as _f:
        HC_COMPONENT_CSS = _f.read()
except OSError:  # pragma: no cover - build must not die over styling
    HC_COMPONENT_CSS = ''

SITE = 'https://fastscheduler.github.io'
OUT = os.path.dirname(HERE)   # .../website
import datetime as _dt
BUILD_DATE = _dt.date.today().isoformat()

HELP_A = OUT + os.sep + 'help' + os.sep + 'a'
HELP_C = OUT + os.sep + 'help' + os.sep + 'c'

SECURITY_METAS = (
    '<meta name="referrer" content="strict-origin-when-cross-origin">\n'
    '<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; '
    'script-src \'self\' \'unsafe-inline\' https://www.googletagmanager.com; style-src \'self\' \'unsafe-inline\'; '
    'img-src \'self\' data: https://www.googletagmanager.com https://*.google-analytics.com https://*.analytics.google.com https://www.google.com; font-src \'self\'; connect-src \'self\' https://www.googletagmanager.com https://*.google-analytics.com https://*.analytics.google.com https://region1.google-analytics.com https://www.google.com; frame-src https://www.googletagmanager.com; '
    # NB: frame-ancestors is deliberately absent from this meta CSP — browsers
    # ignore it when it arrives in a <meta> tag and only log a console error.
    # Framing is blocked by the real headers in website/_headers, which any
    # host that supports custom headers (Cloudflare Pages, Netlify) applies.
    'object-src \'none\'; form-action \'self\'; base-uri \'self\'; upgrade-insecure-requests\">'
)


def strip_html(html):
    txt = re.sub(r'<[^>]+>', ' ', html or '')
    return ' '.join(txt.split())


def sec_metas():
    return SECURITY_METAS


def robots_meta():
    return ('<meta name="robots" content="index, follow, max-image-preview:large, '
            'max-snippet:-1, max-video-preview:-1">')


def jsonld(obj):
    return ('<script type="application/ld+json">'
            + json.dumps(obj, ensure_ascii=False) + '</script>')


def breadcrumb_ld(items):
    ents = []
    for i, (name, url) in enumerate(items, 1):
        ents.append({'@type': 'ListItem', 'position': i, 'name': name, 'item': url})
    return jsonld({'@context': 'https://schema.org', '@type': 'BreadcrumbList',
                   'itemListElement': ents})


def page_head(title, desc, canonical, extra_ld='', og_type='article', noindex=False):
    og_img = SITE + '/og-cover-v2.png'
    robots = '<meta name="robots" content="noindex">' if noindex else robots_meta()
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#1faa59">
<meta name="color-scheme" content="light dark">
{sec_metas()}
<title>{bh.esc(title)}</title>
<meta name="description" content="{bh.esc(desc)}">
{robots}
<link rel="canonical" href="{canonical}">
<link rel="describedby" href="https://fastscheduler.github.io/llms.txt">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Fast Scheduler">
<meta property="og:title" content="{bh.esc(title)}">
<meta property="og:description" content="{bh.esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{bh.esc(title)}">
<meta name="twitter:description" content="{bh.esc(desc)}">
<meta name="twitter:image" content="{og_img}">
{bh.FAVICON}
{extra_ld}'''


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


TOPIC_NAV_CSS = '''
  /* Topics rail next to an article: every category with every article, so a
     reader can jump sideways without going back to the hub. */
  .hc-area { display: grid; grid-template-columns: 264px minmax(0, 1fr);
    gap: 34px; align-items: start; max-width: 1200px; margin: 0 auto;
    padding: 22px 20px 40px; }
  .hc-area > .hc-art-col { min-width: 0; }
  .hc-topics { position: sticky; top: 78px; max-height: calc(100vh - 100px);
    overflow-y: auto; padding: 4px 6px 16px 0; font-size: .88rem; }
  .hc-topics-h { font-weight: 800; font-size: .95rem; letter-spacing: -.01em;
    padding: 0 8px 10px; color: var(--text); }
  .hc-topics details { border-radius: 10px; }
  .hc-topics summary { list-style: none; cursor: pointer; display: flex;
    align-items: center; gap: 6px; padding: 8px 8px; border-radius: 8px;
    font-weight: 700; color: var(--text-dim); }
  .hc-topics summary::-webkit-details-marker { display: none; }
  .hc-topics summary:hover { color: var(--green-strong); background: color-mix(in srgb, var(--green) 8%, transparent); }
  .hc-topics summary .n { margin-left: auto; font-size: .72rem; font-weight: 700; opacity: .7; }
  .hc-topics ul { list-style: none; margin: 2px 0 8px; padding: 0 0 0 10px; }
  .hc-topics li a { display: block; padding: 5px 8px; border-radius: 7px;
    color: var(--text-dim); line-height: 1.4; }
  .hc-topics li a:hover { color: var(--green-strong); background: color-mix(in srgb, var(--green) 8%, transparent); text-decoration: none; }
  .hc-topics li a[aria-current="page"] { color: var(--green-strong);
    background: color-mix(in srgb, var(--green) 12%, transparent); font-weight: 700; }
  .hc-topics-toggle { display: none; }
  @media (max-width: 980px) {
    .hc-area { grid-template-columns: minmax(0, 1fr); gap: 6px; }
    .hc-topics { position: static; max-height: none; order: -1;
      border: 1px solid var(--border); border-radius: 12px; padding: 6px 10px;
      margin-bottom: 14px; background: var(--surface); }
    .hc-topics-h { display: none; }
    .hc-topics-toggle { display: flex; align-items: center; gap: 8px;
      width: 100%; padding: 10px 4px; font: inherit; font-weight: 750;
      color: var(--text); background: 0 0; border: 0; cursor: pointer; }
    .hc-topics-toggle svg { width: 17px; height: 17px; color: var(--green-strong); }
    .hc-topics[data-open="0"] details { display: none; }
  }
'''


def topics_nav(groups, art_ids, current_id, current_cat):
    """Every category with EVERY article — the rail is a full index, not a
    preview. The category being read starts expanded."""
    parts = ['<aside class="hc-topics" data-open="0" aria-label="All help topics">',
             '<div class="hc-topics-h">All topics</div>',
             '<button type="button" class="hc-topics-toggle" data-topics-toggle aria-expanded="false">',
             bh.svg('book'), '<span>Browse all topics</span>', bh.svg('chev'), '</button>']
    for g in groups:
        cat = g['cat']
        kids = [k for k in g['kids'] if k['id'] in art_ids]
        if not kids and cat['id'] not in art_ids:
            continue
        rows = []
        if cat['id'] in art_ids:
            cur = ' aria-current="page"' if cat['id'] == current_id else ''
            rows.append(f'<li><a href="{bh.esc(cat["id"])}.html"{cur}>{bh.esc(cat["title"])}</a></li>')
        for k in kids:
            cur = ' aria-current="page"' if k['id'] == current_id else ''
            rows.append(f'<li><a href="{bh.esc(k["id"])}.html"{cur}>{bh.esc(k["title"])}</a></li>')
        opened = ' open' if cat['id'] == current_cat else ''
        parts.append(
            f'<details{opened}><summary>{bh.esc(cat["title"])}'
            f'<span class="n">{len(rows)}</span></summary>'
            f'<ul>{"".join(rows)}</ul></details>')
    parts.append('</aside>')
    return ''.join(parts)


def page_shell(title_html, body, rel='../..'):
    """rel: prefix for assets from the page location (help/a|c are 2 levels deep)."""
    return f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
{NOFLASH}
{title_html}
<link rel="stylesheet" href="{rel}/styles/main.css?v=20261013m3">
<link rel="stylesheet" href="{rel}/styles/hotkeys-modal.css?v=20261006a1">
<style>{HC_COMPONENT_CSS}
{TOPIC_NAV_CSS}
  </style>
</head>
<body class="help">
<header class="site">
  <div class="wrap nav">
    <a class="brand" href="{rel}/index.html" aria-label="Fast Scheduler — home"><span class="brand-mark">{bh.svg('calendar')}</span><span class="brand-full">Fast Scheduler</span></a>
    <a class="nav-link" href="{rel}/blog/index.html">{bh.svg('megaphone')} Blog</a>
    <a class="nav-link" href="{rel}/help.html">{bh.svg('book')} Help Center</a>
    <a class="btn btn-primary nav-cta" data-cta-short="Open" href="{bh.BOT_URL}" target="_blank" rel="noopener noreferrer">{bh.svg('send')}<span>Open Bot</span></a>
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
        <a class="gp-row" role="menuitem" href="https://t.me/FastSchedulerSupport_bot" target="_blank" rel="noopener noreferrer">{bh.svg('send')}<span>Support chat</span>{bh.svg('chev')}</a>
      </div>
    </span>
  </div>
</header>
<main class="legal">
{body}
</main>
<footer class="site">
  <div class="wrap foot">
    <span class="copy">© 2026 Fast Scheduler — free Telegram scheduling bot</span>
    <nav class="links" aria-label="Legal">
      <a href="{rel}/legal/terms.html">Terms</a>
      <a href="{rel}/legal/privacy.html">Privacy</a>
      <a href="{rel}/legal/refundpolicy.html">Refunds</a>
      <a href="{rel}/blog/index.html">Blog</a>
      <a href="{rel}/help.html">Help</a>
    </nav>
  </div>
</footer>
<script src="{rel}/scripts/theme.js?v=20260930a1"></script>
<script src="{rel}/scripts/settings.js"></script>
  <script src="{rel}/scripts/lang.js?v=20261001a1"></script>
<script src="{rel}/scripts/help-search.js?v=20260930a1"></script>
<script src="{rel}/scripts/hotkeys-modal.js?v=20261006a1"></script>
<script src="{rel}/scripts/help-ai.js?v=20260930a1"></script>
<script src="{rel}/scripts/hotkeys.js?v=20260930a1"></script>
<script src="{rel}/scripts/scroll-jump.js?v=20260930a1"></script>
<script>
/* Topics rail on narrow screens: one tap opens the full index. */
document.querySelectorAll('[data-topics-toggle]').forEach(function (b) {{
  b.addEventListener('click', function () {{
    var box = b.parentElement, open = box.getAttribute('data-open') === '1';
    box.setAttribute('data-open', open ? '0' : '1');
    b.setAttribute('aria-expanded', open ? 'false' : 'true');
  }});
}});
</script>
</body>
</html>'''


def main():
    help_sec, _ = bh.load_help_tree()
    bh.apply_web_model(help_sec)
    bh.inject_seo_articles(help_sec)
    groups = bh.build_groups(help_sec)

    article_order = []
    for g in groups:
        for n in [g['cat']] + g['kids']:
            n['c'] = g['cat']['id']
            if n['id'] != 'misc' and bh.art_eligible(n):
                article_order.append(n)
    for g in groups:
        if g['cat']['id'] == 'misc':
            for n in g['kids']:
                n['c'] = 'misc'
                if bh.art_eligible(n):
                    article_order.append(n)

    by_id = {}
    for g in groups:
        for n in [g['cat']] + g['kids']:
            by_id[n['id']] = n
    art_ids = {n['id'] for n in article_order}
    # the misc-group pass can re-add kids already collected above — dedupe once,
    # here, so pages/sitemap/llms all agree (duplicate URLs waste crawl budget)
    _seen = set()
    uniq_articles = [n for n in article_order if not (n['id'] in _seen or _seen.add(n['id']))]

    order_index = {}
    for i, n in enumerate(article_order):
        if i > 0:
            order_index[('prev', n['id'])] = article_order[i - 1]
        if i < len(article_order) - 1:
            order_index[('next', n['id'])] = article_order[i + 1]

    os.makedirs(HELP_A, exist_ok=True)
    os.makedirs(HELP_C, exist_ok=True)

    # ---------------------------------------------------------- articles --
    for n in uniq_articles:
        aid = n['id']
        cat = by_id.get(n['c'], {})
        cat_id, cat_title = cat.get('id', 'misc'), cat.get('title', 'Help')

        def slink(lid):
            t = by_id.get(lid)
            if t and lid in art_ids:
                return f'{bh.esc(lid)}.html'
            if t and t.get('title'):
                return f'../c/{bh.esc(lid)}.html'
            return '../../help.html'

        def slabel(lid):
            t = by_id.get(lid)
            return t['title'] if t and t.get('title') else lid.replace('_', ' ').title()

        body = n['content'] if n.get('_raw_html') else (bh.text_to_html(n['content']) if n['content'] else '')
        faq_html = bh.render_faq(n['faq'], slink, slabel)

        related, seen = [], set()
        for f in n['faq']:
            for lid in f['links']:
                if lid in seen or lid == aid or lid not in by_id:
                    continue
                seen.add(lid)
                related.append(f'<a class="hc-chip" href="{slink(lid)}"><span>{bh.esc(slabel(lid))}</span>{bh.svg("arrow-r")}</a>')
        related_html = (f'<div class="hc-related"><h2>Related topics</h2>'
                        f'<div class="hc-chips">{"".join(related)}</div></div>') if related else ''

        pager = ['<nav class="hc-pager" aria-label="More articles">']
        p, nx = order_index.get(('prev', aid)), order_index.get(('next', aid))
        pager.append(f'<a class="hc-card prev" href="{bh.esc(p["id"])}.html">{bh.svg("arrow-l")}'
                     f'<span><small>Previous</small><b>{bh.esc(p["title"])}</b></span></a>' if p else '<span></span>')
        pager.append(f'<a class="hc-card next" href="{bh.esc(nx["id"])}.html">'
                     f'<span><small>Next</small><b>{bh.esc(nx["title"])}</b></span>{bh.svg("arrow-r")}</a>' if nx else '<span></span>')
        pager.append('</nav>')
        pager_html = ''.join(pager) if (p or nx) else ''

        crumbs = (f'<nav class="hc-crumbs" aria-label="Breadcrumb">'
                  f'<a href="../../help.html">Help Center</a>{bh.svg("chev")}'
                  f'<a href="../c/{bh.esc(cat_id)}.html">{bh.esc(cat_title)}</a>{bh.svg("chev")}'
                  f'<span aria-current="page">{bh.esc(n["title"])}</span></nav>')

        cta = (f'<div class="hc-cta"><div><b>Still stuck?</b>'
               f'<p>The in-bot assistant answers the same questions &mdash; and a human reads every ticket.</p></div>'
               f'<a class="btn" href="{bh.SUPPORT_URL}" target="_blank" rel="noopener noreferrer">{bh.svg("send")} Ask in Telegram</a></div>')

        topics = topics_nav(groups, art_ids, aid, cat_id)
        content = f'''<div class="hc-area">
  {topics}
  <div class="hc-art-col">
    {crumbs}
    <article class="doc">
      <h1>{bh.esc(n['title'])}</h1>
      <div class="hc-body">{body}</div>
      {faq_html}
      {related_html}
    </article>
    {pager_html}
    {cta}
  </div>
</div>'''

        # --- head metadata
        desc = (n.get('description') or strip_html(n['content'])[:160] or n['title']).strip()
        canonical = f'{SITE}/help/a/{aid}.html'
        cat_url = f'{SITE}/help/c/{cat_id}.html'
        ld_tech = jsonld({
            '@context': 'https://schema.org', '@type': 'TechArticle',
            'headline': n['title'], 'description': desc,
            'articleBody': strip_html(body + ' ' + ' '.join(
                (strip_html(f['q']) + ' ' + strip_html(f['a'])) for f in n['faq'])),
            'articleSection': cat_title,
            'author': {'@type': 'Organization', 'name': 'Fast Scheduler', 'url': SITE},
            'publisher': {'@type': 'Organization', 'name': 'Fast Scheduler', 'url': SITE,
                          'logo': {'@type': 'ImageObject', 'url': SITE + '/og-cover-v2.png'}},
            'mainEntityOfPage': canonical,
            'datePublished': BUILD_DATE,
            'dateModified': BUILD_DATE,
            'isPartOf': {'@type': 'WebSite', 'name': 'Fast Scheduler Help', 'url': SITE + '/help.html'},
        })
        ld_bread = breadcrumb_ld([
            ('Fast Scheduler', SITE + '/'),
            ('Help Center', SITE + '/help.html'),
            (cat_title, cat_url),
            (n['title'], canonical),
        ])
        head = page_head(n['title'] + ' — Fast Scheduler Help', desc, canonical,
                         extra_ld=ld_tech + '\n' + ld_bread + (bh.article_faq_ld(n) or ''))
        html = page_shell(head, content)
        io.open(os.path.join(HELP_A, aid + '.html'), 'w', encoding='utf-8', newline='\n').write(html)

    # -------------------------------------------------------- categories --
    cat_urls = []
    for g in groups:
        cid, ctitle = g['cat']['id'], g['cat']['title']
        kids = [k for k in g['kids'] if k['id'] in art_ids]
        cat_art = [g['cat']] if g['cat']['id'] in art_ids else []
        entries = cat_art + kids
        if not entries:
            continue
        cat_urls.append((cid, ctitle, len(entries)))

        items = ''.join(
            f'<li><a href="../a/{bh.esc(k["id"])}.html">{bh.esc(k["title"])}</a></li>'
            for k in entries)
        intro = strip_html(g['cat'].get('description', '') or g['cat'].get('content', ''))[:220]
        lead = f'<p class="lead">{bh.esc(intro)}</p>' if intro else ''
        content = f'''<div class="wrap" style="max-width:860px;margin:0 auto">
  <nav class="hc-crumbs" aria-label="Breadcrumb"><a href="../../help.html">Help Center</a>{bh.svg("chev")}<span aria-current="page">{bh.esc(ctitle)}</span></nav>
  <article class="doc">
    <h1>{bh.esc(ctitle)}</h1>
    {lead}
    <p>{len(entries)} guide{"s" if len(entries) != 1 else ""} in this topic.</p>
    <ul style="line-height:2">{items}</ul>
  </article>
  <div class="hc-cta"><div><b>Can&rsquo;t find an answer?</b><p>Ask in the bot &mdash; a human reads every ticket.</p></div>
  <a class="btn" href="{bh.SUPPORT_URL}" target="_blank" rel="noopener noreferrer">{bh.svg("send")} Ask in Telegram</a></div>
</div>'''
        desc = (intro or f'{ctitle} — guides and answers in the Fast Scheduler help center.').strip()
        canonical = f'{SITE}/help/c/{cid}.html'
        ld = jsonld({
            '@context': 'https://schema.org', '@type': 'CollectionPage',
            'name': ctitle, 'description': desc,
            'url': canonical, 'dateModified': BUILD_DATE,
            'isPartOf': {'@type': 'WebSite', 'name': 'Fast Scheduler Help', 'url': SITE + '/help.html'},
        })
        ld_bread = breadcrumb_ld([
            ('Fast Scheduler', SITE + '/'),
            ('Help Center', SITE + '/help.html'),
            (ctitle, canonical),
        ])
        head = page_head(ctitle + ' — Fast Scheduler Help', desc, canonical,
                         extra_ld=ld + '\n' + ld_bread, og_type='website')
        io.open(os.path.join(HELP_C, cid + '.html'), 'w', encoding='utf-8', newline='\n').write(page_shell(head, content))

    # ----------------------------------------------------------- sitemap --
    # Blog articles (website/_build/blog_articles*.py) join the sitemap too —
    # the blog builder (build_blog.py) runs separately, but crawlers need one
    # canonical URL list.
    blog_arts = []
    try:
        from blog_articles import BLOG_ARTICLES
        from blog_articles_b import BLOG_ARTICLES_B
        from blog_articles_c import BLOG_ARTICLES_C
        from blog_articles_d import BLOG_ARTICLES_D
        from blog_articles_e import BLOG_ARTICLES_E
        from blog_articles_f import BLOG_ARTICLES_F
        from blog_articles_g import BLOG_ARTICLES_G
        from blog_articles_h import BLOG_ARTICLES_H
        from blog_articles_i import BLOG_ARTICLES_I
        blog_arts = (BLOG_ARTICLES + BLOG_ARTICLES_B + BLOG_ARTICLES_C +
                     BLOG_ARTICLES_D + BLOG_ARTICLES_E + BLOG_ARTICLES_F +
                     BLOG_ARTICLES_G + BLOG_ARTICLES_H + BLOG_ARTICLES_I)
    except Exception:  # pragma: no cover - sitemap must not die over the blog
        blog_arts = []

    urls = [(SITE + '/', '1.0'), (SITE + '/help.html', '0.9')]
    if blog_arts:
        urls.append((SITE + '/blog/', '0.8'))
    urls += [(f'{SITE}/blog/a/{a["id"]}.html', '0.7') for a in blog_arts]
    urls += [(f'{SITE}/help/c/{cid}.html', '0.7') for cid, _, _ in cat_urls]
    urls += [(f'{SITE}/help/a/{n["id"]}.html', '0.8') for n in uniq_articles]
    urls += [(SITE + '/legal/privacy.html', '0.4'), (SITE + '/legal/terms.html', '0.4'),
             (SITE + '/legal/refundpolicy.html', '0.4')]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pri in urls:
        sm.append(f'  <url>\n    <loc>{loc}</loc>\n    <lastmod>{BUILD_DATE}</lastmod>\n'
                  f'    <changefreq>weekly</changefreq>\n    <priority>{pri}</priority>\n  </url>')
    sm.append('</urlset>')
    io.open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n').write('\n'.join(sm))

    # ---------------------------------------------------------- llms.txt --
    lines = ['# Fast Scheduler',
             '',
             '> Telegram bot that schedules and auto-publishes posts to Telegram channels — '
             'batch scheduling, recurring messages, sender bots, statistics, backups and team permissions.',
             '',
             f'- Official site: {SITE}',
             '- Bot: https://t.me/FastSchedulerBot',
             '- Support / feedback bot (a human reads every ticket): https://t.me/FastSchedulerSupport_bot',
             f'- Help Center (interactive search): {SITE}/help.html',
             f'- Blog (Telegram channel growth guides): {SITE}/blog/ ({len(blog_arts)} articles)',
             f'- Full help corpus for AI retrieval: {SITE}/llms-full.txt ({len(article_order)} articles)',
             '- Pricing: Free plan (1 channel, 100 pending scheduled messages, 100 sends/channel/month, '
             f'1 recurring message); Premium ${PREMIUM_PRICE_MONTHLY_CENTS / 100:.2f}/month or '
             f'${PREMIUM_PRICE_YEARLY_CENTS / 100:.2f}/year (3 channels, unlimited sends, '
             'unlimited recurring, bigger uploads, leaderboards, backups).',
             f'- Privacy Policy: {SITE}/legal/privacy.html',
             f'- Terms: {SITE}/legal/terms.html',
             f'- Refund Policy: {SITE}/legal/refundpolicy.html',
             '',
             '## Help topics',
             '']
    for cid, ctitle, cnt in cat_urls:
        lines.append(f'- [{ctitle}]({SITE}/help/c/{cid}.html): {cnt} guides')
    lines += ['', '## Key answers', '']
    for n in uniq_articles[:24]:
        desc = (n.get('description') or strip_html(n['content'])[:200] or n['title'])
        lines.append(f'### {n["title"]}')
        lines.append(f'{desc} Full guide: {SITE}/help/a/{n["id"]}.html')
        lines.append('')
    io.open(os.path.join(OUT, 'llms.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))

    # ------------------------------------------------------ llms-full.txt --
    full = ['# Fast Scheduler — complete help center corpus', '',
            f'Exported {BUILD_DATE}. {len(article_order)} articles. '
            f'Canonical pages: {SITE}/help/a/<article-id>.html', '']
    for g in groups:
        entries = [g['cat']] if g['cat']['id'] in art_ids else []
        entries += [k for k in g['kids'] if k['id'] in art_ids]
        if not entries:
            continue
        full.append(f'# {g["cat"]["title"]}')
        full.append('')
        for n in entries:
            full.append(f'## {n["title"]}')
            full.append(f'URL: {SITE}/help/a/{n["id"]}.html')
            full.append('')
            full.append(strip_html(n.get('content', '') or ''))
            for f in n['faq']:
                full.append('')
                full.append(f'Q: {strip_html(f["q"])}')
                full.append(f'A: {strip_html(f["a"])}')
            full.append('')
    io.open(os.path.join(OUT, 'llms-full.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(full))

    # --------------------------------------------------------- 404 page --
    body404 = '''<div class="wrap" style="max-width:640px;margin:0 auto;text-align:center;padding:70px 20px">
  <h1 style="font-size:3rem;margin:0">404</h1>
  <p style="font-size:1.15rem;color:var(--text-dim)">This page wandered off schedule.</p>
  <p style="margin:26px 0"><a class="btn btn-primary" href="/index.html">Back to home</a>
  <a class="btn btn-ghost" href="/help.html">Search the Help Center</a></p>
</div>'''
    head404 = ('<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
               + sec_metas() + '<title>Page not found — Fast Scheduler</title>'
               + '<meta name="robots" content="noindex">'
               + f'<link rel="stylesheet" href="/styles/main.css?v=20261013m3">'
               + f'<link rel="stylesheet" href="/styles/hotkeys-modal.css?v=20261006a1">')
    # full site header: settings menu + "See hotkeys" row so the hotkeys
    # viewer exists on every page, not just home/help/legal
    nav404 = (f"""<header class="site">
  <div class="wrap nav">
    <a class="brand brand-text" href="/index.html" aria-label="Fast Scheduler — home"><span class="brand-mark">{bh.svg('calendar')}</span><span class="brand-full">Fast Scheduler</span><span class="brand-short">FS</span></a>
    <a class="btn btn-primary nav-cta" data-cta-short="Open" href="{bh.BOT_URL}?start=start__website_404" target="_blank" rel="noopener noreferrer">{bh.svg('send')}<span>Open Bot</span></a>
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
        <a class="gp-row" role="menuitem" href="/blog/index.html">{bh.svg('megaphone')}<span>Blog</span></a>
        <a class="gp-row" role="menuitem" href="/help.html">{bh.svg('book')}<span>Help Center</span><svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9 18 15 12 9 6"/></svg></a>
      </div>
    </span>
  </div>
</header>""")
    io.open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8', newline='\n').write(
        f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
{NOFLASH}
{head404}
</head>
<body>
{nav404}
<main class="legal">{body404}</main>
<script src="/scripts/theme.js?v=20260930a1"></script>
<script src="/scripts/settings.js"></script>
  <script src="{rel}/scripts/lang.js?v=20261001a1"></script>
<script src="/scripts/hotkeys.js?v=20260930a1"></script>
<script src="/scripts/hotkeys-modal.js?v=20261006a1"></script>
</body>
</html>''')

    # The social card is NOT generated here. The old PIL make_og_cover() drew
    # the subtitle at a hardcoded x=320 and the footer at x=100 without ever
    # measuring the text, so both ran off the right edge of the 1200px canvas
    # and every link preview clipped them mid-word. The card now comes from
    # tools/make_og_image.mjs, which renders it in headless Chrome with the
    # site's own webfonts and fails the build if anything lands in a croppable
    # margin. Re-run it after changing the copy.

    # --------------------------------------------- inject metas (index/help/legal) --
    inject_existing()

    print(f'[ok] static SEO layer: {len(article_order)} article pages, {len(cat_urls)} category hubs, '
          f'{len(urls)} sitemap URLs, llms-full.txt {os.path.getsize(os.path.join(OUT, "llms-full.txt")) // 1024} KB')


def inject_existing():
    """Add security + canonical/OG metas to pages that predate this generator."""
    targets = {
        'index.html': SITE + '/',
        'help.html': SITE + '/help.html',
        'legal/privacy.html': SITE + '/legal/privacy.html',
        'legal/terms.html': SITE + '/legal/terms.html',
        'legal/refundpolicy.html': SITE + '/legal/refundpolicy.html',
    }
    for rel, canon in targets.items():
        p = os.path.join(OUT, rel)
        if not os.path.exists(p):
            continue
        s = io.open(p, encoding='utf-8').read()
        if 'strict-origin-when-cross-origin' not in s:
            # insert right after the viewport meta (or charset fallback)
            m = re.search(r'<meta name="viewport"[^>]*>', s)
            if not m:
                m = re.search(r'<meta charset="[^"]*">', s)
            if m:
                s = s[:m.end()] + '\n' + SECURITY_METAS + s[m.end():]
        if rel == 'index.html' and '"@type": "WebSite"' not in s:
            org = jsonld({
                '@context': 'https://schema.org', '@type': 'Organization',
                'name': 'Fast Scheduler', 'url': SITE + '/',
                'logo': SITE + '/og-cover-v2.png',
                'description': 'Telegram bot that schedules and auto-publishes channel posts: '
                               'batch scheduling, recurring messages, sender bots, statistics and backups.',
                'sameAs': ['https://t.me/FastSchedulerBot'],
                'contactPoint': {'@type': 'ContactPoint', 'contactType': 'customer support',
                                 'email': 'fastschedulebot@gmail.com'},
            })
            ws = jsonld({
                '@context': 'https://schema.org', '@type': 'WebSite',
                'name': 'Fast Scheduler', 'alternateName': 'Fast Scheduler Telegram bot',
                'url': SITE + '/',
                'potentialAction': {'@type': 'SearchAction',
                                    'target': {'@type': 'EntryPoint', 'urlTemplate': SITE + '/help.html?q={search_term_string}'},
                                    'query-input': 'required name=search_term_string'},
            })
            m = re.search(r'</head>', s)
            if m:
                s = s[:m.start()] + org + chr(10) + ws + chr(10) + s[m.start():]
        if 'rel="canonical"' not in s:
            m = re.search(r'</title>', s)
            if m:
                og = (f'\n<link rel="canonical" href="{canon}">\n'
                      f'<link rel="describedby" href="https://fastscheduler.github.io/llms.txt">\n'
                      f'<meta property="og:url" content="{canon}">\n'
                      f'<meta property="og:image" content="{SITE}/og-cover-v2.png">\n'
                      f'<meta name="twitter:image" content="{SITE}/og-cover-v2.png">')
                s = s[:m.end()] + og + s[m.end():]
        io.open(p, 'w', encoding='utf-8', newline='\n').write(s)


if __name__ == '__main__':
    main()
