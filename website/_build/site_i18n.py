"""Website copy loader: ``translations/website/<lang>.json``.

The site has exactly one template per page type. Both languages render through
it, and the only thing that changes is the strings handed to the template — so
`/legal/privacy.html` and `/ru/legal/privacy.html` cannot drift apart any more
than a translation does.

Fallback rule: a key missing from ``ru.json`` returns the English string rather
than raising or rendering an empty element. A half-finished translation must
never produce a broken page.

Usage:
    from site_i18n import t, chrome, doc

    t('ru', 'legal', 'ui', 'contents')        -> 'Содержание'
    t('en', 'legal', 'ui', 'last_updated', date='October 26, 2026')
    chrome('ru')['open_bot']                   -> 'Открыть бота'
"""
from __future__ import annotations

import json
import os

LANGS = ('en', 'ru')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR = os.path.join(ROOT, 'translations', 'website')

_cache: dict[str, dict] = {}


def _read(lang: str) -> dict:
    if lang in _cache:
        return _cache[lang]
    path = os.path.join(DIR, '%s.json' % lang)
    try:
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        raise SystemExit('[i18n] cannot read %s: %s' % (path, exc))
    _cache[lang] = data
    return data


def catalog(lang: str) -> dict:
    """The language's catalog, with English filling any gap."""
    if lang not in LANGS:
        lang = 'en'
    base = _read('en')
    if lang == 'en':
        return base
    data = dict(base)
    other = _read(lang)
    for k, v in other.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            merged = dict(base[k])
            merged.update(v)
            data[k] = merged
        else:
            data[k] = v
    return data


def chrome(lang: str) -> dict:
    return dict(catalog(lang).get('chrome') or {})


def doc(lang: str, name: str) -> dict:
    """One legal document's copy: title, description, meta, changelog."""
    docs = (catalog(lang).get('legal') or {}).get('docs') or {}
    base = ((catalog('en').get('legal') or {}).get('docs') or {}).get(name) or {}
    here = docs.get(name) or {}
    out = dict(base)
    out.update(here)
    cl = dict(base.get('changelog') or {})
    cl.update(here.get('changelog') or {})
    if cl:
        out['changelog'] = cl
    return out


def t(lang: str, *path: str, **fmt) -> str:
    """Look a string up by path; ``str.format`` only when fmt is given."""
    node = catalog(lang)
    for part in path:
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            node = None
            break
    if node is None:
        node = catalog('en')
        for part in path:
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                node = ''
                break
    text = node if isinstance(node, str) else ''
    return text.format(**fmt) if fmt else text
