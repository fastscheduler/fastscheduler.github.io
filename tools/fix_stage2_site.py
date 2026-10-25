"""Stage 2 site fixes (Oct 14): contents pill always visible, cleaner contents
sheet, keep prev/next in fullscreen, legal mobile bar, jump menu trim, image
and link repairs.

Targets the published root tree (served at
https://fastscheduler.github.io/).
"""
import io, os, re, glob, sys

def rd(p):
    return io.open(p, encoding='utf-8', errors='replace').read()

def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='\n').write(s)

stats = {}

def bump(key, n=1):
    stats[key] = stats.get(key, 0) + n

# ---------------------------------------------------------------- blog articles
BLOG = sorted(glob.glob('blog/a/*.html'))
for f in BLOG:
    s = ord_s = rd(f)
    # 1. drop the Wide / Nav / Full mini controls from the contents sheet
    s = re.sub(r'<span class="blog-toc-mini">[\s\S]*?</span>', '', s)
    # 2. sheet: keep only the current article, not the neighbouring names
    s = re.sub(r'<a class="blog-toc-navc prev"[\s\S]*?</a>\s*', '', s)
    s = re.sub(r'<a class="blog-toc-navc next"[\s\S]*?</a>\s*', '', s)
    # 3. contents pill: visible without scrolling
    s = s.replace('if(!shown&&window.scrollY>420){shown=!0,fab.hidden=!1}', 'fab.hidden=!1')
    s = re.sub(r'<button class="blog-toc-fab"([^>]*?)\shidden', r'<button class="blog-toc-fab"\1', s)
    # 4. fullscreen keeps the prev/next pager
    s = re.sub(r'html\.blog-fs \.hc-pager, ?', '', s)
    if s != ord_s:
        wr(f, s)
        bump('blog articles patched')

# ------------------------------------------------------------------------- help
H = 'help.html'
s = ord_s = rd(H)
# sheet: current article only
s = re.sub(r'<span class="hc-toc-navc prev none">[\s\S]*?</span>\s*', '', s)
s = re.sub(r'<a class="hc-toc-navc (?:prev|next)[^>]*>[\s\S]*?</a>\s*', '', s)
# contents pill always visible (drop the scroll gate)
s = s.replace('window.scrollY>420', 'true')
# fullscreen keeps the prev/next pager
s = re.sub(r'html\.hc-fs \.hc-pager, ?', '', s)
if s != ord_s:
    wr(H, s)
    bump('help.html patched')

# static help article pages: contents pill/pager parity where present
for f in sorted(glob.glob('help/a/*.html')) + sorted(glob.glob('help/c/*.html')):
    s = ord_s = rd(f)
    s = s.replace('window.scrollY>420', 'true')
    s = re.sub(r'html\.hc-fs \.hc-pager, ?', '', s)
    if s != ord_s:
        wr(f, s)
        bump('help pages patched')

# ------------------------------------------------------------------ shared CSS
CSS = 'styles/main.css'
s = rd(CSS)
if '/* --- site fixes 2026-10-14 --- */' not in s:
    s += """
/* --- site fixes 2026-10-14 --- */
/* Fullscreen: hide the article path, not the prev/next pager (the reader keeps
   a way to walk to the next article). */
html.blog-fs .hc-crumbs, html.blog-fs .hc-toolbar .hc-crumbs,
html.hc-fs .hc-crumbs, html.hc-fs .hc-toolbar .hc-crumbs { display: none !important; }
/* The exit-fullscreen button follows the same rule as the jump button: it steps
   aside while the header is auto-hidden (scrolling down) so it never fights the
   article for the bottom of the screen. */
html.nav-hidden .fs-exit-fab.show { opacity: 0 !important; pointer-events: none !important; visibility: hidden !important; }
@media (max-width: 760px) {
  /* Legal pages: one Open-Bot button only (the bottom bar). The header kept a
     second one, and the bar itself was laid out in the page flow, which put it
     above the real bottom of the screen in Firefox. */
  body.legal header.site .nav-cta, body.legal header.site .nav-cta-sm,
  body.legal header.site .nav-cta-m { display: none !important; }
  body.legal .toc-bar { position: fixed; left: 0; right: 0; bottom: 0; top: auto;
    z-index: 95; transform: none; display: flex; align-items: center; gap: 10px; }
  body.legal .toc-bar .toc-burger { margin-left: auto; }
  /* the contents pill must not sit under the bar */
  body.legal main.legal { padding-bottom: calc(74px + env(safe-area-inset-bottom)); }
}
"""
    wr(CSS, s)
    bump('main.css appended')

# -------------------------------------------------------------- jump menu trim
J = 'scripts/scroll-jump.js'
s = ord_s = rd(J)
row_up = ('<button type="button" class="gp-row" role="menuitem" data-jump="pageup">'
          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
          'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
          '<polyline points="18 15 12 9 6 15"/></svg><span>Jump up a screen</span>'
          '<span class="tab-kbd">U</span></button>')
row_dn = ('<button type="button" class="gp-row" role="menuitem" data-jump="pagedown">'
          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
          'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
          '<polyline points="6 9 12 15 18 9"/></svg><span>Jump down a screen</span>'
          '<span class="tab-kbd">J</span></button>')
for row in (row_up, row_dn):
    if row in s:
        s = s.replace(row, '')
        bump('jump row removed')
if s != ord_s:
    wr(J, s)

# ------------------------------------------------------- missing blog cover art
imgs = set(os.path.basename(p) for p in glob.glob('blog/img/*'))
fixed_img = 0
for f in ['blog/index.html'] + BLOG:
    s = ord_s = rd(f)
    def rep(m):
        global fixed_img
        name = m.group(1)
        if name in imgs:
            return m.group(0)
        alt = os.path.splitext(name)[0]
        for ext in ('.svg', '.jpg', '.png'):
            if alt + ext in imgs:
                fixed_img += 1
                return m.group(0).replace(name, alt + ext)
        return m.group(0)
    pref = '../img/' if os.path.dirname(f) == 'blog/a' else 'img/'
    s = re.sub(re.escape(pref) + r'([A-Za-z0-9._-]+)', lambda m: rep(m), s)
    if s != ord_s:
        wr(f, s)
if fixed_img:
    bump('missing cover fixed', fixed_img)

# ------------------------------------------------------ RU home: relative links
R = 'ru/index.html'
s = ord_s = rd(R)
for name in ('blog/index.html', 'help.html', 'legal/privacy.html', 'legal/terms.html',
             'legal/refundpolicy.html'):
    s = s.replace('href="' + name + '"', 'href="../' + name + '"')
if s != ord_s:
    wr(R, s)
    bump('ru/index.html links fixed')

for k, v in sorted(stats.items()):
    print('%-28s %d' % (k, v))
