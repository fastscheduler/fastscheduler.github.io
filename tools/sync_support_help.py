# -*- coding: utf-8 -*-
"""Mirror rewritten help articles into the Support Bot's flat help keys.

The Support Bot does not read translations/*.json: it keeps its own copy of the
help tree as flat keys ("help.<id>.title", "help.<id>.content",
"help.<id>.faq.N.q" ...). Nothing regenerates those, so after a help rewrite the
support bot kept answering with the previous text and did not know the new
articles at all.

This script copies the articles that tools/help_v2_{en,es,ru}.py owns (the
sender-first / RBAC rewrite) from translations/<lang>.json into
"Support Bot/translations/<lang>.json", and drops keys that no longer exist in
the source (e.g. a FAQ item that was removed). Everything else in that file is
left untouched.

Wiki links ([[id|Label]]) are resolved to plain labels: the support bot's
renderer does not understand the marker and would print it verbatim. The
"Open in web" button on each screen is the way to reach the linked article.

    python tools/sync_support_help.py            # apply
    python tools/sync_support_help.py --check    # report only
"""

import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from help_v2_en import CONTENT_EN  # noqa: E402
from help_v2_es import CONTENT_ES  # noqa: E402
from help_v2_ru import CONTENT_RU  # noqa: E402

SOURCES = {'en': CONTENT_EN, 'es': CONTENT_ES, 'ru': CONTENT_RU}
WIKI = re.compile(r'\[\[([a-z0-9_]+)(?:\|([^\]]+))?\]\]')


def plain(text):
    """[[id|Label]] -> Label (the support bot cannot render the marker)."""
    if not isinstance(text, str):
        return text
    return WIKI.sub(lambda m: m.group(2) or m.group(1).replace('_', ' ').title(), text)


def load(path):
    with io.open(path, encoding='utf-8-sig') as f:
        return json.load(f)


def dump(path, data):
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def sync_lang(lang, check_only):
    src_path = os.path.join(ROOT, 'translations', lang + '.json')
    dst_path = os.path.join(ROOT, 'Support Bot', 'translations', lang + '.json')
    src = load(src_path).get('help', {})
    dst = load(dst_path)

    ids = sorted(SOURCES[lang])
    added = updated = removed = 0
    for aid in ids:
        rec = src.get(aid)
        if not isinstance(rec, dict):
            print('  ! %s: article %s missing from translations' % (lang, aid))
            continue
        prefix = 'help.%s.' % aid
        wanted = {}

        title = plain(rec.get('title') or '')
        if title:
            wanted['title'] = title
        content = plain(rec.get('content') or '')
        if content:
            wanted['content'] = content
        children = rec.get('children') or []
        if children:
            wanted['children'] = ','.join(children)
        for i, faq in enumerate(rec.get('faq') or [], start=1):
            if not isinstance(faq, dict):
                continue
            if faq.get('q'):
                wanted['faq.%d.q' % i] = plain(faq['q'])
            if faq.get('a'):
                wanted['faq.%d.a' % i] = plain(faq['a'])
            links = faq.get('links')
            if links:
                wanted['faq.%d.links' % i] = ','.join(links) if isinstance(links, list) else str(links)

        # Drop stale keys of this article (i-th FAQ that no longer exists).
        for key in [k for k in dst if k.startswith(prefix)]:
            if key[len(prefix):] not in wanted:
                del dst[key]
                removed += 1
        for suffix, value in wanted.items():
            key = prefix + suffix
            if dst.get(key) != value:
                if key in dst:
                    updated += 1
                else:
                    added += 1
                dst[key] = value

    print('%s: %d articles — %d new keys, %d changed, %d stale removed'
          % (lang, len(ids), added, updated, removed))
    if not check_only and (added or updated or removed):
        dump(dst_path, dst)
    return added + updated + removed


def main(argv):
    check_only = '--check' in argv
    total = 0
    for lang in ('en', 'es', 'ru'):
        total += sync_lang(lang, check_only)
    if check_only:
        print('check only — nothing written')
    else:
        print('done (%d key changes)' % total)


if __name__ == '__main__':
    main(sys.argv[1:])
