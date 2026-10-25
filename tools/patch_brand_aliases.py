# -*- coding: utf-8 -*-
"""Give the brand entity the exact spellings people search for.

Search engines resolve a bot by its name, and people do not type the same string
the page uses: "fastscheduler", "fast scheduler bot", "FastSchedule", the
@handle, or "tg scheduler". The generated help/blog pages already carry a wide
`alternateName` list (BRAND_ALIASES in build_help.py), but the two landing pages
— the ones that rank for the brand query — carried only three or four aliases,
and none of the no-space spellings.

This patch:

1. extends BRAND_ALIASES in both copies of build_help.py with the exact-match
   tokens (no-space, lower-case, with/without @, "FastSchedule"), so every
   generated page inherits them;
2. rewrites the `alternateName` of the JSON-LD blocks in index.html and
   ru/index.html to the full list, plus Russian query spellings for the RU page.

Idempotent: each target is detected by its new marker and skipped on re-run.

    python tools/patch_brand_aliases.py           # apply
    python tools/patch_brand_aliases.py --check   # report only
"""

import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Only the canonical builder. Root _build/ is a stale duplicate of the old
# (article-inlined) help page and has no BRAND_ALIASES block at all — the live
# site is produced from website/_build and copied out by tools/sync_root.py.
BUILDERS = (
    os.path.join(ROOT, 'website', '_build', 'build_help.py'),
)

OLD_ALIASES = """BRAND_ALIASES = [
    'Fast Scheduler Bot', 'FastSchedulerBot', 'FastScheduler',
    'Fast Scheduler Telegram bot', 'TG Scheduler', 'Telegram Scheduler Bot',
    'Telegram post scheduler', 'Fast Schedule Bot', 'TG Fast Scheduler',
    'Fast Scheduler TG', 'fast scheduler telegram bot',
]
"""

NEW_ALIASES = """# How the product is actually typed. The brand is two words, but the bot's
# handle, the domain and most search queries are one: "fastscheduler",
# "FastScheduler", "@FastSchedulerBot", and the older "FastSchedule Bot". Every
# generated page publishes this list as the entity's alternateName so a query in
# any of those spellings resolves to the same entity — a one-character mismatch
# ("fast schedular", "FastSchedule") used to drop the page out of the result.
BRAND_ALIASES = [
    'Fast Scheduler Bot', 'FastSchedulerBot', 'FastScheduler',
    'fastscheduler', 'fastschedulerbot', '@FastSchedulerBot',
    'FastSchedule', 'FastSchedule Bot',
    'Fast Scheduler Telegram bot', 'fast scheduler telegram bot',
    'TG Scheduler', 'Telegram Scheduler Bot', 'Telegram post scheduler',
    'TG Fast Scheduler', 'Fast Scheduler TG',
]
"""

EN_OLD = ['"alternateName": ["FastScheduler", "Fast Scheduler Telegram bot", "@FastSchedulerBot"]',
          '"alternateName": ["FastScheduler", "FastSchedulerBot", "@FastSchedulerBot", "Fast Scheduler Telegram bot"]']

EN_ALIASES = [
    'Fast Scheduler Bot', 'FastSchedulerBot', 'FastScheduler', 'fastscheduler',
    'fastschedulerbot', '@FastSchedulerBot', 'FastSchedule', 'FastSchedule Bot',
    'Fast Scheduler Telegram bot', 'fast scheduler telegram bot',
    'TG Scheduler', 'Telegram Scheduler Bot', 'Telegram post scheduler',
    'TG Fast Scheduler', 'Fast Scheduler TG',
]

RU_ALIASES = EN_ALIASES + [
    'планировщик постов телеграм', 'отложенные посты телеграм',
    'бот для отложенных постов', 'планировщик телеграм',
]


def _json_list(items):
    return '[' + ', '.join('"%s"' % i.replace('"', '\\"') for i in items) + ']'


def patch_builder(path, check_only, problems):
    if not os.path.exists(path):
        problems.append('missing %s' % os.path.relpath(path, ROOT))
        return
    with io.open(path, encoding='utf-8') as f:
        src = f.read()
    rel = os.path.relpath(path, ROOT)
    if "'fastscheduler', 'fastschedulerbot', '@FastSchedulerBot'," in src:
        print('%s: already patched' % rel)
        return
    if OLD_ALIASES not in src:
        problems.append('%s: BRAND_ALIASES block not found' % rel)
        return
    if check_only:
        print('%s: would patch BRAND_ALIASES' % rel)
        return
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(src.replace(OLD_ALIASES, NEW_ALIASES, 1))
    print('%s: patched BRAND_ALIASES' % rel)


def patch_landing(path, items, check_only, problems):
    if not os.path.exists(path):
        problems.append('missing %s' % os.path.relpath(path, ROOT))
        return
    with io.open(path, encoding='utf-8') as f:
        src = f.read()
    rel = os.path.relpath(path, ROOT)
    target = '"alternateName": ' + _json_list(items)
    if target in src:
        print('%s: already patched' % rel)
        return
    if check_only:
        print('%s: would patch alternateName' % rel)
        return
    out, n = src, 0
    for old in EN_OLD + ['"alternateName": "Fast Scheduler Telegram bot"']:
        if old in out:
            n += out.count(old)
            out = out.replace(old, target)
    if not n:
        problems.append('%s: no known alternateName block to replace' % rel)
        return
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(out)
    print('%s: rewrote %d alternateName block(s)' % (rel, n))


def main(argv):
    check_only = '--check' in argv
    problems = []
    for path in BUILDERS:
        patch_builder(path, check_only, problems)
    patch_landing(os.path.join(ROOT, 'index.html'), EN_ALIASES, check_only, problems)
    patch_landing(os.path.join(ROOT, 'ru', 'index.html'), RU_ALIASES, check_only, problems)
    if problems:
        for p in problems:
            print('  !', p)
        raise SystemExit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
