#!/usr/bin/env python
"""Ad-hoc SEO diagnostics: sitemap coverage, image attributes, price claims."""
from __future__ import annotations

import os
import re
import collections

ROOT = "website"
SITEMAP = os.path.join(ROOT, "sitemap.xml")
BASE = "https://fastscheduler.github.io/"


def html_pages():
    out = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in
                   ("_build", "styles", "scripts", "fonts", "img", "images", ".git")]
        for f in files:
            if f.endswith(".html"):
                out.append(os.path.join(base, f).replace(os.sep, "/")[len(ROOT) + 1:])
    return sorted(out)


def url_for(rel):
    if rel == "index.html":
        return BASE
    if rel.endswith("/index.html"):
        return BASE + rel[:-len("index.html")]
    return BASE + rel


def main():
    pages = html_pages()
    sm = open(SITEMAP, encoding="utf-8").read()
    locs = re.findall(r"<loc>(.*?)</loc>", sm)
    locset = set(locs)
    print("pages: %d   sitemap <loc>: %d   unique: %d" % (len(pages), len(locs), len(locset)))

    missing, extra = [], []
    for p in pages:
        u = url_for(p)
        if u not in locset:
            missing.append(p)
    for u in sorted(locset):
    # anything in the sitemap with no file on disk
        tail = u[len(BASE):] if u.startswith(BASE) else u
        cand = tail + "index.html" if tail.endswith("/") else tail
        if cand not in pages:
            extra.append(u)
    print("\n-- in sitemap but no file (%d) --" % len(extra))
    for u in extra[:20]:
        print("  ", u)
    print("\n-- file but not in sitemap (%d) --" % len(missing))
    for p in missing[:40]:
        print("  ", p)

    # sitemap lastmod spread
    lm = re.findall(r"<lastmod>(.*?)</lastmod>", sm)
    print("\n-- sitemap lastmod spread --", dict(collections.Counter(lm).most_common(6)))
    print("priority values:", dict(collections.Counter(re.findall(r"<priority>(.*?)</priority>", sm))))

    # image attributes across article pages
    no_dims = nolazy = noalt = webp = 0
    tot = 0
    fmts = collections.Counter()
    for p in pages:
        if "/a/" not in p and not p.startswith("blog/index"):
            continue
        s = open(os.path.join(ROOT, p), encoding="utf-8").read()
        for tag in re.findall(r"<img\b[^>]*>", s, re.I):
            tot += 1
            src = re.search(r'src="([^"]+)"', tag)
            if src:
                fmts[os.path.splitext(src.group(1))[1].lower()] += 1
                if src.group(1).lower().endswith(".webp"):
                    webp += 1
            if not re.search(r"\bwidth=", tag) or not re.search(r"\bheight=", tag):
                no_dims += 1
            if 'loading="lazy"' not in tag:
                nolazy += 1
            if not re.search(r"\balt=", tag):
                noalt += 1
    print("\n-- images on article/hub pages: %d --" % tot)
    print("no width/height: %d   no loading=lazy: %d   no alt: %d   webp: %d" % (no_dims, nolazy, noalt, webp))
    print("formats:", dict(fmts))

    # headings
    for p in ["website/help.html", "website/blog/index.html", "website/help/a/formatting.html"]:
        s = open(p, encoding="utf-8").read()
        print("\n%s: h1=%d h2=%d h3=%d  (h1 samples: %s)" % (
            p,
            len(re.findall(r"<h1\b", s, re.I)), len(re.findall(r"<h2\b", s, re.I)),
            len(re.findall(r"<h3\b", s, re.I)),
            " | ".join(re.findall(r"<h1[^>]*>(.*?)</h1>", s, re.I | re.S)[:3])[:160]))

    # price claims
    s = open("website/index.html", encoding="utf-8").read()
    print("\n-- price strings on index.html --")
    for m in set(re.findall(r"\$\s?\d+(?:\.\d+)?", s)):
        print("  ", m)
    s2 = open("website/legal/privacy.html", encoding="utf-8").read()
    print("-- price strings on legal/privacy.html --", sorted(set(re.findall(r"\$\s?\d+(?:\.\d+)?", s2))))
    s3 = open("website/help/a/premium_plans.html", encoding="utf-8").read() if os.path.exists("website/help/a/premium_plans.html") else ""
    if s3:
        print("-- price strings on help premium page --", sorted(set(re.findall(r"\$\s?\d+(?:\.\d+)?", s3))))


if __name__ == "__main__":
    main()
