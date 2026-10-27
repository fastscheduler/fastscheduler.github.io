"""Stamp the legal pages with their version history (idempotent).

Every legal page keeps a visible "which version am I reading" pill, the
effective-date line and a "what changed" note, plus a link to the archived
edition under ``legal/history/``.  The markup and CSS existed before, but
``_build/build_site.py`` regenerated the three pages from markdown and never
put the block back, so the switcher appeared on whatever page had been
hand-stamped last and vanished from the next rebuild.

``stamp_html`` is therefore called from the builder itself; running this file
directly re-stamps every published page in place.

Usage: py -3 tools/legal_versions.py
"""
from __future__ import annotations

import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, 'website', '_build')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import site_i18n as _i18n  # noqa: E402

CURRENT_STAMP = '2026-10-26'
CURRENT_LABEL = 'October 26, 2026'
OLD_STAMP = '2026-09-26'
OLD_LABEL = 'September 26, 2026'

CHEV_D = ('<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
          'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
          '<polyline points="6 9 12 15 18 9"/></svg>')
CHEV_R = ('<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
          'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
          '<polyline points="9 18 15 12 9 6"/></svg>')
CHECK = ('<svg class="ver-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<polyline points="20 6 9 17 4 12"/></svg>')


def _opt(title, sub, href, on):
    inner = ('<span class="ver-v">%s</span><span class="ver-s">%s</span>%s'
             % (title, sub, CHECK if on else CHEV_R))
    if on:
        return ('<span class="gp-row ver-opt on" role="menuitem" aria-current="true">%s</span>'
                % inner)
    return ('<a class="gp-row ver-opt" role="menuitem" href="%s">%s</a>' % (href, inner))


def _ui(lang, key, **fmt):
    return _i18n.t(lang, 'legal', 'ui', key, **fmt)


def _date(lang, which):
    return _i18n.t(lang, 'legal', 'dates', which)


def block_html(doc, lang='en', in_history=False):
    """Version block, rendered from the shared catalogue for this language."""
    meta = _i18n.doc(lang, doc)
    changelog = meta.get('changelog') or {}
    summary = changelog.get('summary') or ''
    bullets = changelog.get('bullets') or []
    head = _ui(lang, 'doc_versions')
    pill = CURRENT_STAMP + ' · ' + _ui(lang, 'current')
    cur_sub, old_sub = _ui(lang, 'current'), _ui(lang, 'archived')
    eff = _ui(lang, 'effective', date=_date(lang, 'current'), old=_date(lang, 'old'))
    changes = _ui(lang, 'what_changed')
    hist = '../%s.html' % doc if in_history else 'history/%s-%s.html' % (doc, OLD_STAMP)
    menu = ''
    if not in_history:
        menu = (_opt(CURRENT_STAMP, cur_sub, None, True)
                + _opt(OLD_STAMP, old_sub, hist, False))
    dd = ''
    if menu:
        dd = ('<div class="ver-dd">'
              '<button type="button" class="ver-pill" aria-haspopup="menu">'
              '<span class="ver-pill-dot" aria-hidden="true"></span>%s%s</button>'
              '<div class="glass-pop ver-menu" role="menu" aria-label="%s">'
              '<div class="gp-head">%s</div>%s</div></div>'
              % (pill, CHEV_D, head, head, menu))
    return ('<p class="effective">%s</p>\n'
            '<div class="ver-changes" role="note"><b>%s</b> <q>%s</q><ul>%s</ul></div>\n'
            '%s' % (eff, changes, summary,
                    ''.join('<li>%s</li>' % b for b in bullets), dd))


def stamp_html(html, doc, lang='en', in_history=False):
    """Insert the version block once, right after the "Last updated" line."""
    if 'ver-dd' in html or 'ver-changes' in html:
        return html
    m = re.search(r'<p class="updated">(.*?)</p>\s*', html, re.S)
    if not m:
        return html
    end = m.end()
    return html[:end] + block_html(doc, lang, in_history) + '\n' + html[end:]


def pages():
    """(path, doc, lang, in_history) for every published legal page."""
    out = []
    combos = [
        ('legal', 'en', False),
        (os.path.join('website', 'legal'), 'en', False),
        (os.path.join('ru', 'legal'), 'ru', False),
        (os.path.join('website', 'ru', 'legal'), 'ru', False),
        (os.path.join('legal', 'history'), 'en', True),
        (os.path.join('website', 'legal', 'history'), 'en', True),
    ]
    for folder, lang, in_hist in combos:
        for doc in DOCS:
            name = '%s-%s.html' % (doc, OLD_STAMP) if in_hist else '%s.html' % doc
            path = os.path.join(REPO, folder, name)
            if os.path.exists(path):
                out.append((path, doc, lang, in_hist))
    return out


def main():
    for path, doc, lang, in_hist in pages():
        html = open(path, encoding='utf-8').read()
        new = stamp_html(html, doc, lang, in_hist)
        if new != html:
            open(path, 'w', encoding='utf-8').write(new)
            print('stamped:', os.path.relpath(path, REPO))
        else:
            print('kept:', os.path.relpath(path, REPO))


if __name__ == '__main__':
    main()
