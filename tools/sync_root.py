"""Sync the repo-root deploy tree (what GitHub Pages serves) from website/.

Copies every differing + website-only file for the published paths.
Keeps root-only files (dev .py in scripts/, etc.). Removes the stale
pruned article root/help/a/channel_default.html.
"""
import os
import shutil
import sys
import time

PUB = ['index.html', 'help.html', '404.html', 'robots.txt', 'sitemap.xml',
       'llms.txt', 'llms-full.txt', 'blog', 'help', 'legal', 'ru', 'scripts',
       'styles', 'fonts', 'apple-touch-icon.png', 'og-cover-v2.png',
       # Brand favicons. Every page links these by relative path; if they are
       # not published here the links 404 in production and the browser falls
       # back to its default globe.
       'brand-logo.png', 'brand-logo-128.png', 'brand-logo-64.png',
       'icon-96.png', 'icon-48.png', 'favicon-32.png', 'favicon-16.png',
       'favicon.ico', 'favicon.svg', 'site.webmanifest',
       'icon-192.png', 'icon-512.png',
       'storage_state.json', '_headers', 'google7ebfb86d3a3c2fa9.html',
       # IndexNow ownership key. Must be served from the site root or every
       # submission is rejected with 422 key_not_found. See tools/indexnow.py.
       '5817133906fc4ab78b0f19ca52bf8f58.txt']
SKIP_DIRS = {'_build', '__pycache__'}
PRUNE = [os.path.join('help', 'a', 'channel_default.html')]

copied = removed = 0


def _write_bytes(path, data, attempts=6):
    """Write a file, retrying transient Windows sharing violations.

    Antivirus/indexers briefly hold a handle on a file just after it changes;
    Windows answers the next open with EINVAL ("Invalid argument"), which used
    to abort the whole sync part way through. A short backoff settles it and a
    real permission problem still raises after the last attempt.
    """
    for i in range(attempts):
        try:
            with open(path, 'wb') as f:
                f.write(data)
            return
        except OSError:
            if i == attempts - 1:
                raise
            time.sleep(0.15 * (i + 1))


def sync_file(src, dst):
    global copied
    with open(src, 'rb') as f:
        data = f.read()
    if os.path.isfile(dst):
        try:
            with open(dst, 'rb') as f:
                if f.read() == data:
                    return
        except OSError:
            pass
    os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
    _write_bytes(dst, data)
    copied += 1


for top in PUB:
    src = os.path.join('website', top)
    if os.path.isfile(src):
        sync_file(src, top)
    elif os.path.isdir(src):
        for dp, dn, fn in os.walk(src):
            dn[:] = [d for d in dn if d not in SKIP_DIRS]
            for f in fn:
                s = os.path.join(dp, f)
                d = os.path.relpath(s, 'website')
                sync_file(s, d)

for p in PRUNE:
    if os.path.isfile(p):
        os.remove(p)
        removed += 1
        print('pruned', p)

print('copied/updated: %d  removed: %d' % (copied, removed))

# Consent gate last: every page needs the cookie banner + a CSP that allows the
# tag, including pages this script just copied. Idempotent (see the tool).
import subprocess
subprocess.run([sys.executable, os.path.join('tools', 'inject_consent.py')],
               check=True)
