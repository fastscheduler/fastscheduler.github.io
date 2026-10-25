#!/usr/bin/env python3
"""Blog search via Ctrl/Cmd + K.

On the blog hub the search field sits inside the hero, so it scrolls out of
view; the site-wide handler then fell through to the navbar bar, which
navigates back to the same hub. Ctrl+K now always lands on the hub's own field
(bringing it back on screen) and the keycap advertises the shortcut.

Idempotent. Applies to both the source tree (website/) and the published
mirror at the repo root, plus the blog generator templates.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JS_OLD = """      if (SCOPE === 'blog') {
        var bq = document.getElementById('blog-q');
        if (bq && onScreen(bq)) { putCaret(bq); return; }
      }
"""

JS_NEW = """      if (SCOPE === 'blog') {
        /* The hub's own field wins even when it has scrolled away: it searches
           INTO this page's results view (topic filters included), while the
           nav bar would only navigate back to the same hub. Bring it on screen
           first, then focus it without a second scroll. */
        var bq = document.getElementById('blog-q');
        if (bq) {
          if (!onScreen(bq)) {
            try { bq.scrollIntoView({ block: 'center', behavior: 'smooth' }); }
            catch (err) { bq.scrollIntoView(); }
          }
          putCaret(bq);
          return;
        }
      }
"""

CARET_OLD = """  function putCaret(el) {
    try { el.focus({ preventScroll: true }); } catch (e) { try { el.focus(); } catch (e2) {} }
    try { var n = (el.value || '').length; el.setSelectionRange(n, n); } catch (e) {}
  }
"""

CARET_NEW = """  function putCaret(el) {
    try { el.focus({ preventScroll: true }); } catch (e) { try { el.focus(); } catch (e2) {} }
    /* Ctrl+K then typing should replace the old query, not append to it */
    try {
      if (el.value) { el.select(); return; }
      var n = (el.value || '').length; el.setSelectionRange(n, n);
    } catch (e) {}
  }
"""

KBD_OLD = '<kbd class="blog-search-kbd" aria-hidden="true">S</kbd>'
KBD_NEW = ('<kbd class="blog-search-kbd" aria-hidden="true" '
           'title="Ctrl + K">Ctrl K</kbd>')


def patch_text(path, pairs):
    with open(path, 'r', encoding='utf-8', newline='') as f:
        src = f.read()
    out = src
    changed = []
    for old, new in pairs:
        if new in out and old not in out:
            continue                     # already applied
        # tolerate CRLF files
        crlf_old = old.replace('\n', '\r\n')
        crlf_new = new.replace('\n', '\r\n')
        if crlf_old in out:
            out = out.replace(crlf_old, crlf_new, 1)
            changed.append('crlf')
        elif old in out:
            out = out.replace(old, new, 1)
            changed.append('lf')
    if out != src:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(out)
        return ','.join(changed)
    return ''


def main():
    js_targets = [
        os.path.join(ROOT, 'scripts', 'help-search.js'),
        os.path.join(ROOT, 'website', 'scripts', 'help-search.js'),
    ]
    for p in js_targets:
        r = patch_text(p, [(JS_OLD, JS_NEW), (CARET_OLD, CARET_NEW)])
        print(('patched  ' if r else 'unchanged') + ' ' + os.path.relpath(p, ROOT))

    kbd_targets = [
        os.path.join(ROOT, 'blog', 'index.html'),
        os.path.join(ROOT, 'website', 'blog', 'index.html'),
        os.path.join(ROOT, '_build', 'build_blog.py'),
        os.path.join(ROOT, 'website', '_build', 'build_blog.py'),
    ]
    for p in kbd_targets:
        if not os.path.exists(p):
            print('missing   ' + os.path.relpath(p, ROOT))
            continue
        r = patch_text(p, [(KBD_OLD, KBD_NEW)])
        print(('patched  ' if r else 'unchanged') + ' ' + os.path.relpath(p, ROOT))

    # cache-bust every page that loads help-search.js
    n = 0
    for base, _dirs, files in os.walk(ROOT):
        if os.sep + '.git' in base:
            continue
        for fn in files:
            if not fn.endswith('.html'):
                continue
            p = os.path.join(base, fn)
            try:
                with open(p, 'r', encoding='utf-8', newline='') as f:
                    s = f.read()
            except (OSError, UnicodeDecodeError):
                continue
            t = s.replace('help-search.js?v=20261022a3', 'help-search.js?v=20261025a1')
            if t != s:
                with open(p, 'w', encoding='utf-8', newline='') as f:
                    f.write(t)
                n += 1
    print('version-bumped html files:', n)


if __name__ == '__main__':
    main()
