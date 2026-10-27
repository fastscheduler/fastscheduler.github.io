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

# Stable per-page publish dates. Help articles have no authored date, and
# stamping them with BUILD_DATE made every rebuild claim all 308 articles were
# published "today" (freshness signal, plus a sitemap whose lastmod never
# matched anything). The first build that sees a page records its date in
# site_dates.json at the repo root (version-controlled, unlike website/_build/)
# and every later build reuses it.
_SITE_DATES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'site_dates.json')


def _load_site_dates():
    try:
        with io.open(_SITE_DATES_PATH, encoding='utf-8') as fh:
            d = json.load(fh)
    except Exception:
        d = {}
    d.setdefault('help', {})
    d.setdefault('hub', {})
    d.setdefault('legal', {})
    d.setdefault('site', {})
    return d


def publish_date(section, key):
    """First-seen ISO date for one page (stable across rebuilds)."""
    d = _load_site_dates()
    slot = d.setdefault(section, {})
    if key not in slot:
        slot[key] = BUILD_DATE
        try:
            with io.open(_SITE_DATES_PATH, 'w', encoding='utf-8', newline='\n') as fh:
                json.dump(d, fh, indent=1, sort_keys=True, ensure_ascii=False)
                fh.write('\n')
        except Exception as e:       # bookkeeping must never break a build
            print('[warn] could not write site_dates.json: %s' % e)
    return slot[key]

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
    txt = re.sub(r'<[^>]+>', ' ', bh.plain_links(html or ''))
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


def article_meta(pub, mod=None):
    """article:* Open Graph / freshness meta. Crawlers that skip JSON-LD
    still read these; they are also what Telegram/Slack previews use."""
    mod = mod or pub
    return ('<meta property="article:published_time" content="%s">'
            '<meta property="article:modified_time" content="%s">'
            '<meta property="article:section" content="Fast Scheduler">'
            % (pub, mod))


def page_head(title, desc, canonical, extra_ld='', og_type='article', noindex=False,
              extra_meta=''):
    og_img = SITE + '/og-cover-v2.png'
    _depth = canonical[len(SITE):].strip('/').count('/')
    _rel = '../' * _depth
    # One SERP-shaped title/description for every page type on the site.
    title = bh.fit_title(title)
    desc = bh.smart_desc(desc)
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
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Fast Scheduler">
<meta property="og:title" content="{bh.esc(title)}">
<meta property="og:description" content="{bh.esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{bh.esc(title)}">
<meta name="twitter:description" content="{bh.esc(desc)}">
<meta name="twitter:image" content="{og_img}">{extra_meta}
{bh.favicon(_rel)}
{bh.site_entity_ld()}
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
    var _ffs = localStorage.getItem('fs-font') || localStorage.getItem('fs-help-font') || localStorage.getItem('fs-blog-font');
    if (_ffs) { document.documentElement.setAttribute('data-font', _ffs); }
  } catch (e) {}
</script>'''


def page_shell(title_html, body, rel='../..', lang='en'):
    """One shell for every generated page, in every language.

    There used to be a second, hand-copied Russian shell (``page_shell_ru``):
    the same markup, the same script list and the same footer, typed out again
    in Russian. Every chrome change had to be made twice, and the copies drifted
    apart. The language now changes only the strings
    (``translations/website/*.json``) and the /ru/ link prefix.
    """
    def t(key):
        return bh.tr(key, lang)

    R = rel + ('/ru' if lang == 'ru' else '')
    NAV = bh.unified_nav(rel, bh.BOT_URL, bh.settings_menu(bh.SUPPORT_URL, lang), lang=lang)
    FOOT = ('<footer class="site">' + chr(10)
            + '  <div class="wrap foot">' + chr(10)
            + '    <span class="copy">' + t('footer_copy') + '</span>' + chr(10)
            + '    <nav class="links" aria-label="' + t('footer_legal') + '">' + chr(10)
            + '      <a href="' + R + '/legal/terms.html">' + t('footer_terms') + '</a>' + chr(10)
            + '      <a href="' + R + '/legal/privacy.html">' + t('footer_privacy') + '</a>' + chr(10)
            + '      <a href="' + R + '/legal/refundpolicy.html">' + t('footer_refunds') + '</a>' + chr(10)
            + '      <a href="' + R + '/blog/index.html">' + t('blog') + '</a>' + chr(10)
            + '      <a href="' + R + '/help.html">' + t('footer_help') + '</a>' + chr(10)
            + '    </nav>' + chr(10)
            + '  </div>' + chr(10)
            + '</footer>')
    return ('<!DOCTYPE html>' + chr(10)
            + '<html lang="' + lang + '" data-theme="light">' + chr(10)
            + '<head>' + chr(10)
            + NOFLASH + chr(10)
            + title_html + chr(10)
            + '<link rel="stylesheet" href="' + rel + '/styles/main.css?v=20261022a1">' + chr(10)
            + '<link rel="stylesheet" href="' + rel + '/styles/hotkeys-modal.css?v=20261006a1">' + chr(10)
            + '<style>' + HC_COMPONENT_CSS + chr(10)
            + '  </style>' + chr(10)
            + '</head>' + chr(10)
            + '<body class="help">' + chr(10)
            + NAV + chr(10)
            + '<main class="legal">' + chr(10)
            + body + chr(10)
            + '</main>' + chr(10)
            + FOOT + chr(10)
            + '<script src="' + rel + '/scripts/theme.js?v=20260930a1"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/settings.js?v=20261005d1"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/ru-content.js?v=20261004b2"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/ru-chrome.js?v=20261005e1"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/lang.js?v=20261007a1"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/hotkeys-modal.js?v=20261006a1"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/help-ai.js?v=20261022a1"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/help-search.js?v=20261022a3"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/hotkeys.js?v=20261005d1"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/scroll-jump.js?v=20260930a1"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/article-nav.js?v=20260930a2"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/site-footer.js?v=20261018g2"></script>' + chr(10)
            + '</body>' + chr(10)
            + '</html>')


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

    # Title disambiguation. "<Article> — Fast Scheduler Help" is too short for
    # a one-word article ("Cloud" -> 27 chars) and collides whenever two
    # articles share a title across categories (Export vs the Glossary entry
    # Export, Premium vs glossary_premium, Getting Started vs start, ...).
    # Qualify exactly those with their category so every title stays unique
    # and lands in the 30-65 char band search results actually show.
    _base_titles = {}
    for _n in uniq_articles:
        _cat = by_id.get(_n.get('c'), {})
        if _cat.get('id') and _n['id'] == _cat.get('id'):
            # The category's own landing article: help/a/backup.html sits
            # beside help/c/backup.html. It carries no prose, only FAQ, and
            # its title collided with the real guide of the same name
            # (start.html vs getting_started.html, both "Getting Started").
            # Name it for what it actually is.
            _base_titles[_n['id']] = '%s Overview \u2014 Fast Scheduler Help' % _n['title']
        else:
            _base_titles[_n['id']] = '%s \u2014 Fast Scheduler Help' % _n['title']
    _counts = {}
    for _t in _base_titles.values():
        _counts[_t] = _counts.get(_t, 0) + 1
    page_title = {}
    for _n in uniq_articles:
        # The headline already names the task. A "— Fast Scheduler Help"
        # suffix ate 23 characters of the ~60 Google shows, so long titles
        # were cut mid-phrase ("...on Telegram: What"). Use the headline
        # alone, and disambiguate only genuine duplicates with the category.
        _t = _n['title']
        _cat = by_id.get(_n.get('c'), {})
        _ct = _cat.get('title', '')
        if _counts.get('%s — Fast Scheduler Help' % _t, 0) > 1 and _ct:
            _t = '%s — %s' % (_t, _ct)
        # Search results need the brand: a bare "Adding Photos & Videos" reads
        # like a generic how-to and loses the click to YouTube/Telegram docs.
        # Keep the whole headline and append the brand only when it still fits
        # inside the ~60 character SERP cut.
        if len(_t) <= 38:
            _t = '%s — Fast Scheduler Help' % _t
        elif len(_t) + 16 <= 62:
            _t = '%s | Fast Scheduler' % _t
        page_title[_n['id']] = _t

    # Second pass: two articles can share a title (the category landing page
    # "Premium" and the glossary entry "Premium"). Name the landing page as an
    # overview so every <title> stays unique and descriptive.
    _seen_titles = {}
    for _n in uniq_articles:
        _t = page_title[_n['id']]
        if _t in _seen_titles:
            _cat = by_id.get(_n.get('c'), {})
            if _n['id'] == _cat.get('id'):
                _t = '%s Overview — Fast Scheduler Help' % _n['title']
            else:
                _t = '%s — %s — Fast Scheduler Help' % (
                    _n['title'], _cat.get('title', 'Help'))
            page_title[_n['id']] = _t
        _seen_titles[_t] = 1

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
        # Cross-article links inside the prose are hash routes on the hub; on a
        # static page the target lives beside this file, so rewrite them to the
        # real URL (crawlers and no-JS readers get a working link too).
        def _static_link(s):
            # Hash links inside an article point at article ids. On the static
            # mirror each id is a sibling .html file — unless the id is a
            # category page (it has children) or has no page at all, in which
            # case send the reader somewhere that really exists.
            def _repl(m):
                lid = m.group(1)
                if lid in art_ids:
                    return '%s.html' % lid
                if lid in by_id:
                    return '../c/%s.html' % lid
                return '../../help.html'
            return re.sub(r'#/a/([A-Za-z0-9_-]+)', _repl, s)
        body = _static_link(body)
        faq_html = _static_link(faq_html)

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

        content = f'''<div class="wrap legal-layout" style="display:block;max-width:860px;margin:0 auto">
  {crumbs}
  <article class="doc">
    <h1>{bh.esc(n['title'])}</h1>
    <div class="hc-body">{body}</div>
    {faq_html}
    {related_html}
  </article>
  {pager_html}
  {cta}
</div>'''

        # --- head metadata
        # Category articles ship no `description` field, so the old build
        # fell back to the bare title ("Backup" as a 6-character snippet).
        _dsrc = (n.get('description') or '').strip()
        if len(_dsrc) < 70:
            _body = strip_html(n['content'])
            if len(_body) < 70 and n.get('faq'):
                # Category landing articles have no prose; the questions
                # are the only sentence-like text they have, and two of
                # them are not enough to reach the 70 character floor.
                _qs = ' '.join(strip_html(f['q']) for f in n['faq'][:4])
                _body = ('%s: %s' % (n['title'], _qs)).strip()
            _dsrc = _body or _dsrc or n['title']
        desc = bh.smart_desc(_dsrc)
        canonical = f'{SITE}/help/a/{aid}.html'
        cat_url = f'{SITE}/help/c/{cat_id}.html'
        pub_date = publish_date('help', aid)
        ld_tech = jsonld({
            '@context': 'https://schema.org', '@type': 'TechArticle',
            'headline': n['title'], 'description': desc,
            'articleBody': strip_html(body + ' ' + ' '.join(
                (strip_html(f['q']) + ' ' + strip_html(f['a'])) for f in n['faq'])),
            'articleSection': cat_title,
            'author': {'@id': bh.ORG_ID},
            'publisher': {'@id': bh.ORG_ID},
            'mainEntityOfPage': canonical,
            'datePublished': pub_date,
            'dateModified': pub_date,
            'isPartOf': {'@id': bh.WEBSITE_ID},
        })
        ld_bread = breadcrumb_ld([
            ('Fast Scheduler', SITE + '/'),
            ('Help Center', SITE + '/help.html'),
            (cat_title, cat_url),
            (n['title'], canonical),
        ])
        head = page_head(page_title[aid], desc, canonical,
                         extra_ld=ld_tech + '\n' + ld_bread + (bh.article_faq_ld(n) or ''),
                         extra_meta=article_meta(pub_date))
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
        intro = strip_html(g['cat'].get('description', '') or g['cat'].get('content', ''))
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
        # Lead with the category so the hub's snippet never repeats the
        # lead article's verbatim (17 pairs were byte-identical).
        desc = bh.smart_desc(
            f'{ctitle}: {len(entries)} guides in the Fast Scheduler help center. '
            f'{intro or "guides and answers for " + ctitle.lower()}')
        canonical = f'{SITE}/help/c/{cid}.html'
        ld = jsonld({
            '@context': 'https://schema.org', '@type': 'CollectionPage',
            'name': ctitle, 'description': desc,
            'url': canonical, 'dateModified': publish_date('hub', cid),
            'isPartOf': {'@id': bh.WEBSITE_ID},
        })
        ld_bread = breadcrumb_ld([
            ('Fast Scheduler', SITE + '/'),
            ('Help Center', SITE + '/help.html'),
            (ctitle, canonical),
        ])
        # Distinct from the same-named article page (a category and its
        # lead article share an id, so both used "<Category> — Fast
        # Scheduler Help" and collided on 24 titles).
        head = page_head(f'{ctitle} — {len(entries)} Guides | Fast Scheduler', desc, canonical,
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
        from blog_articles_j import BLOG_ARTICLES_J
        from blog_articles_k import BLOG_ARTICLES_K
        blog_arts = (BLOG_ARTICLES + BLOG_ARTICLES_B + BLOG_ARTICLES_C +
                     BLOG_ARTICLES_D + BLOG_ARTICLES_E + BLOG_ARTICLES_F +
                     BLOG_ARTICLES_G + BLOG_ARTICLES_H + BLOG_ARTICLES_I +
                     BLOG_ARTICLES_J + BLOG_ARTICLES_K)
    except Exception:  # pragma: no cover - sitemap must not die over the blog
        blog_arts = []

    # lastmod is only useful if it is real: blog articles carry their
    # publication date, help pages their first-seen date, hubs/legal the build
    # date (those genuinely change on every rebuild).
    blog_dates = {}
    for a in blog_arts:
        d = a.get('date') or a.get('published') or a.get('updated')
        if d:
            blog_dates[a['id']] = str(d)[:10]
    urls = [(SITE + '/', '1.0', publish_date('site', 'home')),
            (SITE + '/help.html', '0.9', publish_date('site', 'help'))]
    if blog_arts:
        latest_blog = max(blog_dates.values()) if blog_dates else BUILD_DATE
        urls.append((SITE + '/blog/', '0.8', latest_blog))
    urls += [(f'{SITE}/blog/a/{a["id"]}.html', '0.7', blog_dates.get(a['id'], BUILD_DATE))
             for a in blog_arts]
    urls += [(f'{SITE}/help/c/{cid}.html', '0.7', publish_date('hub', cid))
             for cid, _, _ in cat_urls]
    urls += [(f'{SITE}/help/a/{n["id"]}.html', '0.8', publish_date('help', n['id']))
             for n in uniq_articles]
    # Hand-authored deep dives (content lives in scripts/help-extra.js) are
    # linked from the Help Center and the home page but are not part of the
    # translations tree, so they need explicit sitemap entries. Without these
    # they stayed crawlable-but-orphaned and never accumulated signals.
    _extra_guides = ['guide_overview', 'guide_interface_map',
                     'guide_schedule_format', 'guide_media_modes',
                     'guide_batch_file', 'guide_fix_duplicates']
    urls += [(f'{SITE}/help/a/{_g}.html', '0.7', publish_date('help', _g))
             for _g in _extra_guides
             if os.path.isfile(os.path.join(HELP_A, _g + '.html'))]
    for _slug in ('privacy', 'terms', 'refundpolicy'):
        urls.append((SITE + '/legal/%s.html' % _slug, '0.4',
                     publish_date('legal', _slug)))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pri, lastmod in urls:
        sm.append(f'  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lastmod}</lastmod>\n'
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
             'unlimited recurring, 100MB media, leaderboards, backups).'
             ' Batch scheduling (many posts in one message or a .txt file) is included on both plans.',
             f'- Privacy Policy: {SITE}/legal/privacy.html',
             f'- Terms: {SITE}/legal/terms.html',
             f'- Refund Policy: {SITE}/legal/refundpolicy.html',
             '',
             '## What is Fast Scheduler',
             '',
             'Fast Scheduler is a Telegram post scheduler bot. Its official bot is '
             '@FastSchedulerBot (https://t.me/FastSchedulerBot), support is '
             '@FastSchedulerSupport_bot, and the official site is ' + SITE + '. It queues, '
             'schedules and auto-publishes posts to Telegram channels, with batch scheduling, '
             'recurring messages, sender bots, statistics, backups and team permissions. '
             'Several unrelated products share the name "Fast Scheduler"; this bot is not '
             'affiliated with them. Reference: ' + SITE + '/help/a/qa_what_is_fast_scheduler.html',
             '',
             '## Batch scheduling format (many posts in one message)',
             '',
             'One block = one post. The first line is the date and time; the lines below are '
             'the post body; one blank line separates one post from the next. Send all blocks '
             'in a single Telegram message, or upload the same text as a UTF-8 .txt file while '
             'scheduling. Works on Free and Premium; the only ceiling is the pending queue '
             '(100 on Free).',
             '',
             '    today 10:23',
             '    Morning news digest: three stories worth your time',
             '    <inline>Read more<link="https://example.com/news">',
             '',
             '    tomorrow 7:24 PM',
             '    Poll day — which topic next?',
             '',
             '    12.12.2026 18:28',
             '    New drop is live. Limited stock, 24 hours only.',
             '    <inline>Shop now<link="https://example.com/shop" style="success"> -- <inline>Details<link="https://example.com/faq">',
             '',
             '    23-10-2027 15:34',
             '    Reminder: the community call starts in 30 minutes.',
             '',
             'Accepted first lines: `today HH:MM`, `tomorrow HH:MM`, `day after tomorrow HH:MM`, '
             '`DD.MM.YYYY HH:MM` (also `/` and `-`), ISO `YYYY-MM-DD HH:MM`, and a bare `HH:MM`. '
             'AM/PM suffixes are supported. Inline buttons: '
             '`<inline>Button Text<link="https://example.com">`, callback buttons with '
             '`<callback="data">`, `--` keeps buttons on one row, `//` starts a new row, '
             '`style="success|danger|primary"` is optional. A blank line inside a post ends it. '
             'Full reference: ' + SITE + '/help/a/qa_schedule_many_at_once.html',
             '',
             '## Help topics',
             '']
    for cid, ctitle, cnt in cat_urls:
        lines.append(f'- [{ctitle}]({SITE}/help/c/{cid}.html): {cnt} guides')
    lines += ['', '## Key answers', '']
    # Pin the entity + batch-format answers first: answer engines quote the top of
    # this list, and these two define what Fast Scheduler is and how its input
    # format works.
    for _pin in ('qa_what_is_fast_scheduler', 'qa_schedule_many_at_once'):
        _n = next((a for a in article_order if a.get('id') == _pin), None)
        if _n is None:
            continue
        lines.append(f'### {_n["title"]}')
        lines.append(f'{bh.smart_desc(_n.get("description") or strip_html(_n["content"]) or _n["title"])} '
                     f'Full guide: {SITE}/help/a/{_n["id"]}.html')
        lines.append('')
    _pinned_ids = {'qa_what_is_fast_scheduler', 'qa_schedule_many_at_once'}
    for n in uniq_articles[:24]:
        if n['id'] in _pinned_ids:
            continue
        desc = bh.smart_desc(
            n.get('description') or strip_html(n['content']) or n['title'])
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
  <p style="margin:26px 0"><a class="btn btn-primary" href="./index.html">Back to home</a>
  <a class="btn btn-ghost" href="./help.html">Search the Help Center</a></p>
</div>'''
    head404 = ('<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
               + sec_metas() + '<title>Page not found — Fast Scheduler</title>'
               + '<meta name="description" content="That Fast Scheduler page does '
               'not exist. Search the Help Center or open the blog for guides on '
               'scheduling Telegram channel posts.">'
               + '<meta name="robots" content="noindex, follow">'
               + f'<link rel="stylesheet" href="./styles/main.css?v=20261022a1">'
               + f'<link rel="stylesheet" href="./styles/hotkeys-modal.css?v=20261006a1">'
               + bh.site_entity_ld())
    # full site header: settings menu + "See hotkeys" row so the hotkeys
    # viewer exists on every page, not just home/help/legal
    _menu404 = (f'''<div class="gp-head">Settings</div>
        <button type="button" class="gp-row" aria-pressed="false" id="rowDark">{bh.svg('moon')}<span>Dark mode</span><span class="io-switch" aria-hidden="true"></span></button>
        <button type="button" class="gp-row" aria-pressed="true" id="rowAnim">{bh.svg('zap')}<span>Animations</span><span class="io-switch" aria-hidden="true"></span></button>
        <button type="button" class="gp-row" aria-pressed="true" id="rowFx">{bh.svg('sparkles')}<span>Effects</span><span class="io-switch" aria-hidden="true"></span></button>
        <button type="button" class="gp-row" aria-pressed="true" id="rowKeys">{bh.svg('keys')}<span>Hotkeys</span><span class="io-switch" aria-hidden="true"></span></button>
        <div class="gp-row gp-fonts" data-fonts>{bh.svg('book')}<span>Font size</span><span class="hc-fonts"><button type="button" data-font="s" aria-label="Small">A</button><button type="button" data-font="m" aria-label="Default">A</button><button type="button" data-font="l" aria-label="Large">A</button></span></div>
        <button type="button" class="gp-row gp-row-sub" id="rowKeysHelp"><svg viewBox="0 0 24 24" fill="none" stroke="none" aria-hidden="true" style="visibility:hidden;width:18px;height:18px"></svg><span class="gp-sub-label">See hotkeys</span><svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9 18 15 12 9 6"/></svg></button>
        <div class="gp-sep" role="separator"></div>
        <a class="gp-row" href="https://t.me/FastSchedulerSupport_bot" target="_blank" rel="noopener noreferrer">{bh.svg('send')}<span>Support chat</span>{bh.svg('chev')}</a>''')
    nav404 = bh.unified_nav('', bh.BOT_URL + '?start=start__website_404', _menu404, with_search=False)
    page404 = (
        f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
{NOFLASH}
{head404}
</head>
<body>
{nav404}
<main class="legal">{body404}</main>
<script src="./scripts/theme.js?v=20260930a1"></script>
<script src="./scripts/settings.js?v=20261005d1"></script>
<script src="./scripts/ru-content.js?v=20261004b2"></script>
<script src="./scripts/ru-chrome.js?v=20261005e1"></script>
<script src="./scripts/lang.js?v=20261007a1"></script>
<script src="./scripts/hotkeys.js?v=20261005d1"></script>
<script src="./scripts/hotkeys-modal.js?v=20261006a1"></script>
<script src="./scripts/site-footer.js?v=20261018g2"></script>
</body>
</html>''')
    # nav markup is built with rel='' (site root); a 404 is served from the
    # project subpath, so keep its assets relative to the page itself
    page404 = page404.replace('src="/brand-logo-128.png"', 'src="./brand-logo-128.png"')
    io.open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8', newline='\n').write(page404)
    # portable root mirror (like index.html): relative asset paths so the
    # page renders styled from file:// and from a repo-root deploy
    root404 = page404.replace('href="/', 'href="./').replace('src="/', 'src="./')
    io.open(os.path.join(os.path.dirname(OUT), '404.html'), 'w',
            encoding='utf-8', newline='\n').write(root404)

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
                      f'<meta property="og:url" content="{canon}">\n'
                      f'<meta property="og:image" content="{SITE}/og-cover-v2.png">\n'
                      f'<meta name="twitter:image" content="{SITE}/og-cover-v2.png">')
                s = s[:m.end()] + og + s[m.end():]
        io.open(p, 'w', encoding='utf-8', newline='\n').write(s)


if __name__ == '__main__':
    main()
