# -*- coding: utf-8 -*-
"""Apply the sender-first / RBAC help rewrite to translations/{en,es,ru}.json.

Run from the repo root:

    python tools/apply_rbac_help_v2.py           # apply
    python tools/apply_rbac_help_v2.py --check   # report only, write nothing

Why a script instead of hand-editing three 800-key JSON files: the same content
must land in all three languages, the help tree must stay self-consistent
(children point at real articles), and the numbers in the text must match
src/channels/admins.py and src/services/{admin_link_recheck,main_bot_fallback}.py.
The script fails loudly if a stale claim survives, so a re-run is a no-op and a
missed article is visible.

Content lives in tools/help_v2_{en,es,ru}.py.
"""

import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from help_v2_en import CONTENT_EN, REPLACE_EN   # noqa: E402
from help_v2_es import CONTENT_ES               # noqa: E402
from help_v2_ru import CONTENT_RU               # noqa: E402

# Exact-substring corrections for articles that only needed a stale claim
# replaced (Spanish and Russian get full rewrites of these, so only EN here).
REPLACE = {'en': REPLACE_EN, 'es': {}, 'ru': {}}

CONTENT = {'en': CONTENT_EN, 'es': CONTENT_ES, 'ru': CONTENT_RU}

# Where a new article is linked from, so it is reachable from the hub.
PARENT_CHILDREN = {
    'admins': ['admins_attach'],
    'bots': ['main_bot_stand_in'],
    'start': ['sender_bot_setup', 'tutorial_walkthrough'],
    'getting_started': ['sender_bot_setup'],
}

# A claim that was true before the rewrite and is now actively misleading.
STALE_CLAIMS = [
    '@FastSchedulerBot must be an administrator',
    '@FastSchedulerBot</b> <b>admin</b>',
    'Add @FastSchedulerBot as an administrator',
    'Haz a <b>@FastSchedulerBot</b> <b>admin</b>',
    'Сделайте <b>@FastSchedulerBot</b> <b>Администратором</b>',
    'найдите @FastSchedulerBot',
]

PLACEHOLDER_RE = re.compile(r'\{([a-z_0-9]+)\}')


def _load(lang):
    path = os.path.join(ROOT, 'translations', lang + '.json')
    with io.open(path, encoding='utf-8-sig') as f:
        return path, json.load(f)


def _dump(path, data):
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def _check_article(lang, key, rec, problems):
    if not rec.get('title'):
        problems.append(f'{lang}:{key}: missing title')
    if not rec.get('description'):
        problems.append(f'{lang}:{key}: missing description')
    if not rec.get('content'):
        problems.append(f'{lang}:{key}: missing content')
    for field in ('title', 'description', 'content'):
        text = rec.get(field) or ''
        if '<b>' in text or '<i>' in text:
            if text.count('<b>') != text.count('</b>'):
                problems.append(f'{lang}:{key}: unbalanced <b> in {field}')
            if text.count('<i>') != text.count('</i>'):
                problems.append(f'{lang}:{key}: unbalanced <i> in {field}')
    for link in re.findall(r'\[\[([a-z0-9_]+)\|', rec.get('content') or ''):
        pass  # resolved against the merged tree by _check_links
    for faq in rec.get('faq') or []:
        if not faq.get('q') or not faq.get('a'):
            problems.append(f'{lang}:{key}: faq item missing q/a')


def _check_links(lang, tree, problems):
    for key, rec in tree.items():
        if not isinstance(rec, dict):
            continue
        text = (rec.get('content') or '') + ' ' + (rec.get('description') or '')
        for faq in rec.get('faq') or []:
            text += ' ' + (faq.get('a') or '')
        for target in re.findall(r'\[\[([a-z0-9_]+)\|', text):
            if target not in tree:
                problems.append(f'{lang}:{key}: link to missing article {target}')
        for child in rec.get('children') or []:
            if child not in tree:
                problems.append(f'{lang}:{key}: child {child} is not an article')


def _check_placeholders(lang, key, rec, problems):
    expected = {'scheduled_free', 'monthly_sent_free', 'recurring_free',
                'channels_free', 'channels_prem', 'bots_free', 'bots_prem', 'tz'}
    for field in ('title', 'description', 'content'):
        for name in PLACEHOLDER_RE.findall(rec.get(field) or ''):
            if name not in expected:
                problems.append(f'{lang}:{key}: unknown placeholder {{{name}}} in {field}')


def _check_stale(lang, tree, problems):
    for key, rec in tree.items():
        if not isinstance(rec, dict):
            continue
        blob = ' '.join([
            str(rec.get('title') or ''),
            str(rec.get('description') or ''),
            str(rec.get('content') or ''),
        ] + [f"{f.get('q','')} {f.get('a','')}" for f in (rec.get('faq') or [])])
        for claim in STALE_CLAIMS:
            if claim in blob:
                problems.append(f'{lang}:{key}: stale claim still present: {claim!r}')


def apply_lang(lang, apply_changes=True):
    path, data = _load(lang)
    help_tree = data.setdefault('help', {})
    problems = []

    for key, rec in CONTENT[lang].items():
        new_rec = dict(rec)
        # Keep an existing icon/flag-ish fields the help renderer may use.
        existing = help_tree.get(key)
        if isinstance(existing, dict):
            for carry in ('icon', 'emoji', 'order'):
                if carry in existing and carry not in new_rec:
                    new_rec[carry] = existing[carry]
        help_tree[key] = new_rec
        _check_article(lang, key, new_rec, problems)
        _check_placeholders(lang, key, new_rec, problems)

    for key, pairs in REPLACE.get(lang, {}).items():
        rec = help_tree.get(key)
        if not isinstance(rec, dict):
            problems.append(f'{lang}: cannot patch missing article {key}')
            continue
        body = (rec.get('content') or '').replace('\r\n', '\n')
        for old, new in pairs:
            if old not in body:
                # Re-running the script must stay a no-op, not a failure: the
                # target is gone precisely because the replacement landed.
                if new and new in body:
                    continue
                problems.append(f'{lang}:{key}: replacement target not found: {old[:60]!r}')
                continue
            body = body.replace(old, new, 1)
        rec['content'] = body

    for parent, children in PARENT_CHILDREN.items():
        parent_rec = help_tree.get(parent)
        if not isinstance(parent_rec, dict):
            problems.append(f'{lang}: parent article {parent} missing')
            continue
        current = list(parent_rec.get('children') or [])
        changed = False
        for child in children:
            if child not in current and child in help_tree:
                current.append(child)
                changed = True
        if changed:
            parent_rec['children'] = current

    _check_links(lang, help_tree, problems)
    _check_stale(lang, help_tree, problems)

    if problems:
        for p in problems:
            print('  !', p)
        raise SystemExit(f'{lang}: {len(problems)} problem(s) — nothing written')

    if apply_changes:
        _dump(path, data)
        print(f'{lang}: wrote {len(CONTENT[lang])} articles to {os.path.relpath(path, ROOT)}')
    else:
        print(f'{lang}: {len(CONTENT[lang])} articles ready (check only, nothing written)')


def main(argv):
    check_only = '--check' in argv
    for lang in ('en', 'es', 'ru'):
        apply_lang(lang, apply_changes=not check_only)


if __name__ == '__main__':
    main(sys.argv[1:])
