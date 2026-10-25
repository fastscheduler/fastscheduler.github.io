#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build server-rendered Russian blog: website/ru/blog/ (hub + articles).

Mirrors the EN blog tree one level deeper under /ru/ so every relative link
keeps working by symmetry:
  blog/index.html  ->  ru/blog/index.html   (../index.html == ru home)
  blog/a/x.html    ->  ru/blog/a/x.html     (../../help.html == ru help)

Text nodes are translated through the same MAP as the other RU hubs
(ru-chrome.js + lang.js inline core); article bodies keep the client-side
sentence dictionary (ru-content.js) exactly like EN->RU switching does.
Idempotent: outputs are fully regenerated each run.
"""

import io
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT + os.sep + 'tools')
sys.path.insert(0, ROOT)

from build_ru_pages import load_map, transform, set_head  # noqa: E402
from build_ru_pages2 import inject_alts  # noqa: E402

SITE = os.path.join(ROOT, 'website')
BASE = 'https://fastscheduler.github.io'
SRC = os.path.join(SITE, 'blog')
DST = os.path.join(SITE, 'ru', 'blog')

_BLOG_ASSET_RE = re.compile(
    r'((?:src|href)=")(\.\./(?:\.\./)?)'
    r'(scripts/|styles/|fonts/|brand-logo\.png|brand-logo-128\.png|'
    r'brand-logo-64\.png|icon-96\.png|icon-48\.png|favicon-32\.png|'
    r'favicon-16\.png|apple-touch-icon\.png|og-cover-v2\.png)')


def fix_blog_assets(html):
    """One extra ../ for asset URLs (page links keep working by symmetry)."""
    return _BLOG_ASSET_RE.sub(lambda m: m.group(1) + '../' + m.group(2) + m.group(3), html)


HUB_TITLE = 'Блог — Заметки о росте Telegram-каналов'
HUB_DESC = ('Заметки о росте Telegram-каналов для владельцев каналов: '
            'гайды в разделе «Статьи», запуски в «Новостях».')
ART_TITLE_SUFFIX = ' — Блог Fast Scheduler'


def _ru_head_hub(html):
    return set_head(html, HUB_TITLE, HUB_DESC,
                    BASE + '/ru/blog/', BASE + '/blog/')


def _ru_head_article(html, slug):
    m = re.search(r'<title>(.*?)</title>', html, flags=re.S)
    en_title = (m.group(1).strip() if m else slug)
    # Keep the EN title readable: RU suffix marks the language, the client
    # dictionary swaps the title itself when it knows the RU form.
    title = en_title + ART_TITLE_SUFFIX if 'Блог' not in en_title else en_title
    m2 = re.search(r'<meta name="description" content="([^"]*)"', html)
    desc = m2.group(1) if m2 else HUB_DESC
    return set_head(html, title, desc,
                    BASE + '/ru/blog/a/%s.html' % slug,
                    BASE + '/blog/a/%s.html' % slug)


def _rewrite_urls(html):
    # Canonical / OG absolute URLs point at the EN tree; mirror them to /ru/.
    html = html.replace('Fast-Scheduler/blog/', 'Fast-Scheduler/ru/blog/')
    html = html.replace('Fast-Scheduler/ru/ru/blog/', 'Fast-Scheduler/ru/blog/')
    return html


def build_hub(MAP):
    src = io.open(os.path.join(SRC, 'index.html'), encoding='utf-8').read()
    html, unmapped = transform(src, MAP)
    html = _rewrite_urls(html)
    html = fix_blog_assets(html)
    html = _ru_head_hub(html)
    os.makedirs(DST, exist_ok=True)
    out = os.path.join(DST, 'index.html')
    io.open(out, 'w', encoding='utf-8', newline='\n').write(html)
    inject_alts(os.path.join(SRC, 'index.html'),
                BASE + '/ru/blog/', BASE + '/blog/')
    return out, unmapped


def build_articles(MAP):
    src_dir = os.path.join(SRC, 'a')
    dst_dir = os.path.join(DST, 'a')
    os.makedirs(dst_dir, exist_ok=True)
    slugs = sorted(f[:-5] for f in os.listdir(src_dir) if f.endswith('.html'))
    all_unmapped = {}
    for slug in slugs:
        src = io.open(os.path.join(src_dir, slug + '.html'), encoding='utf-8').read()
        html, unmapped = transform(src, MAP)
        html = _rewrite_urls(html)
        html = fix_blog_assets(html)
        html = _ru_head_article(html, slug)
        io.open(os.path.join(dst_dir, slug + '.html'),
                'w', encoding='utf-8', newline='\n').write(html)
        inject_alts(os.path.join(src_dir, slug + '.html'),
                    BASE + '/ru/blog/a/%s.html' % slug,
                    BASE + '/blog/a/%s.html' % slug)
        for k, c in unmapped.items():
            all_unmapped[k] = all_unmapped.get(k, 0) + c
    # Drop stale RU articles removed from EN.
    keep = set(s + '.html' for s in slugs)
    for f in os.listdir(dst_dir):
        if f.endswith('.html') and f not in keep:
            os.remove(os.path.join(dst_dir, f))
    return len(slugs), all_unmapped


def copy_assets():
    # Cover images + hub JS are language-neutral; copy verbatim.
    for name in ('img',):
        s, d = os.path.join(SRC, name), os.path.join(DST, name)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
    for name in ('blog-search.js',):
        s, d = os.path.join(SRC, name), os.path.join(DST, name)
        if os.path.isfile(s):
            shutil.copyfile(s, d)


def update_sitemap(urls):
    try:
        sm_path = os.path.join(SITE, 'sitemap.xml')
        sm = io.open(sm_path, encoding='utf-8').read()
        sm = re.sub(r'\s*<url>\s*<loc>[^<]*/ru/blog/[^<]*</loc>.*?</url>', '',
                    sm, flags=re.S)
        add = ''.join('  <url>\n    <loc>%s</loc>\n'
                      '    <changefreq>monthly</changefreq>\n'
                      '    <priority>0.6</priority>\n  </url>\n' % u for u in urls)
        sm = sm.replace('</urlset>', add + '</urlset>')
        io.open(sm_path, 'w', encoding='utf-8', newline='\n').write(sm)
        print('sitemap /ru/blog URLs: %d' % len(urls))
    except Exception as e:
        print('sitemap skipped (%s)' % e)


def main():
    MAP = load_map()
    print('MAP keys: %d' % len(MAP))
    hub_out, hub_un = build_hub(MAP)
    print('wrote %s (%d unmapped)' % (hub_out, len(hub_un)))
    n, art_un = build_articles(MAP)
    print('wrote %d RU blog articles (%d unmapped)' % (n, len(art_un)))
    copy_assets()
    print('copied blog img + search assets')
    urls = ([BASE + '/ru/blog/'] +
            [BASE + '/ru/blog/a/%s.html' % f[:-5]
             for f in sorted(os.listdir(os.path.join(DST, 'a')))
             if f.endswith('.html')])
    update_sitemap(urls)
    top = sorted(set(list(hub_un) + list(art_un)))[:30]
    if top:
        print('sample unmapped:')
        for k in top:
            print('  [?] %s' % k[:120])
    return 0


if __name__ == '__main__':
    sys.exit(main())
