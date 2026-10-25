#!/usr/bin/env python3
"""Apply the new brand mark and favicon to every page, and the short mobile CTA.

The homepage got the new artwork by hand; this does the other 676 pages so the
site reads as one product:

  * <link rel="icon" data:image/svg+xml,...>  ->  the new PNG favicons
  * <span class="brand-mark"><svg .../></span> ->  <img src=".../brand-logo.png">
  * nav CTAs gain data-cta-short="Open" so the phone bar can print the short
    label (main.css zeroes the long text below 860px).

Paths are RELATIVE on purpose. The site is published at the domain root but
pages sit at different depths, so the prefix is computed from each file's
depth under website/, and
favicon-32.png / brand-logo.png therefore resolve correctly from blog/a/,
ru/help/a/ and every other depth.

Also patches _build/build_help.py, the only generator that emits these
strings, so a rebuild reproduces the same output.

    python tools/apply_brand.py           # apply
    python tools/apply_brand.py --check   # report only, exit 1 if work remains
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEBSITE = ROOT / "website"

ICON_LINKS = (
    '<link rel="icon" href="{p}favicon.ico" sizes="any">\n'
    '  <link rel="icon" href="{p}favicon.svg" type="image/svg+xml">\n'
    '  <link rel="icon" href="{p}favicon-32.png" sizes="32x32" type="image/png">\n'
    '  <link rel="icon" href="{p}icon-48.png" sizes="48x48" type="image/png">\n'
    '  <link rel="icon" href="{p}favicon-16.png" sizes="16x16" type="image/png">\n'
    '  <link rel="icon" href="{p}brand-logo.png" sizes="256x256" type="image/png">\n'
    '  <link rel="apple-touch-icon" href="{p}apple-touch-icon.png" sizes="180x180">\n'
    '  <link rel="manifest" href="{p}site.webmanifest">'
)

# The old inline SVG favicon, as a single link element.
OLD_FAVICON = re.compile(r'<link rel="icon" href="data:image/svg\+xml,[^"]*"[^>]*>')

# <span class="brand-mark"> containing only an <svg>.
BRAND_MARK = re.compile(r'<span class="brand-mark"[^>]*>\s*<svg\b.*?</svg>\s*</span>', re.S)

# Nav CTAs that still lack the short label. Inner pages emit
# class="btn btn-primary nav-cta", so match the token anywhere in class.
CTA = re.compile(r'<a class="([^"]*\bnav-cta(?:-sm|-m)?\b[^"]*)"(?![^>]*data-cta-short)')


def prefix_for(path: Path) -> str:
    """Relative prefix from `path` back to the website root."""
    depth = len(path.relative_to(WEBSITE).parts) - 1  # minus the filename
    return "../" * depth


def patch_html(text: str, prefix: str) -> tuple[str, int]:
    n = 0

    def fav(m: re.Match[str]) -> str:
        nonlocal n
        if "brand-logo.png" in m.group(0) or "favicon-32.png" in m.group(0):
            return m.group(0)
        n += 1
        return ICON_LINKS.format(p=prefix)

    text, had = OLD_FAVICON.subn(fav, text)

    def mark(m: re.Match[str]) -> str:
        nonlocal n
        if "<img" in m.group(0):
            return m.group(0)
        n += 1
        return (f'<span class="brand-mark"><img src="{prefix}brand-logo.png" alt="" '
                f'width="30" height="30" decoding="async"></span>')

    text = BRAND_MARK.sub(mark, text)

    def cta(m: re.Match[str]) -> str:
        nonlocal n
        n += 1
        return f'<a class="{m.group(1)}" data-cta-short="Open"'

    text = CTA.sub(cta, text)

    # The English legal pages shipped with no <link rel="icon"> at all. Give
    # them the brand favicon rather than leaving them on the browser default.
    # Test for the icon link specifically: these pages already reference
    # brand-logo.png from the header mark, which is not a favicon.
    if not had and 'rel="icon"' not in text and "</head>" in text:
        text = text.replace("</head>", ICON_LINKS.format(p=prefix) + "\n</head>", 1)
        n += 1

    return text, n


def pages() -> list[Path]:
    out: list[Path] = []
    for p in sorted(WEBSITE.rglob("*.html")):
        if "_build" in p.parts:
            continue
        out.append(p)
    return out


# ---- generator patches (build_help.py owns the only remaining copies) -------
HELP_FAVICON = re.compile(r'FAVICON = \("data:image/svg\+xml,.*?"\)\n', re.S)
HELP_MARK = re.compile(r'f\'<span class="brand-mark">\{svg\("calendar"\)\}</span>\'')


def patch_help(text: str) -> tuple[str, int]:
    n = 0
    if HELP_FAVICON.search(text):
        # build_help writes every page with an explicit relative prefix already
        # in scope as `rel`, so the links stay depth-correct.
        new = ('FAVICON = (\n'
               '    \'<link rel="icon" href="{rel}/favicon.ico" sizes="any">\\n\'\n'
               '    \'  <link rel="icon" href="{rel}/favicon.svg" type="image/svg+xml">\\n\'\n'
               '    \'<link rel="icon" href="{rel}/favicon-32.png" sizes="32x32" type="image/png">\\n\'\n'
               '    \'  <link rel="icon" href="{rel}/icon-48.png" sizes="48x48" type="image/png">\\n\'\n'
               '    \'  <link rel="icon" href="{rel}/favicon-16.png" sizes="16x16" type="image/png">\\n\'\n'
               '    \'  <link rel="icon" href="{rel}/brand-logo.png" sizes="256x256" type="image/png">\\n\'\n'
               '    \'  <link rel="apple-touch-icon" href="{rel}/apple-touch-icon.png" sizes="180x180">\\n\'\n'
               '    \'  <link rel="manifest" href="{rel}/site.webmanifest">\'\n'
               ')\n')
        text = HELP_FAVICON.sub(lambda m: new, text, count=1)
        n += 1
    if HELP_MARK.search(text):
        text = HELP_MARK.sub(
            'f\'<span class="brand-mark"><img src="{rel}/brand-logo.png" alt="" \'\n'
            '             f\'width="30" height="30" decoding="async"></span>\'', text, count=1)
        n += 1
    return text, n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    total = 0
    files: list[tuple[str, int]] = []

    for p in pages():
        text = p.read_text(encoding="utf-8", errors="replace")
        new, n = patch_html(text, prefix_for(p))
        if not n:
            continue
        if not args.check:
            p.write_text(new, encoding="utf-8", newline="")
        total += n
        files.append((str(p.relative_to(ROOT)), n))

    for gen in (ROOT / "_build" / "build_help.py", WEBSITE / "_build" / "build_help.py"):
        if not gen.is_file():
            continue
        text = gen.read_text(encoding="utf-8", errors="replace")
        new, n = patch_help(text)
        if not n:
            continue
        if not args.check:
            gen.write_text(new, encoding="utf-8", newline="")
        total += n
        files.append((str(gen.relative_to(ROOT)), n))

    if not files:
        print("brand already applied everywhere.", file=out)
        return 0
    verb = "would change" if args.check else "changed"
    print(f"{verb} {total} spot(s) in {len(files)} file(s):", file=out)
    for name, n in files[:8]:
        print(f"  {name} ({n})", file=out)
    if len(files) > 8:
        print(f"  ... and {len(files) - 8} more file(s)", file=out)
    if args.check:
        print("--check: work remains.", file=out)
        return 1
    print("done.", file=out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
