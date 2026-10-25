"""End-to-end integrity check for the published tree.

Verifies the things a static-site build can silently get wrong: sitemap URLs
that 404, hreflang clusters pointing at missing pages, orphan /ru/ files,
unresolved template markers, and unbalanced script tags. Exits non-zero on
any failure so it can gate a deploy.
"""
from __future__ import annotations

import io
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'website')
PREFIX = 'https://fastscheduler.github.io/'
NS = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
MARKER = re.compile(r'@@[A-Z_]+@@|\{[a-z_]+\}')
SCRIPT = re.compile(r'<script\b')
ALT = re.compile(r'<link\b[^>]*\brel="alternate"[^>]*>', re.I | re.S)
ALT_HREF = re.compile(r'\bhref="([^"]+)"', re.I)


def normalise(rel):
    """Sitemap/scan path -> the file key pages() produces."""
    if rel.endswith('/'):
        rel += 'index.html'
    return rel or 'index.html'


def visible(s):
    """Page text with <script>/<style> removed.

    Needed because a JSON-LD SearchAction legitimately carries
    "{search_term_string}" in its URL template -- that is required syntax,
    not an unresolved build placeholder.
    """
    s = re.sub(r'<script\b.*?</script>', ' ', s, flags=re.I | re.S)
    s = re.sub(r'<style\b.*?</style>', ' ', s, flags=re.I | re.S)
    return re.sub(r'<!--.*?-->', ' ', s, flags=re.S)


def pages():
    out = set()
    for base, dirs, files in os.walk(SITE):
        dirs[:] = [d for d in dirs if d not in
                   ('_build', 'styles', 'scripts', 'fonts', 'img', 'images', '.git')]
        for f in files:
            if f.endswith('.html'):
                out.add(os.path.relpath(os.path.join(base, f), SITE).replace(os.sep, '/'))
    return out


def main():
    allp = pages()
    fails = []

    # 1. every sitemap URL exists, in website/ AND in the deploy root
    tree = ET.parse(os.path.join(SITE, 'sitemap.xml'))
    locs = [e.text for e in tree.getroot().findall('s:url/s:loc', NS)]
    dupe = len(locs) - len(set(locs))
    if dupe:
        fails.append('%d duplicate sitemap URLs' % dupe)
    missing_site = missing_root = 0
    for u in locs:
        rel = u[len(PREFIX):] if u.startswith(PREFIX) else None
        if rel is None:
            fails.append('sitemap URL off-prefix: %s' % u)
            continue
        rel = normalise(rel)
        if rel not in allp:
            missing_site += 1
        if not os.path.exists(os.path.join(ROOT, rel)):
            missing_root += 1
    if missing_site:
        fails.append('%d sitemap URLs missing from website/' % missing_site)
    if missing_root:
        fails.append('%d sitemap URLs missing from the deploy root' % missing_root)

    # 2. pages reachable but not in the sitemap
    unsitemapped = sorted(allp - set(
        normalise(u[len(PREFIX):] if u.startswith(PREFIX) else u) for u in locs))
    noindex_ok = [p for p in unsitemapped if 'legal/history' in p or p == '404.html']
    other = [p for p in unsitemapped if p not in noindex_ok]

    # 3. hreflang targets must exist
    broken_alt = 0
    for p in allp:
        s = io.open(os.path.join(SITE, p), encoding='utf-8', errors='replace').read()
        for tag in ALT.finditer(s.split('</head>')[0]):
            h = ALT_HREF.search(tag.group(0))
            if not h:
                continue
            u = h.group(1)
            if not u.startswith(PREFIX):
                continue
            rel = u[len(PREFIX):]
            if rel not in allp:
                broken_alt += 1
    if broken_alt:
        fails.append('%d hreflang alternates point at missing pages' % broken_alt)

    # 4. unresolved markers and unbalanced script tags
    markers = scripts_bad = 0
    for p in allp:
        s = io.open(os.path.join(SITE, p), encoding='utf-8', errors='replace').read()
        if MARKER.search(visible(s)):
            markers += 1
        if len(SCRIPT.findall(s)) != s.count('</script>'):
            scripts_bad += 1
    if markers:
        fails.append('%d pages contain unresolved template markers' % markers)
    if scripts_bad:
        fails.append('%d pages have unbalanced <script> tags' % scripts_bad)

    # 5. every /ru/ page declares Russian and is in the sitemap
    ru = [p for p in allp if p.startswith('ru/')]
    bad_lang = [p for p in ru
                if not re.search(r'<html[^>]*\blang="ru"', io.open(
                    os.path.join(SITE, p), encoding='utf-8', errors='replace').read())]
    if bad_lang:
        fails.append('%d /ru/ pages are not lang="ru": %s' % (len(bad_lang), bad_lang[:3]))

    print('pages: %d  (ru: %d)' % (len(allp), len(ru)))
    print('sitemap URLs: %d  duplicates: %d' % (len(locs), dupe))
    print('not in sitemap (expected 404.html + legal/history): %s'
          % ', '.join(sorted(p.split('/')[-1] for p in noindex_ok)))
    if other:
        print('NOT in sitemap, unexpected: %s' % ', '.join(other[:10]))
        fails.append('%d pages missing from the sitemap: %s' % (len(other), other[:5]))
    print('hreflang alternates resolved: %s' % ('yes' if not broken_alt else 'NO'))
    print('unresolved markers: %d | unbalanced scripts: %d | bad /ru/ lang: %d'
          % (markers, scripts_bad, len(bad_lang)))
    if fails:
        print('\nFAIL:')
        for f in fails:
            print('  - %s' % f)
        return 1
    print('\nOK')
    return 0


if __name__ == '__main__':
    sys.exit(main())