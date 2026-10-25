"""Rewrite root-absolute /scripts/ (and friends) references to relative paths.

592 pages -- every help article, every RU help article and the RU legal pages --
referenced the translation runtime as:

    <script src="/scripts/ru-chrome.js?...">
    <script src="/scripts/lang.js?...">

A leading slash is resolved against the ORIGIN, not the site directory. The site
is published from a repository subdirectory, so the live origin is
https://fastscheduler.github.io and "/scripts/lang.js" requests

    https://fastscheduler.github.io/scripts/lang.js   -> 404

while the file actually lives at

    https://fastscheduler.github.io/scripts/lang.js -> 200

Every other asset on those pages (theme.js, settings.js, help-search.js,
hotkeys.js, ...) already used a correct relative path, which is why the pages
looked fine: only the two translation scripts silently failed. That is why
switching language appeared to do nothing at all on help pages, and why Russian
coverage was so poor there - neither the 392-entry MAP dictionary nor the
content dictionary was ever loaded.

The fix is to make the two refs relative like their neighbours. Depth is taken
from each file's own location so no page can end up pointing at the wrong
directory.

Idempotent: re-running is a no-op. Use --check to verify without writing.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, 'website')

# Only directories that genuinely live at the site root are rewritten.
DIRS = ('scripts', 'styles', 'fonts', 'assets', 'blog', 'help', 'legal', 'ru')

ABS_RE = re.compile(
    r'\b(src|href)="/(' + '|'.join(DIRS) + r')/([^"?#]*)(\?[^"#]*)?(#[^"]*)?"')


def depth_prefix(rel_path):
    """'help/a/admins.html' -> '../../'  ;  'index.html' -> ''"""
    return '../' * rel_path.count('/')


def fix(h, rel_path):
    pre = depth_prefix(rel_path)

    def sub(m):
        attr, d, rest, q, frag = m.groups()
        return '%s="%s%s/%s%s%s"' % (attr, pre, d, rest, q or '', frag or '')

    return ABS_RE.sub(sub, h)


def main():
    check = '--check' in sys.argv
    changed = 0
    rewritten = 0
    for dirpath, _dirs, files in os.walk(WEB):
        if '_build' in dirpath.split(os.sep):
            continue
        for f in files:
            if not f.endswith('.html'):
                continue
            p = os.path.join(dirpath, f)
            rel = os.path.relpath(p, WEB).replace('\\', '/')
            with open(p, encoding='utf-8') as fh:
                orig = fh.read()
            if not ABS_RE.search(orig):
                continue
            new = fix(orig, rel)
            if new == orig:
                continue
            n = len(ABS_RE.findall(orig))
            changed += 1
            rewritten += n
            if check:
                print('WOULD CHANGE %s (%d refs)' % (rel, n))
            else:
                with open(p, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(new)
    print('files changed  : %d' % changed)
    print('refs rewritten : %d' % rewritten)
    return 1 if (check and changed) else 0


if __name__ == '__main__':
    sys.exit(main())