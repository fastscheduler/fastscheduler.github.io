#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tell Bing/Yandex/etc. that pages changed - IndexNow submission.

Why this exists
---------------
Indexing is not automatic. Google only re-reads what it re-crawls, and
after a deploy of 676 pages the crawl budget decides how much of it gets
seen. IndexNow is the one lever a site owner actually controls: you POST
the URLs you changed and participating crawlers (Bing, Yandex, DuckDuckGo,
and increasingly others) come and fetch them now instead of waiting days.

The API is public and needs no account, only a key file hosted on the site.

The key file is the part people get wrong
----------------------------------------
IndexNow answers 422 key_not_found unless it can fetch the key from
    https://<host>/<key>.txt        (root of the host)
or, when the site lives in a subdirectory, from the site root:
    https://<host>/<path>/<key>.txt

This site is served from a REPOSITORY SUBNAME
(https://fastscheduler.github.io/), so the key file has to
sit at the root of THAT deploy tree - repo root and website/ - not at the
repository root and not inside the page directory. It is published through
the PUB allowlist in sync_root.py / sync_audit.py for exactly that reason.

Because the key file only goes live when the deploy does, the very first
submission after adding it will fail until the push lands. That is expected;
this script says so instead of returning a bare 422.

Usage
-----
    python tools/indexnow.py --check          verify the key is reachable
    python tools/indexnow.py --all            submit every sitemap URL
    python tools/indexnow.py                 submit pages changed vs HEAD
    python tools/indexnow.py <url> [<url>...] submit specific URLs
    python tools/indexnow.py --dry-run ...    print, do not send

`--changed` (the default) diffs the working tree against HEAD and maps each
changed .html to its published URL, so the common case - edit something,
push, notify - needs no arguments.
"""
import argparse
import io
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE = 'https://fastscheduler.github.io/'
KEY = '5817133906fc4ab78b0f19ca52bf8f58'
KEY_FILE = KEY + '.txt'
API = 'https://api.indexnow.org/indexnow'
HOST = 'fastscheduler.github.io'
KEY_URL = SITE + KEY_FILE

TIMEOUT = 20


def out(msg):
    """Windows consoles here are cp1252; never let a print kill the script."""
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()


def _fetch(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data,
                                 headers=headers or {})
    return urllib.request.urlopen(req, timeout=TIMEOUT)


def fetch_key():
    """Return (ok, detail). IndexNow only accepts a key it can download."""
    try:
        r = _fetch(KEY_URL)
    except urllib.error.HTTPError as e:
        return False, 'HTTP %s from %s' % (e.code, KEY_URL)
    except Exception as e:  # noqa: BLE001 - network failure of any kind
        return False, '%s: %s' % (type(e).__name__, e)
    body = r.read().decode('utf-8', 'replace').strip()
    if body != KEY:
        return False, 'key file at %s contains %r, expected the key' % (
            KEY_URL, body[:40])
    return True, 'key file served correctly at %s' % KEY_URL


def local_key_ok():
    """The file has to be in the deploy tree before a push carries it."""
    missing = [p for p in (os.path.join('website', KEY_FILE), KEY_FILE)
               if not os.path.isfile(os.path.join(ROOT, p))]
    return (not missing), missing


def changed_files():
    """Every .html that differs from HEAD PLUS every untracked .html.

    `git diff HEAD` alone is not enough: it only sees tracked files, so a
    page that is NEW is invisible until it is committed. That is exactly
    the case that matters here - the whole /ru/ tree was untracked, and
    `git diff` reported zero Russian pages changed.
    """
    files = set()
    cmds = (
        ['git', '-C', ROOT, 'diff', '--name-only', 'HEAD'],
        ['git', '-C', ROOT, 'ls-files', '--others', '--exclude-standard'],
    )
    for cmd in cmds:
        try:
            out_s = subprocess.check_output(
                cmd, stderr=subprocess.DEVNULL).decode('utf-8', 'replace')
        except Exception as e:  # noqa: BLE001
            return None, 'git failed (%s): %s' % (cmd[3], e)
        files.update(l.strip() for l in out_s.splitlines()
                     if l.strip().endswith('.html'))
    return sorted(files), None


# Directories served from the root but never indexed (noindex / staging
# copies). Telling a crawler to re-fetch these is pure noise.
SKIP_PREFIX = ('_hero_phone_backup', '_build', 'legal/history')
# 404.html is served for unknown paths and is deliberately absent from
# sitemap.xml; asking crawlers to re-fetch it invites soft-404 handling.
SKIP_FILES = ('404.html',)


def to_url(rel):
    """Map a repo-relative path to its published URL.

    website/ is the source tree; the repo root is what GitHub Pages serves.
    blog/a/x.html and website/blog/a/x.html are the same public URL.
    """
    p = rel.replace('\\', '/')
    if p.startswith('website/'):
        p = p[len('website/'):]
    if p.startswith(SKIP_PREFIX) or '/history/' in p or p in SKIP_FILES:
        return None
    if p.endswith('index.html'):
        return SITE + p[:-len('index.html')]
    if p.endswith('.html'):
        return SITE + p
    return None


def sitemap_urls():
    """Pull every <loc> out of sitemap.xml.

    Handles both shapes the file is written in: `<loc>url</loc>` on one line
    and the tag split across lines. The one-liner case is the easy one to get
    wrong - buffering until `</loc>` yields an empty string for every URL.
    """
    path = os.path.join(ROOT, 'sitemap.xml')
    if not os.path.isfile(path):
        return []
    with io.open(path, 'r', encoding='utf-8') as f:
        txt = f.read()
    urls, buf, grab = [], [], False
    for line in txt.splitlines():
        s = line.strip()
        start = s.find('<loc>')
        if start != -1:
            rest = s[start + len('<loc>'):]
            end = rest.find('</loc>')
            if end != -1:
                urls.append(rest[:end].strip())   # whole URL on this line
                buf, grab = [], False
                continue
            grab, buf = True, [rest]
            continue
        end = s.find('</loc>')
        if end != -1 and grab:
            buf.append(s[:end])
            urls.append(''.join(buf).strip())
            buf, grab = [], False
            continue
        if grab:
            buf.append(s)
    return urls


def submit(urls, dry=False, key_verified=True):
    """POST the batch (IndexNow's documented method); GET as a fallback.

    IndexNow answers 202 for a GET it cannot verify yet - it queues the
    request rather than rejecting it. That is NOT delivery. Counting a 202
    as success and exiting 0 made a completely unverified submission look
    like a working one, so the two states are reported separately.
    """
    urls = sorted(set(u for u in urls if u))
    if not urls:
        return 0, 'no URLs to submit', True
    body = json.dumps({'host': HOST, 'key': KEY,
                       'keyLocation': SITE + KEY_FILE,
                       'urlList': urls}).encode('utf-8')
    if dry:
        return 0, 'dry run: would POST %d URL(s)\n%s' % (
            len(urls), '\n'.join('  ' + u for u in urls)), True

    delivered = False
    try:
        r = _fetch(API, data=body, headers={
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'FastScheduler-IndexNow/1.0'})
        r.read()
        return len(urls), 'POST batch of %d -> HTTP %d (accepted)' % (
            len(urls), r.status), True
    except urllib.error.HTTPError as e:
        detail = e.read().decode('utf-8', 'replace')[:300]
        post = 'POST batch -> HTTP %s %s' % (e.code, detail)
    except Exception as e:  # noqa: BLE001
        post = 'POST batch failed: %s' % e

    # Fallback: GET per URL, the other form the IndexNow docs accept.
    #
    # Only worth running when the key file is actually reachable. If it is
    # not, every GET comes back 202 (queued, then discarded), so the sweep
    # would issue hundreds of requests to learn nothing it did not already
    # know from the POST status. Cap it too, and say so rather than
    # truncating silently.
    if not key_verified:
        return 0, (post + '\n  key file is not reachable, so the per-URL GET '
                          'fallback is skipped: it would return 202 for every '
                          'URL and the requests would be discarded'), False

    cap = min(len(urls), 500)
    ok, queued, notes = 0, 0, []
    for u in urls[:cap]:
        try:
            r = _fetch('%s?url=%s&key=%s' % (API, u, KEY))
            r.read()
            if r.status == 202:
                queued += 1
            else:
                ok += 1
        except urllib.error.HTTPError as e:
            e.read()
            notes.append('%s -> HTTP %s' % (u, e.code))
        except Exception as e:  # noqa: BLE001
            notes.append('%s -> %s' % (u, e))

    summary = '%s | GET fallback: %d accepted, %d queued-unverified, %d failed' % (
        post, ok, queued, cap - ok - queued)
    if cap < len(urls):
        summary += ' (capped at %d of %d; re-run for the rest)' % (
            cap, len(urls))
    if ok:
        delivered = True
    elif queued:
        summary += ('\n  NOTE: 202 means queued, not delivered.')
    if notes:
        summary += '\n  first errors: ' + '; '.join(notes[:5])
    return ok, summary, delivered


def main():
    ap = argparse.ArgumentParser(
        description='Submit changed URLs to IndexNow.')
    ap.add_argument('urls', nargs='*', help='absolute URLs to submit')
    ap.add_argument('--check', action='store_true',
                    help='only verify the key file is reachable')
    ap.add_argument('--all', action='store_true',
                    help='submit every URL in sitemap.xml')
    ap.add_argument('--changed', action='store_true',
                    help='submit pages changed vs HEAD (default)')
    ap.add_argument('--dry-run', action='store_true',
                    help='print what would be sent, send nothing')
    ap.add_argument('--skip-key-check', action='store_true',
                    help='submit even if the key file is not reachable')
    args = ap.parse_args()

    ok, missing = local_key_ok()
    if not ok:
        out('LOCAL ERROR: %s missing from the deploy tree: %s'
            % (KEY_FILE, ', '.join(missing)))
        out('It must exist in both website/ and the repo root.')
        return 2
    out('local key file present in website/ and repo root: yes')

    if args.check:
        ok, detail = fetch_key()
        out('remote key check: %s' % detail)
        return 0 if ok else 1

    # Refuse to submit against a key the crawler cannot read.
    key_verified = False
    if not args.skip_key_check:
        ok, detail = fetch_key()
        if not ok:
            out('REMOTE KEY NOT REACHABLE: %s' % detail)
            if os.environ.get('CI') or 'github' in os.environ.get(
                    'GITHUB_ACTIONS', ''):
                out('running in CI - skipping the live check and submitting '
                    'anyway')
            else:
                out('The key file is not deployed yet. Push first, then run '
                    'this again, or pass --skip-key-check to force.')
                return 1
        else:
            out('remote key check: %s' % detail)
            key_verified = True
    else:
        out('WARNING: --skip-key-check. The key file may not be live, so '
            'anything submitted below can be discarded by IndexNow.')

    if args.all:
        urls = sitemap_urls()
        if not urls:
            out('sitemap.xml yielded no URLs')
            return 2
        out('submitting all %d sitemap URLs' % len(urls))
    elif args.urls:
        urls = list(args.urls)
    else:
        files, err = changed_files()
        if err:
            out(err)
            return 2
        urls = []
        for f in files:
            u = to_url(f)
            if u:
                urls.append(u)
        uniq = sorted(set(urls))
        out('%d changed .html file(s) -> %d published URL(s)'
            % (len(files), len(uniq)))
        urls = uniq

    if not urls:
        out('nothing changed to submit')
        return 0

    sent, note, delivered = submit(urls, dry=args.dry_run,
                                   key_verified=key_verified)
    out(note)
    if not args.dry_run:
        if not key_verified and not args.skip_key_check:
            out('rejected: key file is not live. Push, then re-run.')
            return 1
        if delivered:
            out('accepted by IndexNow: %d URL(s)' % sent)
            return 0
        # Two distinct failures land here, and they need opposite advice. When
        # the key file is unreachable the fix is to push; when it is reachable
        # and still refused, the file is served but the key is not verified for
        # this host, and pushing again changes nothing.
        if not key_verified:
            out('NOT delivered. Re-run after the key file is live at %s' % KEY_URL)
        else:
            out('NOT delivered, and the key file IS live at %s.' % KEY_URL)
            out('The remaining cause is ownership, not deployment: IndexNow has')
            out('no verified key for this host. Register the key with your IndexNow')
            out('/ Bing Webmaster Tools account for %s and complete host' % HOST)
            out('verification, then re-run this. Pushing again will not help.')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())