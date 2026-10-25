# -*- coding: utf-8 -*-
"""Turn stale pretty-URL duplicates (help/a/<id>/index.html) into redirect stubs.

The builders emit one page per article at ``help/a/<id>.html`` and
``blog/a/<id>.html`` and the sitemap lists those. An older build also wrote a
copy at ``help/a/<id>/index.html``; those copies were never regenerated, so they
still serve the previous text (the retired setup flow, unresolved wiki links)
with a self-referencing canonical — duplicate content competing with the page
that is actually maintained.

GitHub Pages cannot send a 301 from a static file, so each stale copy becomes a
redirect stub: canonical to the maintained URL, ``noindex,follow``, and an
immediate meta refresh, which is what search engines treat as a soft redirect
and users never notice.

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

TEMPLATE = (
    '<!DOCTYPE html>\n'
    '<html lang="{lang}"><head><meta charset="utf-8">{marker}\n'
    '<meta name="robots" content="noindex,follow">\n'
    '<link rel="canonical" href="{url}.html">\n'
    '<meta http-equiv="refresh" content="0; url={url}.html">\n'
    '<title>{title}</title></head>\n'
    '<body><p>This page has moved to <a href="{url}.html">{url}.html</a>.</p>'
    '<script>location.replace(\'{url}.html\');</script></body></html>\n'
)


def lang_of(path):
    norm = path.replace(os.sep, '/')
    return 'ru' if ('/ru/' in norm or norm.startswith('ru/')) else 'en'


def main(argv):
    check_only = '--check' in argv
    converted = skipped = 0
    for tree in ('.', 'website'):
        for section in ('help', 'blog'):
            base = os.path.join(tree, section, 'a') if tree != '.' else os.path.join(section, 'a')
            if not os.path.isdir(base):
                continue
            for name in sorted(os.listdir(base)):
                d = os.path.join(base, name)
                page = os.path.join(base, name + '.html')
                copy = os.path.join(d, 'index.html')
                if not (os.path.isdir(d) and os.path.isfile(copy) and os.path.isfile(page)):
                    continue
                with io.open(copy, encoding='utf-8', errors='replace') as f:
                    src = f.read()
                if MARKER in src:
                    skipped += 1
                    continue
                if check_only:
                    converted += 1
                    continue
                with io.open(page, encoding='utf-8', errors='replace') as f:
                    target = f.read()
                title = 'Redirecting'
                start = target.find('<title>')
                if start > -1:
                    end = target.find('</title>', start)
                    title = target[start + 7:end].strip() or title
                url = '%s/%s/a/%s' % (SITE, section, name)
                with io.open(copy, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(TEMPLATE.format(lang=lang_of(copy), marker=MARKER,
                                            url=url, title=title))
                converted += 1
    print('%s %d duplicate page(s), %d already stubs'
          % ('would convert' if check_only else 'converted', converted, skipped))


if __name__ == '__main__':
    main(sys.argv[1:])
