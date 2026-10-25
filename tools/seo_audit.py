#!/usr/bin/env python
"""Static SEO audit for the website/ tree.

Reports per-page metadata problems and site-wide summary counts so SEO
regressions in the generated pages are visible without a crawler.

Usage:  python tools/seo_audit.py [--root website] [--json out.json]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

SKIP_DIRS = {"_build", "styles", "scripts", "fonts", "img", "images", ".git"}


def get1(s: str, pat: str):
    m = re.search(pat, s, re.I | re.S)
    return m.group(1).strip() if m else None


def html_pages(root: str):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".html"):
                p = os.path.join(base, f)
                yield os.path.relpath(p, root).replace(os.sep, "/")


def audit(root: str):
    rows = []
    for p in sorted(html_pages(root)):
        s = open(os.path.join(root, p), encoding="utf-8", errors="replace").read()
        close = s.lower().find("</head>")
        head = s[:close] if close > 0 else s[:20000]
        title = get1(head, r"<title>(.*?)</title>")
        desc = get1(head, r'<meta\s+name="description"\s+content="(.*?)"')
        canon = get1(head, r'<link\s+rel="canonical"\s+href="(.*?)"')
        robots = get1(head, r'<meta\s+name="robots"\s+content="(.*?)"')
        h1 = re.findall(r"<h1[^>]*>", s, re.I)
        lang = get1(s[:600], r'<html[^>]*\blang="([^"]+)"')
        ld = len(re.findall(r"application/ld\+json", head))
        hreflang = re.findall(r'hreflang="([^"]+)"', head)
        imgs = re.findall(r"<img\b[^>]*>", s, re.I)
        noalt = sum(1 for i in imgs if not re.search(r"\balt=", i, re.I))
        emptya = sum(1 for i in imgs if re.search(r'\balt=""', i, re.I))
        rows.append(dict(
            page=p, title=title, title_len=len(title or ""), desc=desc,
            desc_len=len(desc or ""), canon=canon, robots=robots, h1=len(h1),
            lang=lang, ld=ld, hreflang=hreflang, imgs=len(imgs), noalt=noalt,
            emptya=emptya, bytes=len(s.encode("utf-8")),
        ))
    return rows


def report(rows, root: str, verbose: bool = False):
    issues = collections.Counter()
    detail = collections.defaultdict(list)

    def add(key, page):
        issues[key] += 1
        if len(detail[key]) < 6:
            detail[key].append(page)

    # Pages that ask not to be indexed are not expected to carry indexing
    # metadata, and duplicates among them are by design (the archived legal
    # revisions deliberately share a canonical with the current document).
    # Counting them as failures buried the real signal, so they are reported
    # separately.
    blocked = [r for r in rows if r["robots"] and "noindex" in r["robots"]]
    live = [r for r in rows if r not in blocked]
    hl_missing = 0

    for r in live:
        if not r["title"]:
            add("no <title>", r["page"])
        if not r["desc"]:
            add("no meta description", r["page"])
        if not r["canon"]:
            add("no canonical", r["page"])
        if r["robots"] and "index" not in r["robots"]:
            add("robots meta blocks indexing", r["page"])
        if r["h1"] != 1:
            add("h1 count != 1 (%d)" % r["h1"], r["page"])
        if r["ld"] == 0:
            add("no JSON-LD", r["page"])
        if r["noalt"]:
            add("img without alt", r["page"])
        if r["emptya"]:
            add('img alt=""', r["page"])
        if r["desc_len"] and not (70 <= r["desc_len"] <= 160):
            add("meta description length outside 70-160", r["page"])
        if r["title_len"] and not (30 <= r["title_len"] <= 65):
            add("title length outside 30-65", r["page"])
        if r["canon"] and "fastscheduler.github.io" not in r["canon"]:
            add("canonical off-domain", r["page"])
        if not r["hreflang"]:
            # Informational, not a defect. hreflang is only correct when two
            # URLs are genuinely different localized documents; the Russian
            # layer is a client-side translation of the same URL, so
            # advertising alternates would claim two pages that are one.
            hl_missing += 1

    tcount = collections.Counter(r["title"] for r in live if r["title"])
    dups = [(t, n) for t, n in tcount.items() if n > 1]
    dcount = collections.Counter(r["desc"] for r in live if r["desc"])
    ddups = [(d, n) for d, n in dcount.items() if n > 1]
    ccount = collections.Counter(r["canon"] for r in live if r["canon"])
    cdups = [(c, n) for c, n in ccount.items() if n > 1]
    bcount = collections.Counter(r["canon"] or "(none)" for r in blocked)

    print("=== %s : %d HTML pages ===" % (root, len(rows)))
    print("\n-- issues --")
    if not issues:
        print("none")
    for k, n in issues.most_common():
        print("%-42s %4d   e.g. %s" % (k, n, ", ".join(detail[k])))
    print("\n-- duplicates (indexable pages only) --")
    print("noindex pages excluded: %d  %s" % (
        len(blocked), ", ".join(r["page"] for r in blocked[:6])))
    print("duplicate titles: %d" % len(dups))
    for t, n in dups[:8]:
        print("   %dx %s" % (n, t[:88]))
    print("duplicate descriptions: %d" % len(ddups))
    for d, n in ddups[:8]:
        print("   %dx %s" % (n, (d or "")[:88]))
    print("duplicate canonicals: %d" % len(cdups))
    for c, n in cdups[:8]:
        print("   %dx %s" % (n, c))
    print("\n-- distributions --")
    print("html lang:", dict(collections.Counter(r["lang"] for r in rows)))
    print("indexable pages: %d   noindex pages: %d" % (len(live), len(blocked)))
    if hl_missing:
        print("no hreflang alternates: %d of %d pages (informational -- the site "
              "has one language URL; see docs/SEO_REPORT.md for the /ru/ plan)"
              % (hl_missing, len(live)))
    print("bytes: max %d  avg %d  total %.1f MB" % (
        max(r["bytes"] for r in rows),
        int(sum(r["bytes"] for r in rows) / max(1, len(rows))),
        sum(r["bytes"] for r in rows) / 1048576.0))
    heavy = sorted(rows, key=lambda r: -r["bytes"])[:8]
    print("heaviest pages:")
    for r in heavy:
        print("   %8.1f KB  %s" % (r["bytes"] / 1024.0, r["page"]))
    if verbose:
        print("\n-- every page --")
        for r in rows:
            print("%-58s t=%3d d=%3d h1=%d ld=%d hl=%s %6.1fKB" % (
                r["page"], r["title_len"], r["desc_len"], r["h1"], r["ld"],
                len(r["hreflang"]), r["bytes"] / 1024.0))
    return issues, dups, ddups, cdups


def main():
    # Titles now include Cyrillic (the /ru/ pages), which the Windows console
    # (cp1252) cannot encode -- printing one used to abort the whole report.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="website")
    ap.add_argument("--json")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    rows = audit(a.root)
    report(rows, a.root, a.verbose)
    if a.json:
        json.dump(rows, open(a.json, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("\nwrote %s" % a.json)


if __name__ == "__main__":
    main()
