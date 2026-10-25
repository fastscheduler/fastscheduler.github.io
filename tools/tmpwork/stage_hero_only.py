# -*- coding: utf-8 -*-
"""Stage only the hero-channel hunks of the two index files.

The working copy also carries someone else's uncommitted pricing copy edit;
that must stay unstaged. So: read the diff, keep hunks that mention the hero
channel markup or the cache-bust version, drop everything else, and apply the
filtered patch to the index.
"""
import io
import os
import subprocess
import sys

FILES = ['website/index.html', 'website/ru/index.html',
         'index.html', 'ru/index.html']
KEEP = ('chan-', 'hero-demo.js?v=20261006a2', 'hero-cinema.css?v=20261006a2')
DROP = ('pprice', 'Everything in Monthly', 'breaks down to', 'if paid monthly',
        'в пересчёте', 'при помесячной оплате', 'Всё из месячного тарифа')


def run(args, **kw):
    r = subprocess.run(args, capture_output=True, **kw)
    r.stdout = (r.stdout or b'').decode('utf-8', 'replace')
    r.stderr = (r.stderr or b'').decode('utf-8', 'replace')
    return r


res0 = run(['git', 'diff', '--'] + FILES)
if res0.returncode != 0:
    print('git diff failed')
    print(res0.stderr)
    sys.exit(1)
raw = res0.stdout
if not raw.strip():
    print('nothing to stage')
    sys.exit(0)

out = []
kept = dropped = 0
header = []
hunks = []
cur = None
for line in raw.splitlines(True):
    if line.startswith('diff --git '):
        if cur:
            hunks.append(cur)
            cur = None
        header = [line]
        if cur:
            hunks.append(cur)
            cur = None
        continue
    if line.startswith('@@'):
        if cur:
            hunks.append(cur)
        cur = {'head': line, 'body': [], 'file_header': list(header)}
        header = []
        continue
    if cur:
        cur['body'].append(line)
    else:
        header.append(line)
if cur:
    hunks.append(cur)

# now group by file_header (only the first hunk per file carries it;
# the rest inherit the running one)
byfile = []
cur_fh = None
for h in hunks:
    fh = h['file_header'] or cur_fh
    if not fh or not fh[0].startswith('diff --git '):
        continue
    cur_fh = fh
    body = ''.join(h['body'])
    text = body
    keep = any(k in text for k in KEEP) and not any(d in text for d in DROP)
    if not byfile or byfile[-1][0] != fh:
        byfile.append((fh, []))
    if keep:
        byfile[-1][1].append(h['head'] + body)
        kept += 1
    else:
        dropped += 1

patch = []
for fh, kept_hunks in byfile:
    if not kept_hunks:
        continue
    patch.extend(fh)
    patch.extend(kept_hunks)

if not patch:
    print('no hero hunks found (kept=0 dropped=%d)' % dropped)
    sys.exit(0)

path = 'tools/tmpwork/hero_only.patch'
io.open(path, 'w', encoding='utf-8', newline='').write(''.join(patch))
print('kept=%d dropped=%d -> %s' % (kept, dropped, path))

res = run(['git', 'apply', '--cached', '--recount', path])
if res.returncode != 0:
    print('APPLY FAILED')
    print(res.stdout)
    print(res.stderr)
    sys.exit(1)
print('staged ok')
