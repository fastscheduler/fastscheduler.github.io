#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Server-rendered Russian hub/landing pages + RU search-data file."""

import io
import json
import os
import re
import sys
from html.parser import HTMLParser
import html as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'website')
BUILD = os.path.join(SITE, '_build')
BATCH = os.path.join(ROOT, 'tools', 'ru_batches')

sys.path.insert(0, BUILD)
sys.path.insert(0, ROOT)

import build_help as bh  # noqa: E402
import build_static as bs  # noqa: E402
import importlib.util as _ilu

BASE = 'https://fastscheduler.github.io'
BS_CHR = chr(92)
NL = chr(10)

SKIP_TAGS = {'script', 'style', 'code', 'pre', 'textarea'}
SKIP_CLASSES = {'phone-stage', 'demo', 'ios-app', 'chan-msg', 'sl-head',
                'sl-foot', 'tg-header', 'tg-input', 'tg-explorer',
                'rl-notif', 'fx-bar', 'fs-lang-seg'}


def _load_pairs(path):
    s = io.open(path, encoding='utf-8').read()
    out = []
    n = len(s)
    i = 0
    SQ = chr(39)
    while i < n:
        if s[i] == SQ:
            j = i + 1
            buf = []
            closed = False
            while j < n:
                c = s[j]
                if c == BS_CHR and j + 1 < n:
                    buf.append(s[j + 1])
                    j += 2
                    continue
                if c == SQ:
                    closed = True
                    break
                buf.append(c)
                j += 1
            if not closed:
                i += 1
                continue
            key = ''.join(buf)
            k = j + 1
            while k < n and s[k] in ' :\t\r\n':
                k += 1
            if k < n and s[k] == SQ:
                j = k + 1
                buf = []
                closed = False
                while j < n:
                    c = s[j]
                    if c == BS_CHR and j + 1 < n:
                        buf.append(s[j + 1])
                        j += 2
                        continue
                    if c == SQ:
                        closed = True
                        break
                    buf.append(c)
                    j += 1
                if closed:
                    out.append((key, ''.join(buf)))
                    i = j + 1
                    continue
            i = j + 1
        else:
            i += 1
    return out


def load_map():
    MAP = {}
    for name in ('ru-chrome.js', 'lang.js'):
        for k, v in _load_pairs(os.path.join(SITE, 'scripts', name)):
            MAP.setdefault(k, v)
    return MAP


RU_EXT = {
    'Up next': 'Далее',
    'Next': 'Далее',
    'Previous': 'Назад',
}


def plural(n, one, few, many):
    n = abs(int(n))
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and (n % 100 < 12 or n % 100 > 14):
        return few
    return many


class RUTransformer(HTMLParser):
    def __init__(self, MAP):
        super().__init__(convert_charrefs=True)
        self.MAP = MAP
        self.out = []
        self.stack = []
        self.unmapped = {}

    def _skip(self):
        for tag, attrs in self.stack:
            if tag in SKIP_TAGS:
                return True
            cls = attrs.get('class', '')
            if attrs.get('data-no-ru') is not None:
                return True
            for c in cls.split():
                if c in SKIP_CLASSES:
                    return True
        return False

    def handle_starttag(self, tag, attrs):
        self.stack.append((tag, dict(attrs)))
        self.out.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        self.out.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    del self.stack[i:]
                    break
        self.out.append('</' + tag + '>')

    def _in_raw(self):
        # script/style bodies are code, not copy: emit byte-identical so
        # inline JS/CSS survive (escaping &&/</> here kills every script).
        for tag, _attrs in self.stack:
            if tag in ('script', 'style'):
                return True
        return False

    def handle_data(self, data):
        if self._in_raw():
            self.out.append(data)
            return
        if not data.strip() or self._skip():
            self.out.append(H.escape(data, quote=False))
            return
        key = data.strip()
        if key in self.MAP:
            lead = data[:len(data) - len(data.lstrip())]
            trail = data[len(data.rstrip()):]
            self.out.append(H.escape(lead, quote=False) + H.escape(self.MAP[key], quote=False) + H.escape(trail, quote=False))
        else:
            if len(key) >= 3 and re.search(r'[A-Za-z]', key) and not re.search(r'[А-яЁё]', key):
                self.unmapped[key] = self.unmapped.get(key, 0) + 1
            self.out.append(H.escape(data, quote=False))

    def handle_comment(self, data):
        self.out.append('<!--' + data + '-->')

    def handle_decl(self, decl):
        self.out.append('<!' + decl + '>')

    def handle_pi(self, data):
        self.out.append('<?' + data + '>')


def transform(html, MAP):
    MAP2 = dict(MAP)
    MAP2.update(RU_EXT)
    t = RUTransformer(MAP2)
    t.feed(html)
    t.close()
    return ''.join(t.out), t.unmapped


RU_KEEP = {
    # Plan labels kept in Latin across RU product copy (matches bot + batches).
    'Free:', '. Premium:', 'Premium:', 'Free', 'Premium',
    # Product / brand / feature names kept as-is in RU.
    'Telegram Stars', 'Telegram Stars:', 'Telegram:', 'Telegram',
    'Telegram Ads', 'Email', 'Stars', 'Bots', 'Media Storage',
    'SetDate', 'CryptoBot', 'Fast Scheduler',
    # RU article titles that are intentionally Latin (FAQ acronym etc.).
    'FAQ: API', 'FAQ: Telegram',
    # Time-zone identifiers, contact, kept technical terms.
    'Europe/Berlin', 'UTC', 'fastschedulebot@gmail.com',
    'user ID', 'username Telegram',
    # English etymology kept inside RU explanation (letter p = protected).
    'protected',
    # File formats.
    '.fsback / .fspback', '.fsback', '.fspback',
    '.csv', '.json', '.txt', '.odt', '.rtf',
}

_EXT_RE = re.compile(r'^\.[a-z0-9]+(\s*/\s*\.[a-z0-9]+)?$', re.I)
_EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


def filter_unmapped(unmapped, patch=None):
    """Drop audit noise: known RU titles + intentional Latin tokens.

    Returns a new dict with only genuine leftovers.
    """
    titles = set()
    if patch:
        for _aid, _tr in patch.items():
            if isinstance(_tr, dict):
                _t = (clean_ru(_tr.get('title', '')) or '').strip()
                if _t:
                    titles.add(_t)
    titles.add('Другие темы')
    out = {}
    for k, c in unmapped.items():
        if k in titles or k in RU_KEEP:
            continue
        s = k.strip()
        if not s:
            continue
        head = s.lstrip('•·- ').strip()
        if head[:1] in ('/', '@'):
            continue
        if _EXT_RE.match(s) or _EMAIL_RE.match(s):
            continue
        if s == 'UTC' or s.startswith('UTC+') or s.startswith('UTC-'):
            continue
        out[k] = c
    return out


def set_head(html, title, desc, canonical, en_url):
    html = re.sub(r'<html([^>]*)lang="en"',
                  lambda m: '<html' + m.group(1) + 'lang="ru"', html, count=1)
    html = re.sub(r'<title>.*?</title>', '<title>' + H.escape(title) + '</title>',
                  html, count=1, flags=re.S)
    html = re.sub(r'(<meta name="description" content=").*?(")',
                  lambda m: m.group(1) + H.escape(desc, quote=True) + m.group(2),
                  html, count=1)
    for prop in ('og:title', 'twitter:title'):
        html = re.sub(r'(<meta property="' + prop + r'" content=").*?(")',
                      lambda m: m.group(1) + H.escape(title, quote=True) + m.group(2),
                      html, count=1)
    for prop in ('og:description', 'twitter:description'):
        html = re.sub(r'(<meta (?:property|name)="' + prop + r'" content=").*?(")',
                      lambda m: m.group(1) + H.escape(desc, quote=True) + m.group(2),
                      html, count=1)
    for prop in ('og:url', 'twitter:url'):
        html = re.sub(r'(<meta (?:property|name)="' + prop + r'" content=").*?(")',
                      lambda m: m.group(1) + canonical + m.group(2),
                      html, count=1)
    html = re.sub(r'(<link rel="canonical" href=").*?(")',
                  lambda m: m.group(1) + canonical + m.group(2), html, count=1)
    alt = ('<!--fs:ru-alt-->' + NL
           + '<link rel="alternate" hreflang="ru" href="' + canonical + '">' + NL
           + '<link rel="alternate" hreflang="en" href="' + en_url + '">' + NL
           + '<link rel="alternate" hreflang="x-default" href="' + en_url + '">' + NL
           + '<!--/fs:ru-alt-->')
    mark = re.compile('<!--fs:ru-alt-->.*?<!--/fs:ru-alt-->' + NL + '?', re.S)
    html = mark.sub('', html)
    html = html.replace('</head>', alt + '</head>', 1)
    return html


ASSET_RE = re.compile(r'((?:src|href)=")(scripts/|styles/|fonts/|brand-logo\.png|'
                      r'brand-logo-128\.png|brand-logo-64\.png|icon-96\.png|'
                      r'icon-48\.png|favicon-32\.png|favicon-16\.png|'
                      r'apple-touch-icon\.png|og-cover-v2\.png)')


def fix_asset_paths(html):
    return ASSET_RE.sub(lambda m: m.group(1) + '../' + m.group(2), html)


def load_ru_articles():
    patch = {}
    for f in sorted(os.listdir(BATCH)):
        if f.startswith('help_') and f.endswith('.py'):
            path = os.path.join(BATCH, f)
            spec = _ilu.spec_from_file_location('ru_' + f[:-3], path)
            mod = _ilu.module_from_spec(spec)
            spec.loader.exec_module(mod)
            for k, v in getattr(mod, 'PATCH', {}).items():
                if isinstance(v, dict):
                    patch[k] = v
    return patch


def clean_ru(text):
    if not text or not isinstance(text, str):
        return text
    try:
        text = bh.fill_placeholders(text)
    except Exception:
        pass
    text = re.sub(r'@@[A-Z_]+@@', '', text)
    return text


def strip_ru(html):
    s = re.sub(r'<[^>]+>', ' ', html or '')
    s = H.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()


def build_help_data_ru(patch):
    src = io.open(os.path.join(SITE, 'scripts', 'help-data.js'), encoding='utf-8').read()
    side = json.loads(re.search(r'__HELP_SIDE=(\[.*?\]);', src, re.S).group(1))
    arr = json.loads(re.search(r'__HELP_DATA=(\[.*\])', src, re.S).group(1))
    ru_side = []
    for cat in side:
        cid = cat['id']
        rec = patch.get(cid, {})
        ru_side.append({
            'id': cid,
            'title': clean_ru(rec.get('title', '')) or cat['title'],
            'n': cat['n'],
            'icon': cat['icon'],
            'kids': [{'id': k['id'],
                      't': clean_ru(patch.get(k['id'], {}).get('title', '')) or k['t']}
                     for k in cat.get('kids', [])],
        })
    ru_data = []
    for it in arr:
        aid = it['id']
        tr = patch.get(aid)
        if tr and 'href' not in it:
            faq_txt = ' '.join(
                (strip_ru(f.get('q', '')) + ' ' + strip_ru(f.get('a', ''))).strip()
                for f in (tr.get('faq') or []) if isinstance(f, dict))
            body_txt = strip_ru(clean_ru(tr.get('content') or ''))
            ru_data.append({
                'id': aid, 'c': it['c'],
                't': clean_ru(tr.get('title', '')) or it['t'],
                'b': body_txt or it['b'],
                'f': faq_txt,
                'd': bh.smart_desc(body_txt) if body_txt else it['d'],
            })
        else:
            ru_data.append(it)
    js = ('/* Generated by tools/build_ru_pages.py -- do not edit. */' + NL
          + 'window.__HELP_SIDE='
          + json.dumps(ru_side, ensure_ascii=False, separators=(',', ':'))
          + ';' + NL + 'window.__HELP_DATA='
          + json.dumps(ru_data, ensure_ascii=False, separators=(',', ':'))
          + ';' + NL)
    return js, ru_side, {a['id']: a for a in ru_data}
