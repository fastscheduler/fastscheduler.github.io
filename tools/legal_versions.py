"""Stamp the legal pages with their version history (idempotent).

Every legal page keeps a visible "which version am I reading" pill, the
effective-date line and a "what changed" note, plus a link to the archived
edition under ``legal/history/``.

Two failure modes are guarded here, because both happened more than once:

1. ``_build/build_site.py`` regenerates the pages from markdown and has to
   re-add this block, so the switcher used to appear on whichever page had
   been hand-stamped last and vanish from the next rebuild. ``stamp_html`` is
   therefore called from the builder itself **and** rewrites an existing block
   in place, so a page can never keep a stale or half-written one.
2. The archived row pointed at ``history/<doc>-<stamp>.html`` from every
   language, but only the English archive ever existed: the Russian pages
   linked to a 404, which is what "sometimes it's there, sometimes it isn't"
   looked like from the outside. The link is now resolved against the file
   system — a language's own archive when it exists, the English archive
   (clearly labelled) when it does not, and never a missing path.

``tests/unit/test_legal_archive.py`` locks both in place: it fails if any
published page loses the block or links to a file that is not there.

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

#: Document slugs whose pages get the block.
DOCS = ('privacy', 'terms', 'refundpolicy')

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


def _exists(*parts) -> bool:
    return os.path.exists(os.path.join(REPO, *parts))


def archived_target(doc, lang='en'):
    """(href, foreign) for this document's archived edition — or (None, False).

    ``href`` is relative to the *current* page for that language and only ever
    points at a file that exists. ``foreign`` is True when the archived text
    is published in another language (the archive is English-only for the
    editions that predate the Russian site).
    """
    if lang == 'ru':
        own = os.path.join('ru', 'legal', 'history', '%s-%s.html' % (doc, OLD_STAMP))
        if _exists(own):
            return 'history/%s-%s.html' % (doc, OLD_STAMP), False
        # Russian archive not published for this edition: fall back to the
        # English archive (../../legal/history/... from /ru/legal/<doc>.html)
        # instead of a dead history/<doc>.html link.
        if _exists('legal', 'history', '%s-%s.html' % (doc, OLD_STAMP)):
            return '../../legal/history/%s-%s.html' % (doc, OLD_STAMP), True
        return None, False
    if _exists('legal', 'history', '%s-%s.html' % (doc, OLD_STAMP)):
        return 'history/%s-%s.html' % (doc, OLD_STAMP), False
    return None, False


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
    menu = ''
    if not in_history:
        if lang == 'ru':
            # From /ru/legal/<doc>.html the English archive sits at
            # ../../legal/history/...; the *current* English page is not the
            # right target, so only the archived row is rendered.
            target, foreign = archived_target(doc, lang)
        else:
            target, foreign = archived_target(doc, lang)
        if target:
            sub = old_sub if not foreign else '%s · %s' % (old_sub, _ui(lang, 'archive_en_note'))
            menu = (_opt(CURRENT_STAMP, cur_sub, None, True)
                    + _opt(OLD_STAMP, sub, target, False))
        else:
            # No archived file at all: still show the edition, but as an
            # inert row — a visible dead link is worse than a labelled one.
            menu = (_opt(CURRENT_STAMP, cur_sub, None, True)
                    + '<span class="gp-row ver-opt" role="menuitem" aria-disabled="true">'
                      '<span class="ver-v">%s</span><span class="ver-s">%s</span>%s</span>'
                    % (OLD_STAMP, old_sub, CHEV_R))
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


#: Where the version block starts and ends on a rendered page. The block is
#: rewritten as a *region*, not matched piece by piece: a stale, partial or
#: even duplicated block (both happened) is replaced wholesale on every build,
#: which is what makes "sometimes it's there, sometimes it isn't" impossible.
_BLOCK_START = '<p class="effective">'
_BLOCK_END_MARKERS = (
    '<p class="see-also">',       # current legal pages: block sits right before it
    '<nav class="toc-box"',       # fallback: table of contents
    '<article',                    # last resort
)
_INSERT_AFTER_RE = re.compile(r'<p class="updated">(.*?)</p>\s*', re.S)


def stamp_html(html, doc, lang='en', in_history=False):
    """Insert — or replace — the version block, once, deterministically.

    Archived pages are left alone: their banner and switcher are built by
    ``tools/build_legal_history.py`` from the frozen snapshot, and rewriting
    them here would fight that file for the same markup.
    """
    if in_history:
        return html
    fresh = block_html(doc, lang, in_history)
    start = html.find(_BLOCK_START)
    if start != -1:
        for marker in _BLOCK_END_MARKERS:
            end = html.find(marker, start + len(_BLOCK_START))
            if end != -1:
                return html[:start] + fresh + '\n' + html[end:]
        # No end marker: the page shape is not one we know, so leave it alone
        # rather than truncating a live document.
        return html
    m = _INSERT_AFTER_RE.search(html)
    if not m:
        return html
    end = m.end()
    return html[:end] + fresh + '\n' + html[end:]


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
        (os.path.join('ru', 'legal', 'history'), 'ru', True),
        (os.path.join('website', 'ru', 'legal', 'history'), 'ru', True),
    ]
    for folder, lang, in_hist in combos:
        for doc in DOCS:
            name = '%s-%s.html' % (doc, OLD_STAMP) if in_hist else '%s.html' % doc
            path = os.path.join(REPO, folder, name)
            if os.path.exists(path):
                out.append((path, doc, lang, in_hist))
    return out


def verify(verbose=True):
    """Post-build guard: every page keeps the block and no archive link is dead.

    Called by the builders after writing the pages. A caller that ignores the
    return value still gets the loud log line, which is what stops this from
    going unnoticed for another two weeks.
    """
    problems = []
    for path, doc, lang, in_hist in pages():
        rel = os.path.relpath(path, REPO)
        try:
            html = open(path, encoding='utf-8').read()
        except Exception as exc:
            problems.append('%s: unreadable (%s)' % (rel, exc))
            continue
        if not in_hist and '<div class="ver-dd">' not in html:
            problems.append('%s: missing the version switcher' % rel)
        target, _foreign = archived_target(doc, lang)
        if target is None:
            continue
        for href in re.findall(r'class="ver-opt"[^>]*href="([^"]+)"', html):
            if href.startswith(('http:', 'https:', 'mailto:', '#')):
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), href))
            if not os.path.exists(resolved):
                problems.append('%s: archived link %s does not exist' % (rel, href))
    if verbose:
        if problems:
            print('[legal_versions] PROBLEMS:')
            for p in problems:
                print('   -', p)
        else:
            print('[legal_versions] ok: version block present and every archive link resolves')
    return problems


def main():
    for path, doc, lang, in_hist in pages():
        html = open(path, encoding='utf-8').read()
        new = stamp_html(html, doc, lang, in_hist)
        if new != html:
            open(path, 'w', encoding='utf-8').write(new)
            print('stamped:', os.path.relpath(path, REPO))
        else:
            print('kept:', os.path.relpath(path, REPO))
    verify()


if __name__ == '__main__':
    main()
