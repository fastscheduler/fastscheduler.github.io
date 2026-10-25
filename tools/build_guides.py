# -*- coding: utf-8 -*-
"""Render the long-form guides in ``_build/guides_content.py``.

The guides are written by hand but must look and behave exactly like the
generated Help Center pages, so this reuses ``build_static``'s page shell,
head builder, FAQ renderer and icons. It only writes the pages it owns and
patches the surrounding indexes (category lists, home counts, sitemap,
llms-full corpus, hub search extras) idempotently.

    python tools/build_guides.py

Run from the repo root. Safe to re-run.
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
BUILD = os.path.join(REPO, '_build')
for p in (BUILD, REPO, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import build_static as bs          # noqa: E402  (imports build_help as bh)
from guides_content import GUIDES  # noqa: E402

bh = bs.bh
SITE = bs.SITE
DATE = bs.BUILD_DATE

CAT_TITLES = {
    'start': 'Getting Started',
    'scheduling': 'Scheduling Messages',
    'import': 'Import',
}

GUIDE_IDS = [g['id'] for g in GUIDES]

# Every page id that already exists on disk, plus the new ones: used to decide
# whether a related-topic link points at an article or a category hub.
ARTICLE_IDS = set(GUIDE_IDS)
for name in os.listdir(os.path.join(REPO, 'help', 'a')):
    if name.endswith('.html'):
        ARTICLE_IDS.add(name[:-5])

TITLES = {}
for g in GUIDES:
    TITLES[g['id']] = g['title']
try:
    with io.open(os.path.join(REPO, 'translations', 'en.json'), encoding='utf-8-sig') as f:
        _help = json.load(f).get('help', {})
    for k, v in _help.items():
        if isinstance(v, dict) and v.get('title'):
            TITLES.setdefault(k, v['title'])
except Exception:
    pass
for mod_name in ('seo_articles', 'seo_articles_b'):
    try:
        mod = __import__(mod_name)
        seq = getattr(mod, 'SEO_ARTICLES', None) or getattr(mod, 'ARTICLES_B', [])
        for a in seq:
            if a.get('id') and a.get('title'):
                TITLES.setdefault(a['id'], a['title'])
    except Exception:
        pass


def label(lid):
    return TITLES.get(lid) or lid.replace('_', ' ').title()


def href(lid):
    if lid in ARTICLE_IDS:
        return lid + '.html'
    if lid in CAT_TITLES:
        return '../c/' + lid + '.html'
    if os.path.exists(os.path.join(REPO, 'help', 'c', lid + '.html')):
        return '../c/' + lid + '.html'
    return '../../help.html'


EXTRA_CSS = ('<style>'
             '.hc-body pre{background:var(--surface);border:1px solid var(--border);'
             'border-radius:12px;padding:14px 16px;overflow-x:auto;margin:0 0 18px;'
             'font-size:.86rem;line-height:1.55}'
             '.hc-body pre code{word-break:normal;white-space:pre}'
             '.hc-body ol{margin:0 0 18px;padding-left:22px}'
             '.hc-body ol li{margin:0 0 8px}'
             '</style>')


def howto(n):
    steps = n.get('howto')
    if not steps:
        return ''
    return bs.jsonld({
        '@context': 'https://schema.org', '@type': 'HowTo',
        'name': n['title'], 'description': n['description'],
        'totalTime': 'PT5M',
        'step': [{'@type': 'HowToStep', 'name': s[0], 'text': s[1]} for s in steps],
    })


def render(n, prev_n, next_n):
    aid = n['id']
    cat = n['category']
    cat_title = CAT_TITLES.get(cat, 'Help')
    desc = n['description']
    canonical = f'{SITE}/help/a/{aid}.html'

    faq = [{'q': f['q'], 'a': f['a'], 'links': [l for l in (f.get('links') or []) if l in ARTICLE_IDS]}
           for f in n.get('faq', [])]
    faq_html = bh.render_faq(faq, href, label)

    related, seen = [], set()
    for f in faq:
        for lid in f['links']:
            if lid in seen or lid == aid:
                continue
            seen.add(lid)
            related.append('<a class="hc-chip" href="%s"><span>%s</span>%s</a>'
                           % (href(lid), bh.esc(label(lid)), bh.svg('arrow-r')))
    related_html = ('<div class="hc-related"><h2>Related topics</h2><div class="hc-chips">%s</div></div>'
                    % ''.join(related)) if related else ''

    pager = ['<nav class="hc-pager" aria-label="More articles">']
    if prev_n:
        pager.append('<a class="hc-card prev" href="%s.html">%s<span><small>Previous</small><b>%s</b></span></a>'
                     % (prev_n['id'], bh.svg('arrow-l'), bh.esc(prev_n['title'])))
    else:
        pager.append('<a class="hc-card prev" href="../c/%s.html">%s<span><small>Topic</small><b>%s</b></span></a>'
                     % (cat, bh.svg('arrow-l'), bh.esc(cat_title)))
    if next_n:
        pager.append('<a class="hc-card next" href="%s.html"><span><small>Next</small><b>%s</b></span>%s</a>'
                     % (next_n['id'], bh.esc(next_n['title']), bh.svg('arrow-r')))
    else:
        pager.append('<a class="hc-card next" href="../../help.html"><span><small>All topics</small>'
                     '<b>Help Center</b></span>%s</a>' % bh.svg('arrow-r'))
    pager.append('</nav>')

    crumbs = ('<nav class="hc-crumbs" aria-label="Breadcrumb">'
              '<a href="../../help.html">Help Center</a>%s'
              '<a href="../c/%s.html">%s</a>%s'
              '<span aria-current="page">%s</span></nav>'
              % (bh.svg('chev'), cat, bh.esc(cat_title), bh.svg('chev'), bh.esc(n['title'])))

    cta = ('<div class="hc-cta"><div><b>Still stuck?</b>'
           '<p>The in-bot assistant answers the same questions &mdash; and a human reads every ticket.</p></div>'
           '<a class="btn" href="%s" target="_blank" rel="noopener noreferrer">%s Ask in Telegram</a></div>'
           % (bh.SUPPORT_URL, bh.svg('send')))

    body = ('<div class="wrap legal-layout" style="display:block;max-width:860px;margin:0 auto">'
            '%s<article class="doc"><h1>%s</h1><div class="hc-body">%s%s</div>%s%s</article>%s%s</div>'
            % (crumbs, bh.esc(n['title']), EXTRA_CSS, n['content'], faq_html, related_html,
               ''.join(pager), cta))

    ld_tech = bs.jsonld({
        '@context': 'https://schema.org', '@type': 'TechArticle',
        'headline': n['title'], 'description': desc,
        'articleBody': bs.strip_html(n['content']),
        'articleSection': cat_title,
        'author': {'@type': 'Organization', 'name': 'Fast Scheduler', 'url': SITE},
        'publisher': {'@type': 'Organization', 'name': 'Fast Scheduler', 'url': SITE,
                      'logo': {'@type': 'ImageObject', 'url': SITE + '/og-cover-v2.png'}},
        'mainEntityOfPage': canonical,
        'datePublished': DATE, 'dateModified': DATE,
        'isPartOf': {'@type': 'WebSite', 'name': 'Fast Scheduler Help', 'url': SITE + '/help.html'},
    })
    ld_bread = bs.breadcrumb_ld([
        ('Fast Scheduler', SITE + '/'),
        ('Help Center', SITE + '/help.html'),
        (cat_title, f'{SITE}/help/c/{cat}.html'),
        (n['title'], canonical),
    ])
    ld_faq = bh.article_faq_ld({'faq': faq})
    head = bs.page_head(n['title'] + ' — Fast Scheduler Help', desc, canonical,
                        extra_ld='\n'.join(x for x in (ld_tech, ld_bread, ld_faq, howto(n)) if x))
    html = bs.page_shell(head, body)
    # Every other article page carries the shared footer and the global
    # Ctrl/Cmd+K search; the bare shell does not, so add them here.
    if 'site-search.js' not in html:
        extra = ('<script src="../../scripts/site-footer.js?v=20261018g2"></script>\n'
                 '<script src="../../scripts/site-search.js?v=20261018f1"></script>\n')
        html = html.replace('</body>', extra + '</body>')
    return html


def write_both(rel, text):
    for base in (REPO, os.path.join(REPO, 'website')):
        path = os.path.join(base, rel)
        if not os.path.isdir(os.path.dirname(path)):
            continue
        io.open(path, 'w', encoding='utf-8', newline='\n').write(text)


def patch_category(cat, items):
    """Add missing guide links to a category page; return how many were new."""
    rel = os.path.join('help', 'c', cat + '.html')
    path = os.path.join(REPO, rel)
    if not os.path.exists(path):
        return 0
    s = io.open(path, encoding='utf-8').read()
    added = 0
    for aid, title in items:
        if f'../a/{aid}.html' in s:
            continue
        li = f'<li><a href="../a/{aid}.html">{bh.esc(title)}</a></li>'
        idx = s.find('</ul>')
        if idx == -1:
            continue
        s = s[:idx] + li + s[idx:]
        added += 1
    if added:
        m = re.search(r'<p>(\d+) guides? in this topic\.</p>', s)
        if m:
            s = s[:m.start()] + f'<p>{int(m.group(1)) + added} guides in this topic.</p>' + s[m.end():]
        write_both(rel, s)
    return added


def patch_home_counts(counts):
    """Sync the help hub card counters with each category page's own count.

    Reading the category page (rather than adding a delta) keeps this
    idempotent: the counter can drift into a wrong value only if the source
    of truth is wrong too.
    """
    del counts
    rel = 'help.html'
    path = os.path.join(REPO, rel)
    if not os.path.exists(path):
        return
    s = io.open(path, encoding='utf-8').read()
    orig = s
    for cat in CAT_TITLES:
        cpath = os.path.join(REPO, 'help', 'c', cat + '.html')
        if not os.path.exists(cpath):
            continue
        cs = io.open(cpath, encoding='utf-8').read()
        cm = re.search(r'<p>(\d+) guides? in this topic\.</p>', cs)
        if not cm:
            continue
        n = cm.group(1)
        card = ('(<a class="hc-cat hc-card" href="#/c/' + re.escape(cat) + '">.*?)'
                r'(<span class="hc-cat-c">)\d+( articles?</span>)')
        s = re.sub(card, lambda m: m.group(1) + m.group(2) + n + m.group(3), s, count=1, flags=re.S)
    if s != orig:
        write_both(rel, s)


def patch_sitemap():
    rel = 'sitemap.xml'
    path = os.path.join(REPO, rel)
    if not os.path.exists(path):
        return
    s = io.open(path, encoding='utf-8').read()
    add = []
    for g in GUIDES:
        loc = f'{SITE}/help/a/{g["id"]}.html'
        if loc in s:
            continue
        add.append(f'  <url>\n    <loc>{loc}</loc>\n    <lastmod>{DATE}</lastmod>\n'
                   f'    <changefreq>monthly</changefreq>\n    <priority>0.85</priority>\n  </url>')
    if add:
        s = s.replace('</urlset>', '\n'.join(add) + '\n</urlset>')
        write_both(rel, s)


def patch_llms_full():
    rel = 'llms-full.txt'
    path = os.path.join(REPO, rel)
    if not os.path.exists(path):
        return
    s = io.open(path, encoding='utf-8').read()
    marker = '# Start here — complete guides'
    if marker in s:
        return
    out = ['', marker,
           'These five guides are the fastest way for a model or a person to learn the bot: the',
           'menu map, the exact schedule syntax, media modes, duplicate handling and file batches.',
           '']
    for g in GUIDES:
        out += [f'## {g["title"]}',
                f'URL: {SITE}/help/a/{g["id"]}.html',
                '',
                bs.strip_html(g['content'])]
        for f in g.get('faq', []):
            out += ['', f'Q: {bs.strip_html(f["q"])}', f'A: {bs.strip_html(f["a"])}']
        out.append('')
    io.open(path, 'a', encoding='utf-8', newline='\n').write('\n' + '\n'.join(out))
    alt = os.path.join(REPO, 'website', rel)
    if os.path.exists(alt):
        s2 = io.open(alt, encoding='utf-8').read()
        if marker not in s2:
            io.open(alt, 'a', encoding='utf-8', newline='\n').write('\n' + '\n'.join(out))


def write_extras():
    docs = []
    for g in GUIDES:
        faq = ' '.join(bs.strip_html(f['q']) + ' ' + bs.strip_html(f['a']) for f in g.get('faq', []))
        docs.append({'id': g['id'], 'c': g['category'], 't': g['title'],
                     'b': bs.strip_html(g['content']), 'f': faq,
                     'd': g['description'],
                     'href': 'help/a/' + g['id'] + '.html'})
    js = ('/* New long-form guides — appended to the Help Center search index.\n'
          '   Generated by tools/build_guides.py; edit _build/guides_content.py instead. */\n'
          'window.__HELP_EXTRA=' + json.dumps(docs, ensure_ascii=False) + ';\n')
    write_both(os.path.join('scripts', 'help-extra.js'), js)


def main():
    counts = {}
    for i, g in enumerate(GUIDES):
        prev_n = GUIDES[i - 1] if i else None
        next_n = GUIDES[i + 1] if i + 1 < len(GUIDES) else None
        html = render(g, prev_n, next_n)
        write_both(os.path.join('help', 'a', g['id'] + '.html'), html)

    for cat in CAT_TITLES:
        items = [(g['id'], g['title']) for g in GUIDES if g['category'] == cat]
        counts[cat] = patch_category(cat, items)
    patch_home_counts(counts)
    patch_sitemap()
    patch_llms_full()
    write_extras()
    print('[ok] guides:', len(GUIDES), '| category additions:', counts)


if __name__ == '__main__':
    main()
