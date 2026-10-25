"""Publish the shared site footer to every page and prune a help section.

Run from the repo root:

    python tools/apply_site_footer.py

What it does (idempotent):

1. Adds <script src=".../scripts/site-footer.js"> before </body> on every
   HTML page under website/ (the source tree). scripts/site-footer.js renders
   the brand footer at runtime, so one file drives every page.
2. Removes the redundant "Every help article, by topic" section
   (<section class="hc-index">) from website/help.html.

The repo-root deploy tree is refreshed afterwards with tools/sync_root.py.
"""
from __future__ import annotations

import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEBSITE = os.path.join(REPO, 'website')
FOOTER_VER = '20261018g2'
FOOTER_TAG_RE = re.compile(r'site-footer\.js')


def prefix_for(path: str) -> str:
    """Relative prefix from a page back to the site root, e.g. '../../'."""
    rel = os.path.relpath(WEBSITE, os.path.dirname(path))
    if rel == '.':
        return ''
    return rel.replace(os.sep, '/') + '/'


def add_footer_script(path: str, html: str) -> tuple[str, bool]:
    if FOOTER_TAG_RE.search(html):
        return html, False
    # 404 pages are served for arbitrary URLs, so a relative script path would
    # resolve against the (nonexistent) requested path. Use a root-absolute one.
    if os.path.basename(path) == '404.html':
        src = '/scripts/site-footer.js'
    else:
        src = prefix_for(path) + 'scripts/site-footer.js'
    tag = f'<script src="{src}?v={FOOTER_VER}"></script>'
    idx = html.rfind('</body>')
    if idx == -1:
        return html, False
    html = html[:idx] + tag + '\n' + html[idx:]
    return html, True


def strip_hc_index(html: str) -> tuple[str, bool]:
    start = html.find('<section class="hc-index"')
    if start == -1:
        return html, False
    end = html.find('</section>', start)
    if end == -1:
        return html, False
    # Walk nested <section> so we close the outer one, not the first child.
    depth = 0
    pos = start
    while True:
        nxt_open = html.find('<section', pos)
        nxt_close = html.find('</section>', pos)
        if nxt_open != -1 and nxt_open < nxt_close:
            depth += 1
            pos = nxt_open + len('<section')
        else:
            depth -= 1
            pos = nxt_close + len('</section>')
            if depth == 0:
                end = pos
                break
    # Trim surrounding blank lines.
    out = html[:start].rstrip() + '\n' + html[end:].lstrip('\n')
    return out, True


def main() -> None:
    changed = added = pruned = 0
    for dp, dn, fn in os.walk(WEBSITE):
        dn[:] = [d for d in dn if d not in ('_build', '__pycache__')]
        for name in fn:
            if not name.endswith('.html'):
                continue
            path = os.path.join(dp, name)
            with io.open(path, encoding='utf-8') as fh:
                html = fh.read()
            new, did_add = add_footer_script(path, html)
            if name == 'help.html' and os.path.dirname(path) == WEBSITE:
                new, did_prune = strip_hc_index(new)
                pruned += int(did_prune)
            else:
                did_prune = False
            if did_add or did_prune:
                with io.open(path, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(new)
                changed += 1
                added += int(did_add)
    print(f'pages updated: {changed}  footer tags added: {added}  hc-index removed: {pruned}')


if __name__ == '__main__':
    main()
