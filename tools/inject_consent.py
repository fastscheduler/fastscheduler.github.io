# -*- coding: utf-8 -*-
"""Turn on the consent gate: CSP allowances + the consent script on every page.

Two things have to be true on a published page before Google Tag Manager can
exist there at all:

1. the strict Content-Security-Policy (`script-src 'self'`) has to allow
   googletagmanager.com, or the tag is blocked before it is even fetched — and
   blocked forever, silently, in production only;
2. the page has to load scripts/consent.js, which is what asks the visitor and
   injects the container *only* after Accept.

Both are applied here instead of inside the three builders because the CSP
fragment is duplicated in four templates and the script tag belongs on pages the
builders do not touch (404, legal history, hand-maintained landing pages). The
pass is idempotent, so running it twice changes nothing, and it is wired into
tools/sync_root.py so a normal publish cannot forget it.

    python tools/inject_consent.py            # apply
    python tools/inject_consent.py --check    # report only
"""

import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

VERSION = '20261025a1'
SCRIPT_TAG = '<script src="%sscripts/consent.js?v=%s" defer></script>\n'

OLD_POLICY = ("default-src 'self'; script-src 'self' 'unsafe-inline'; "
              "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
              "font-src 'self'; connect-src 'self'; object-src 'none'; "
              "form-action 'self'; base-uri 'self'; upgrade-insecure-requests")

NEW_POLICY = ("default-src 'self'; script-src 'self' 'unsafe-inline' "
              "https://www.googletagmanager.com; "
              "style-src 'self' 'unsafe-inline'; "
              "img-src 'self' data: https://www.googletagmanager.com "
              "https://*.google-analytics.com https://*.analytics.google.com "
              "https://www.google.com; font-src 'self'; "
              "connect-src 'self' https://www.googletagmanager.com "
              "https://*.google-analytics.com https://*.analytics.google.com "
              "https://region1.google-analytics.com https://www.google.com; "
              "frame-src https://www.googletagmanager.com; "
              "object-src 'none'; form-action 'self'; base-uri 'self'; "
              "upgrade-insecure-requests")

SKIP_DIRS = {'.git', '.venv', 'node_modules', 'backups', 'backup', '__pycache__',
             'alwaysdata', 'freebuff-sites-build', '.uv-cache-rich-test',
             '1Fast Schedule & SetDate', 'data', 'database', 'media',
             '_hero_phone_backup', 'tmp'}


def html_files(base):
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith('.html'):
                yield os.path.join(dirpath, name)


def patch_page(path, check_only, stats):
    rel_dir = os.path.relpath(os.path.dirname(path), ROOT)
    depth = 0 if rel_dir == '.' else rel_dir.count(os.sep) + 1
    if path.startswith(os.path.join(ROOT, 'website') + os.sep):
        depth = max(0, depth - 1)  # website/ is itself the site root
    prefix = '../' * depth

    with io.open(path, encoding='utf-8', errors='replace') as f:
        src = f.read()
    out = src

    if 'scripts/consent.js' not in out:
        if '</head>' not in out:
            stats['skipped'] += 1
            return
        out = out.replace('</head>', SCRIPT_TAG % (prefix, VERSION) + '</head>', 1)
        stats['tag'] += 1

    if OLD_POLICY in out:
        out = out.replace(OLD_POLICY, NEW_POLICY)
        stats['csp'] += 1
    elif 'googletagmanager.com' in out:
        stats['csp_done'] += 1
    else:
        stats['csp_missing'] += 1

    if out != src and not check_only:
        with io.open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(out)


def patch_builders(check_only, stats):
    """Keep the generated pages correct on the next build, not just this one."""
    targets = [
        os.path.join(ROOT, 'website', '_build', 'build_static.py'),
        os.path.join(ROOT, 'website', '_build', 'build_blog.py'),
        os.path.join(ROOT, 'website', '_build', 'build_help.py'),
        os.path.join(ROOT, '_build', 'build_static.py'),
        os.path.join(ROOT, '_build', 'build_blog.py'),
        os.path.join(ROOT, '_build', 'build_help.py'),
    ]
    for path in targets:
        if not os.path.isfile(path):
            continue
        with io.open(path, encoding='utf-8') as f:
            src = f.read()
        if 'googletagmanager.com' in src:
            stats['builder_done'] += 1
            continue
        # fragments are split across python string literals with escaped quotes
        out = src
        for quote in ("\\'", "'"):
            out = out.replace(
                "script-src %sself%s %sunsafe-inline%s; style-src" % (quote, quote, quote, quote),
                "script-src %sself%s %sunsafe-inline%s https://www.googletagmanager.com; style-src"
                % (quote, quote, quote, quote))
            out = out.replace(
                "img-src %sself%s data:; font-src %sself%s; connect-src %sself%s;"
                % (quote, quote, quote, quote, quote, quote),
                "img-src %sself%s data: https://www.googletagmanager.com "
                "https://*.google-analytics.com https://*.analytics.google.com "
                "https://www.google.com; font-src %sself%s; connect-src %sself%s "
                "https://www.googletagmanager.com https://*.google-analytics.com "
                "https://*.analytics.google.com "
                "https://region1.google-analytics.com https://www.google.com; "
                "frame-src https://www.googletagmanager.com;"
                % (quote, quote, quote, quote, quote, quote))
        if out == src:
            stats['builder_miss'] += 1
            continue
        stats['builder'] += 1
        if not check_only:
            with io.open(path, 'w', encoding='utf-8', newline='') as f:
                f.write(out)


def main(argv):
    check_only = '--check' in argv
    stats = dict.fromkeys(
        ('tag', 'csp', 'csp_done', 'csp_missing', 'skipped',
         'builder', 'builder_done', 'builder_miss'), 0)
    for path in html_files(ROOT):
        if os.path.relpath(path, ROOT).startswith('website' + os.sep):
            continue
        patch_page(path, check_only, stats)
    for path in html_files(os.path.join(ROOT, 'website')):
        patch_page(path, check_only, stats)
    patch_builders(check_only, stats)

    print('pages: %d tagged, %d CSP relaxed, %d already relaxed, %d without CSP, %d skipped'
          % (stats['tag'], stats['csp'], stats['csp_done'],
             stats['csp_missing'], stats['skipped']))
    print('builders: %d patched, %d already ok, %d not matched'
          % (stats['builder'], stats['builder_done'], stats['builder_miss']))
    if check_only:
        print('check only — nothing written')


if __name__ == '__main__':
    main(sys.argv[1:])
