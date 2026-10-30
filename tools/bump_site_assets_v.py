#!/usr/bin/env python
"""Bump the ?v= cache stamp on styles/*.css and scripts/*.js references.

The published tree (repo root, served at
https://fastscheduler.github.io/) caches CSS and JS by URL.
Editing styles/main.css or scripts/*.js without bumping the stamp means
returning visitors keep the old copy from their disk cache and the fix looks
like it never shipped.

    python tools/bump_site_assets_v.py 20261014a1
    python tools/bump_site_assets_v.py --check
"""
import io, os, re, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = ('.git', 'node_modules', 'venv', '.venv', '__pycache__', '_build', 'tools', 'src',
        'tests', 'website', '.kilo', 'backup', 'local', 'data', 'docs', 'SetDate',
        'Support Bot', '_hero_phone_backup', '.scripts', 'alwaysdata')
PAT = re.compile(r'((?:\.\./)*styles/[A-Za-z0-9_\-]+\.css|(?:\.\./)*scripts/[A-Za-z0-9_\-]+\.js)\?v=([^"\'&]+)')


def _write(path, text, attempts=6):
    """Write a page, retrying transient Windows sharing violations.

    Antivirus/indexers briefly hold a handle right after a file is rewritten;
    Windows answers the next open with EINVAL ("Invalid argument"), which used
    to abort the whole bump half way through the tree. Retrying settles it.
    """
    for i in range(attempts):
        try:
            io.open(path, 'w', encoding='utf-8', newline='\n').write(text)
            return
        except OSError:
            if i == attempts - 1:
                raise
            time.sleep(0.15 * (i + 1))


def main():
    args = sys.argv[1:]
    check_only = '--check' in args
    new = next((a for a in args if not a.startswith('--')), None)
    if not new and not check_only:
        raise SystemExit(__doc__)
    stamps, touched, files = {}, 0, 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP and not d.startswith('.')]
        for name in filenames:
            if not name.endswith('.html'):
                continue
            full = os.path.join(dirpath, name)
            s = io.open(full, encoding='utf-8', errors='replace').read()
            if not PAT.search(s):
                continue
            for m in PAT.finditer(s):
                stamps[m.group(2)] = stamps.get(m.group(2), 0) + 1
            if check_only:
                continue
            out = PAT.sub(lambda m: m.group(1) + '?v=' + new, s)
            if out != s:
                _write(full, out)
                touched += 1
            files += 1
    print(('checked' if check_only else 'bumped to %s in' % new), files, 'page(s),', touched, 'rewritten')
    for v, n in sorted(stamps.items(), key=lambda kv: -kv[1])[:12]:
        print('   %-14s %d refs' % (v, n))


if __name__ == '__main__':
    main()
