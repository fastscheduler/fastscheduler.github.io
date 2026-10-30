# -*- coding: utf-8 -*-
"""Turn stale ``<page>/index.html`` duplicates into redirect stubs.

The builders emit one maintained page per URL as ``<path>.html`` (the sitemap
lists exactly those). An older clean-URL build also wrote a second copy at
``<path>/index.html`` — the hub at ``help/index.html``, every category at
``help/c/<id>/index.html``, every legal document at ``legal/<doc>/index.html``,
and the Russian equivalents. Those copies are never regenerated, so they keep
serving the previous markup, old hotkey hints and unresolved links, with a
canonical that points at themselves. That is duplicate content competing with
the page that is actually maintained — and it is why a fix can look like it
"came back" when a search result or old bookmark lands on the directory URL.

GitHub Pages cannot send a 301 from a static file, so each stale copy becomes a
redirect stub: canonical to the maintained URL, ``noindex,follow``, and an
immediate meta refresh, which search engines treat as a soft redirect and
users never notice. Query string and hash are carried over, so
``/help/#/a/admins`` still opens that article on ``/help.html``.

Idempotent: a page already carrying the redirect marker is skipped.

    python tools/stub_duplicate_pages.py            # apply
    python tools/stub_duplicate_pages.py --check    # report only
"""

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = 'https://fastscheduler.github.io'
MARKER = '<!--fs-redirect-->'
SKIP_DIRS = {'.git', 'freebuff-sites-build', '_hero_phone_backup', 'node_modules',
             '__pycache__', '_build', '.kilo', 'backup', 'tools', '_shots',
             'website'}

TEMPLATE = (
    '<!DOCTYPE html>\n'
    '<html lang="{lang}"><head><meta charset="utf-8">{marker}\n'
    '<meta name="robots" content="noindex,follow">\n'
    '<link rel="canonical" href="{url}">\n'
    '<meta http-equiv="refresh" content="0; url={rel}">\n'
    '<title>{title}</title></head>\n'
    '<body><p>This page has moved to <a href="{rel}">{url}</a>.</p>'
    "<script>location.replace('{rel}' + location.search + location.hash);"
    '</script></body></html>\n'
)


def trees():
    """The deploy tree and the source tree, each with the root it maps to."""
    yield ROOT, ROOT
    site = os.path.join(ROOT, 'website')
    if os.path.isdir(site):
        yield site, site


def pairs():
    """Yield (index_path, target_html_path, tree_root) for stale duplicates."""
    for tree, base in trees():
        for dirpath, dirnames, filenames in os.walk(tree):
            top = dirpath == tree
            dirnames[:] = [d for d in dirnames
                           if not d.startswith('.')
                           and d not in ('node_modules', '__pycache__')
                           and not (top and d in SKIP_DIRS)]
            if 'index.html' not in filenames:
                continue
            sibling = dirpath + '.html'
            if os.path.isfile(sibling):
                yield os.path.join(dirpath, 'index.html'), sibling, base


def main(argv):
    check_only = '--check' in argv
    converted = skipped = 0
    for index, target, base in pairs():
        with io.open(index, encoding='utf-8', errors='replace') as fh:
            src = fh.read()
        url = SITE + '/' + os.path.relpath(target, base).replace(os.sep, '/')
        # Relative redirect target: works on the published domain, on a
        # staging copy and on localhost, and keeps the hash route intact.
        rel = os.path.relpath(target, os.path.dirname(index)).replace(os.sep, '/')
        # An existing stub is only finished if it points at the right page:
        # a stub that redirects to the wrong URL is rewritten, not skipped.
        if MARKER in src and ('href="%s"' % rel) in src:
            skipped += 1
            continue
        if check_only:
            converted += 1
            print('[duplicate]', os.path.relpath(index, ROOT))
            continue
        title = ''
        i = src.find('<title>')
        if i != -1:
            j = src.find('</title>', i)
            if j != -1:
                title = src[i + 7:j].strip()
        norm = index.replace(os.sep, '/')
        lang = 'ru' if '/ru/' in norm else 'en'
        with io.open(index, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(TEMPLATE.format(lang=lang, marker=MARKER, url=url,
                                     rel=rel, title=title))
        converted += 1
    print('stubbed: %d  already stubbed: %d' % (converted, skipped))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
