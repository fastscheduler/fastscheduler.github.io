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

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CURRENT_STAMP = '2026-10-26'
CURRENT_LABEL = 'October 26, 2026'
OLD_STAMP = '2026-09-26'
OLD_LABEL = 'September 26, 2026'

DOCS = {
    'privacy': {
        'en': ('Privacy Policy',
               'This edition adds the website\u2019s analytics disclosure: Google Analytics 4, '
               'delivered through Google Tag Manager and loaded only after you press Accept.',
               ['A named analytics section: Google Tag Manager / GA4, what is measured, and the two cookies it sets.',
                'Consent is stated as the gate: before a choice, nothing is inserted into the page at all.',
                'Declining is described as leaving every page, feature and download fully available.']),
        'ru': ('Политика конфиденциальности',
               'В этой редакции добавлено описание аналитики сайта: Google Analytics 4 через Google Tag Manager, '
               'который загружается только после нажатия «Принять».',
               ['Отдельный раздел об аналитике: Google Tag Manager / GA4, что измеряется и какие два файла cookie ставятся.',
                'Согласие описано как условие запуска: до выбора ничего не добавляется на страницу.',
                'Отказ описан как полностью равноправный вариант: все страницы и функции остаются доступны.']),
    },
    'terms': {
        'en': ('Terms of Service',
               'The effective date moved with the privacy refresh; the rules themselves are unchanged.',
               ['References to the website\u2019s measurement tools point at the updated Privacy Policy.']),
        'ru': ('Условия использования',
               'Дата вступления в силу обновлена вместе с политикой конфиденциальности; сами правила не изменились.',
               ['Ссылки на инструменты измерения сайта ведут на обновлённую Политику конфиденциальности.']),
    },
    'refundpolicy': {
        'en': ('Refund Policy',
               'The effective date moved with the privacy refresh; refund terms are unchanged.',
               ['No change to Stars finality, cancellation or the discretionary cases.']),
        'ru': ('Политика возврата',
               'Дата вступления в силу обновлена вместе с политикой конфиденциальности; условия возврата не изменились.',
               ['Правила по Stars, отмена и исключительные случаи не изменились.']),
    },
}

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


def block_html(doc, lang='en', in_history=False):
    title, summary, bullets = DOCS[doc][lang]
    if lang == 'ru':
        head = 'Версии документа'
        pill = CURRENT_STAMP + ' · текущая'
        cur_sub, old_sub = 'текущая', 'архив'
        eff = ('Действует с <b>%s</b>. Эта редакция заменяет версию от %s; '
               'прошлые редакции остаются опубликованными.' % (CURRENT_LABEL, OLD_LABEL))
        changes = 'Что изменилось в этой редакции.'
        hist = '../%s.html' % doc if in_history else 'history/%s-%s.html' % (doc, OLD_STAMP)
        cur_href = ('../%s.html' % doc) if in_history else None
    else:
        head = 'Document versions'
        pill = CURRENT_STAMP + ' · current'
        cur_sub, old_sub = 'current', 'archived'
        eff = ('Effective <b>%s</b>. This edition replaces the %s text; every earlier '
               'edition stays published below.' % (CURRENT_LABEL, OLD_LABEL))
        changes = 'What changed in this version.'
        hist = '../%s.html' % doc if in_history else 'history/%s-%s.html' % (doc, OLD_STAMP)
        cur_href = ('../%s.html' % doc) if in_history else None
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
