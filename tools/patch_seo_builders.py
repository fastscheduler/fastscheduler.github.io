#!/usr/bin/env python
"""Idempotent SEO patches for the website builders in website/_build/.

website/_build/ is gitignored (local build tooling, not published source), so
these edits cannot go through the normal file-edit tools. They live here as a
reviewable, re-runnable patch script instead.

Run:  python tools/patch_seo_builders.py          # apply (idempotent)
      python tools/patch_seo_builders.py --check  # report only, exit 1 if a
                                                  # patch is missing
"""
from __future__ import annotations

import argparse
import os
import sys

BUILD = os.path.join("website", "_build")
CHANGED = []


def sub(path, old, new, count=1, label=None):
    """Replace `old` with `new` in website/_build/<path>."""
    full = os.path.join(BUILD, path)
    s = open(full, encoding="utf-8").read()
    tag = label or old.splitlines()[0].strip()[:66]
    if new in s and old not in s:
        return 0
    if old not in s:
        raise SystemExit("ANCHOR MISSING in %s:\n---\n%s\n---" % (path, old[:300]))
    if count == 0:                       # replace every occurrence
        n = s.count(old)
        s = s.replace(old, new)
    else:
        if s.count(old) < count:
            raise SystemExit("expected %d occurrences in %s, found %d:\n%s"
                             % (count, path, s.count(old), old[:300]))
        s = s.replace(old, new, count)
    open(full, "w", encoding="utf-8", newline="\n").write(s)
    CHANGED.append("%s :: %s" % (path, tag))
    return 1


# --------------------------------------------------------------- build_help
def patch_help():
    n = 0
    # (1) One FAQPage per URL, not ~100 inlined in the hub's <body>.
    n += sub("build_help.py", """                       by_id, order_index)
        + article_faq_ld(n)
        for n in article_order)""", """                       by_id, order_index)
        for n in article_order)
    # No per-article FAQPage JSON-LD inlined here. Google expects one FAQPage
    # per URL and treats ~100 of them as structured-data spam; it also cost
    # 92 KB of body markup. Every article here also has a static page
    # (help/a/<id>.html) whose <head> carries the same FAQPage markup
    # (build_static.py emits it). The hub declares itself a CollectionPage
    # with an ItemList of all articles instead — the schema Google recommends
    # for an index page, and an explicit statement of which URLs are canonical.""")
    # (2) Heading outline: the hub is ONE page, so only its hero title is an h1.
    n += sub("build_help.py", '<h1>{esc(cat["title"])}</h1>', '<h2>{esc(cat["title"])}</h2>')
    n += sub("build_help.py", '<h1>{esc(n["title"])}</h1>', '<h2>{esc(n["title"])}</h2>')
    n += sub("build_help.py", '<h1>Search results</h1>', '<h2>Search results</h2>')
    n += sub("build_help.py", '<h1>Page not found</h1>', '<h2>Page not found</h2>')
    n += sub("build_help.py", ".view h1:focus {", ".view h1:focus, .view h2:focus {")
    n += sub("build_help.py", ".hc-cat-head h1 {", ".hc-cat-head h1, .hc-cat-head h2 {", count=0)
    n += sub("build_help.py", ".hc-art > h1 {", ".hc-art > h1, .hc-art > h2 {", count=0)
    n += sub("build_help.py", ".hc-404 h1 {", ".hc-404 h1, .hc-404 h2 {")
    n += sub("build_help.py", 'html[data-hcfont="l"] .hc-art > h1 {',
             'html[data-hcfont="l"] .hc-art > h1, html[data-hcfont="l"] .hc-art > h2 {')
    n += sub("build_help.py", "var h1 = el.querySelector('h1');",
             "var h1 = el.querySelector('h1, h2');")
    # (3) CollectionPage + ItemList so Google knows this URL indexes every
    #     article's canonical URL.
    n += sub("build_help.py", """    year = datetime.date.today().year
    n_cats = len(groups)""", """    year = datetime.date.today().year
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
    }, ensure_ascii=False)""")
    n += sub("build_help.py", """      {{"@type": "ListItem", "position": 2, "name": "Help Center", "item": "https://fastscheduler.github.io/help.html"}}
    ]
  }}
  </script>""", """      {{"@type": "ListItem", "position": 2, "name": "Help Center", "item": "https://fastscheduler.github.io/help.html"}}
    ]
  }}
  </script>
  <script type="application/ld+json">{HELP_INDEX_LD}</script>""")
    return n


# ------------------------------------------------------------- build_static
STATIC_DATE_HELPERS = '''BUILD_DATE = _dt.date.today().isoformat()

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
    return d


def publish_date(section, key):
    """First-seen ISO date for one page (stable across rebuilds)."""
    d = _load_site_dates()
    slot = d.setdefault(section, {})
    if key not in slot:
        slot[key] = BUILD_DATE
        try:
            with io.open(_SITE_DATES_PATH, 'w', encoding='utf-8', newline='\\n') as fh:
                json.dump(d, fh, indent=1, sort_keys=True, ensure_ascii=False)
                fh.write('\\n')
        except Exception as e:       # bookkeeping must never break a build
            print('[warn] could not write site_dates.json: %s' % e)
    return slot[key]'''


def patch_static():
    n = 0
    n += sub("build_static.py", "BUILD_DATE = _dt.date.today().isoformat()", STATIC_DATE_HELPERS)
    # help articles: real (stable) dates + article:* Open Graph meta
    n += sub("build_static.py", """            'mainEntityOfPage': canonical,
            'datePublished': BUILD_DATE,
            'dateModified': BUILD_DATE,""", """            'mainEntityOfPage': canonical,
            'datePublished': pub_date,
            'dateModified': pub_date,""")
    n += sub("build_static.py", """        canonical = f'{SITE}/help/a/{aid}.html'
        cat_url = f'{SITE}/help/c/{cat_id}.html'""", """        canonical = f'{SITE}/help/a/{aid}.html'
        cat_url = f'{SITE}/help/c/{cat_id}.html'
        pub_date = publish_date('help', aid)""")
    n += sub("build_static.py", """        head = page_head(n['title'] + ' — Fast Scheduler Help', desc, canonical,
                         extra_ld=ld_tech + '\\n' + ld_bread + (bh.article_faq_ld(n) or ''))""",
             """        head = page_head(n['title'] + ' — Fast Scheduler Help', desc, canonical,
                         extra_ld=ld_tech + '\\n' + ld_bread + (bh.article_faq_ld(n) or ''),
                         extra_meta=article_meta(pub_date))""")
    # page_head gains an extra_meta slot
    n += sub("build_static.py", """def page_head(title, desc, canonical, extra_ld='', og_type='article', noindex=False):""",
             """def article_meta(pub, mod=None):
    \"\"\"article:* Open Graph / freshness meta. Crawlers that skip JSON-LD
    still read these; they are also what Telegram/Slack previews use.\"\"\"
    mod = mod or pub
    return ('<meta property="article:published_time" content="%s">'
            '<meta property="article:modified_time" content="%s">'
            '<meta property="article:section" content="Fast Scheduler">'
            % (pub, mod))


def page_head(title, desc, canonical, extra_ld='', og_type='article', noindex=False,
              extra_meta=''):""")
    n += sub("build_static.py", """<meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{bh.esc(title)}">
<meta name="twitter:description" content="{bh.esc(desc)}">
<meta name="twitter:image" content="{og_img}">
<link rel="icon" href="{bh.FAVICON}">""", """<meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{bh.esc(title)}">
<meta name="twitter:description" content="{bh.esc(desc)}">
<meta name="twitter:image" content="{og_img}">{extra_meta}
<link rel="icon" href="{bh.FAVICON}">""")
    # 404: it already says noindex; give it a description so a soft-404 or a
    # shared link still renders a sensible snippet.
    n += sub("build_static.py", """+ '<title>Page not found — Fast Scheduler</title>'
               + '<meta name="robots" content="noindex">'""",
             """+ '<title>Page not found — Fast Scheduler</title>'
               + '<meta name="description" content="That Fast Scheduler page does '
               'not exist. Search the Help Center or open the blog for guides on '
               'scheduling Telegram channel posts.">'
               + '<meta name="robots" content="noindex, follow">'""")
    # sitemap: real lastmod per URL (blog publication dates, stable help dates)
    n += sub("build_static.py", """    urls = [(SITE + '/', '1.0'), (SITE + '/help.html', '0.9')]
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
        sm.append(f'  <url>\\n    <loc>{loc}</loc>\\n    <lastmod>{BUILD_DATE}</lastmod>\\n'
                  f'    <changefreq>weekly</changefreq>\\n    <priority>{pri}</priority>\\n  </url>')""",
             """    # lastmod is only useful if it is real: blog articles carry their
    # publication date, help pages their first-seen date, hubs/legal the build
    # date (those genuinely change on every rebuild).
    blog_dates = {}
    for a in blog_arts:
        d = a.get('date') or a.get('published') or a.get('updated')
        if d:
            blog_dates[a['id']] = str(d)[:10]
    urls = [(SITE + '/', '1.0', BUILD_DATE), (SITE + '/help.html', '0.9', BUILD_DATE)]
    if blog_arts:
        latest_blog = max(blog_dates.values()) if blog_dates else BUILD_DATE
        urls.append((SITE + '/blog/', '0.8', latest_blog))
    urls += [(f'{SITE}/blog/a/{a["id"]}.html', '0.7', blog_dates.get(a['id'], BUILD_DATE))
             for a in blog_arts]
    urls += [(f'{SITE}/help/c/{cid}.html', '0.7', BUILD_DATE) for cid, _, _ in cat_urls]
    urls += [(f'{SITE}/help/a/{n["id"]}.html', '0.8', publish_date('help', n['id']))
             for n in uniq_articles]
    urls += [(SITE + '/legal/privacy.html', '0.4', BUILD_DATE),
             (SITE + '/legal/terms.html', '0.4', BUILD_DATE),
             (SITE + '/legal/refundpolicy.html', '0.4', BUILD_DATE)]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pri, lastmod in urls:
        sm.append(f'  <url>\\n    <loc>{loc}</loc>\\n    <lastmod>{lastmod}</lastmod>\\n'
                  f'    <changefreq>weekly</changefreq>\\n    <priority>{pri}</priority>\\n  </url>')""")
    return n


# --------------------------------------------------------------- build_blog
def patch_blog():
    n = 0
    n += sub("build_blog.py", """def page_head(title, desc, canonical, extra_ld='', og_type='article'):""",
             """def article_meta(pub, mod=None):
    \"\"\"article:* freshness meta (works for crawlers that ignore JSON-LD).\"\"\"
    mod = mod or pub
    return ('<meta property="article:published_time" content="%s">'
            '<meta property="article:modified_time" content="%s">' % (pub, mod))


def page_head(title, desc, canonical, extra_ld='', og_type='article', extra_meta=''):""")
    n += sub("build_blog.py", """<meta name="twitter:image" content="{SITE}/og-cover-v2.png">
<link rel="icon" href="{FAVICON}">""", """<meta name="twitter:image" content="{SITE}/og-cover-v2.png">{extra_meta}
<link rel="icon" href="{FAVICON}">""")
    n += sub("build_blog.py", """        head = page_head(art['title'] + ' — Fast Scheduler Blog', art['description'], canon,
                         extra_ld=ld_post + '\\n' + ld_bread + (faq_ld(art) or ''))""",
             """        head = page_head(art['title'] + ' — Fast Scheduler Blog', art['description'], canon,
                         extra_ld=ld_post + '\\n' + ld_bread + (faq_ld(art) or ''),
                         extra_meta=article_meta(str(art['date'])[:10]))""")
    return n


PATCHES = {"build_help.py": patch_help,
           "build_static.py": patch_static,
           "build_blog.py": patch_blog}

MARKERS = [
    ("build_help.py", '<div class="nav-group nav-left">{brand}{cta}{gear}{left_extra}</div>'),
    ("build_help.py", 'HELP_INDEX_LD'),
    ("build_static.py", 'def publish_date(section, key):'),
    ("build_static.py", "article:published_time"),
    ("build_blog.py", "def article_meta(pub, mod=None):"),
]


def check():
    ok = True
    for path, marker in MARKERS:
        src = open(os.path.join(BUILD, path), encoding="utf-8").read()
        hit = marker in src
        print("  %-16s %-6s %s" % (path, "ok" if hit else "MISSING", marker[:52]))
        ok = ok and hit
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        print("checking %s" % BUILD)
        return check()
    total = 0
    for path, fn in PATCHES.items():
        print("%s:" % path)
        total += fn()
    print("\napplied %d edits" % total)
    for c in CHANGED:
        print("  +", c)
    if total == 0:
        print("(already applied)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
