"""Crawl-graph reachability: follow only real <a href> targets from /.

Googlebot cannot discover href="#/a/foo" fragments. This walks the site the
way a crawler does -- real links only, no JS -- and reports which of the
generated pages are reachable at all, and how deep they sit.
"""
import os
import re
import sys
from collections import deque
from urllib.parse import urldefrag, unquote, urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'website')

HREF = re.compile(r'<a\b[^>]*?\bhref="([^"]+)"', re.I | re.S)
# Crawlers discover hreflang partners as well as links. Following them is what
# makes a /ru/ page count as reachable from its English original.
ALT = re.compile(r'<link\b[^>]*\brel="alternate"[^>]*>', re.I | re.S)
ALT_HREF = re.compile(r'\bhref="([^"]+)"', re.I)


def all_pages():
    out = set()
    for dp, dirs, fns in os.walk(SITE):
        dirs[:] = [d for d in dirs if d not in ('_build', 'scripts', 'styles', 'img')]
        for fn in fns:
            if fn.endswith('.html'):
                rel = os.path.relpath(os.path.join(dp, fn), SITE).replace('\\', '/')
                out.add(rel)
    return out


def resolve(base, href):
    """Absolute site-relative path for href, or None if not an in-site link."""
    href, _frag = urldefrag(href.strip())
    if not href:
        return None
    if href.startswith(('http://', 'https://', '//', 'mailto:', 'tel:', 'javascript:')):
        if 'fastscheduler.github.io' in href:
            href = urlsplit(href).path or '/'
        else:
            return None
    if href.startswith('#'):
        return None                      # fragment-only: invisible to crawlers
    if href.startswith('/'):
        return href.lstrip('/')
    base_dir = os.path.dirname(base)
    return os.path.normpath(os.path.join(base_dir, href)).replace('\\', '/')


def links_of(page):
    p = os.path.join(SITE, page)
    if not os.path.isfile(p):
        return []
    s = open(p, encoding='utf-8', errors='replace').read()
    out = []
    for m in HREF.finditer(s):
        r = resolve(page, m.group(1))
        if r:
            out.append(r)
    for tag in ALT.finditer(s):
        h = ALT_HREF.search(tag.group(0))
        if h:
            r = resolve(page, h.group(1))
            if r:
                out.append(r)
    return out


def main():
    pages = all_pages()
    start = 'index.html'
    seen = {start}
    depth = {start: 0}
    q = deque([start])
    frontier_depth = {}
    while q:
        cur = q.popleft()
        for tgt in links_of(cur):
            cand = tgt
            if cand.endswith('/'):
                cand += 'index.html'
            if cand in pages and cand not in seen:
                seen.add(cand)
                depth[cand] = depth[cur] + 1
                q.append(cand)
            elif cand not in seen and not os.path.exists(os.path.join(SITE, cand)):
                frontier_depth.setdefault(cur, []).append(cand)

    unreachable = sorted(pages - seen)
    by_dir = {}
    for p in pages:
        parts = p.split('/')
        key = '/'.join(parts[:2]) if p.startswith('ru/') and len(parts) > 1 else (
            parts[0] if '/' in p else '(root)')
        by_dir.setdefault(key, []).append(p)

    print('generated pages: %d' % len(pages))
    print('reachable from %s via real hrefs: %d' % (start, len(seen)))
    print('UNREACHABLE: %d' % len(unreachable))
    print()
    print('-- reachable per section --')
    for k in sorted(by_dir):
        tot = len(by_dir[k])
        got = sum(1 for p in by_dir[k] if p in seen)
        print('  %-14s %4d / %4d' % (k, got, tot))
    print()
    print('-- unreachable sample (first 25) --')
    for p in unreachable[:25]:
        print('   ', p)
    print()
    print('-- max click depth from home: %d --' % (max(depth.values()) if depth else 0))
    return 0 if not unreachable else 1


if __name__ == '__main__':
    sys.exit(main())