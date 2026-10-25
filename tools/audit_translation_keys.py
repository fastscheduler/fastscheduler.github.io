"""Conservative translation-key audit for Fast Scheduler.

Classifies every flat key in translations/en.json (and translations/admin/en.json)
as USED or UNUSED, and reports code-referenced keys that are missing.

Anchored on `find_missing_translations.py` (the project's own key extractor) but
deliberately biased toward RETENTION: a key is only reported UNUSED when it is
unreferenced under *all* of the following checks, so a dynamic lookup can never
cause a live key to be deleted.

    1. literal  t()/t_safe()/_t()  key argument            (AST)
    2. any string literal appearing inside a dynamic call  (ternaries, dicts)
    3. dynamic f-string family prefix, e.g. f'stats_metric_{m}' -> 'stats_metric_'
    4. the exact key string appearing anywhere in src/ source text
    5. the key's final '_' segment appearing as a string literal anywhere in src/

Checks 4 and 5 are intentionally blunt: they over-retain (e.g. the weekday names
looked up via `day_key`) rather than risk deleting a key the bot resolves at
runtime. `--json` emits a machine-readable report.

Usage:
    python tools/audit_translation_keys.py             # human summary
    python tools/audit_translation_keys.py --show 80   # print first 80 unused
"""
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
EN = ROOT / "translations" / "en.json"
ADMIN_EN = ROOT / "translations" / "admin" / "en.json"
EXCLUDED_PARTS = {"tests", "migrations", "for_agents", "__pycache__"}
EXCLUDED_FILES = {SRC / "core" / "i18n.py"}
CALL_NAMES = {"t", "_t", "t_safe"}
# Families resolved at runtime by iterating translation sections or bounded
# callback-data domains — every key under these prefixes is live by construction:
#   help.*      HELP_TREE is built from en['help'] dict-nodes (keyboards.py)
#   tips.cmd.*  COMMAND_MAP iterates en keys with this prefix (services/tips.py)
PROTECTED_PREFIXES = ("help.", "tips.cmd.")


def flat(d, p=""):
    out = {}
    for k, v in d.items():
        kk = f"{p}.{k}" if p else k
        if isinstance(v, dict):
            out.update(flat(v, kk))
        elif isinstance(v, str):
            out[kk] = v
    return out


def _is_key_arg(node):
    """Literal string key in arg position (arg 1 for t/t_safe, arg 1 here too)."""
    return isinstance(node, ast.Constant) and isinstance(node.value, str)


def scan():
    """Return (literal_keys, dynamic_prefixes, all_literals, dynamic_sites)."""
    literal, prefixes, all_lits, sites = set(), set(), set(), []
    for path in sorted(SRC.rglob("*.py")):
        if any(p in EXCLUDED_PARTS for p in path.parts):
            continue
        if path.resolve() in {p.resolve() for p in EXCLUDED_FILES}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text)
        except Exception:
            continue
        rel = path.relative_to(ROOT).as_posix()
        for n in ast.walk(tree):
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                all_lits.add(n.value)
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            if not (isinstance(f, ast.Name) and f.id in CALL_NAMES):
                continue
            args = n.args
            nargs = len(args)
            keynode = None
            if f.id == "t_safe":
                for kw in n.keywords:                      # t_safe(key='x')
                    if kw.arg == "key":
                        keynode = kw.value
                if keynode is None and nargs >= 1:
                    keynode = args[0]
            else:
                if nargs >= 2:
                    keynode = args[1]
                elif nargs == 1:
                    keynode = args[0]
            if keynode is None:
                continue
            if _is_key_arg(keynode):
                literal.add(keynode.value)
                continue
            # dynamic: harvest every literal in the expression, plus f-string prefix
            for sub in ast.walk(keynode):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                    literal.add(sub.value)
                if isinstance(sub, ast.JoinedStr):
                    lead = ""
                    for part in sub.values:
                        if isinstance(part, ast.Constant) and isinstance(part.value, str):
                            lead += part.value
                        else:
                            break
                    if lead and lead.endswith(("_", ".")):
                        prefixes.add(lead)
            sites.append((rel, n.lineno,
                          (ast.get_source_segment(text, n) or "?").replace("\n", " ")[:120]))
    return literal, prefixes, all_lits, sites


def scan_tests_literals():
    """Literal t() keys referenced anywhere under tests/ — never delete those."""
    found = set()
    tdir = ROOT / "tests"
    if not tdir.exists():
        return found
    for path in tdir.rglob("*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            if not (isinstance(f, ast.Name) and f.id in CALL_NAMES):
                continue
            for arg in list(n.args) + [kw.value for kw in n.keywords]:
                for sub in ast.walk(arg):
                    if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                        if re.fullmatch(r"[A-Za-z0-9_.]+", sub.value):
                            found.add(sub.value)
    return found


def expand_literal(literal):
    """Literal refs plus every nested path the runtime underscore-split
    fallback can resolve them to: t('plan_monthly_3') -> 'plan.monthly_3'."""
    out = set(literal)
    for r in literal:
        if "_" in r and not r.startswith("__") and "." not in r:
            first, rest = r.split("_", 1)
            out.add(f"{first}.{rest}")
    return out


def classify(keys, literal, prefixes, all_lits, src_text, expanded):
    used, unused = {}, []
    for k in keys:
        reasons = []
        if k.startswith(PROTECTED_PREFIXES):
            reasons.append("protected family")
        if k in literal:
            reasons.append("literal t()")
        if any(k.startswith(p) for p in prefixes):
            reasons.append("dynamic family")
        if k in src_text:
            reasons.append("key text in src")
        last = k.split(".")[-1].split("_")[-1]
        if last and len(last) > 2 and last in all_lits:
            reasons.append(f"segment '{last}' literal in src")
        # dotted keys are resolved by the i18n underscore-split fallback too
        if "." in k and k.replace(".", "_") in literal:
            reasons.append("underscore-split form used")
        # ...and flat keys resolve into nested dicts via the same fallback:
        # t('plan_monthly_3') reads dict['plan']['monthly_3'] (runtime _resolve).
        if k in expanded:
            reasons.append("flat form resolves to nested path")
        if reasons:
            used[k] = reasons
        else:
            unused.append(k)
    return used, unused


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    en = json.loads(EN.read_text(encoding="utf-8-sig"))
    admin = json.loads(ADMIN_EN.read_text(encoding="utf-8-sig")) if ADMIN_EN.exists() else {}
    fe, fa = flat(en), flat(admin)

    literal, prefixes, all_lits, sites = scan()
    literal |= scan_tests_literals()
    src_text = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in SRC.rglob("*.py")
        if not any(x in EXCLUDED_PARTS for x in p.parts)
    )

    ru_keys = flatten_paths(ROOT / "translations" / "ru.json")

    expanded = expand_literal(literal)
    groups = {}
    for name, keys in (("main", fe), ("admin", fa)):
        used, unused = classify(set(keys), literal, prefixes, all_lits, src_text, expanded)
        groups[name] = {"total": len(keys), "used": len(used), "unused": unused}

    referenced = (literal | {k for k in literal}
                  | {k for k in fe if any(k.startswith(p) for p in prefixes)})
    referenced |= {k for k in fe if k in src_text}
    missing_main = sorted(k for k in referenced
                          if k in literal and k not in fe and k not in fa
                          and not k.startswith("admin_") and not looks_admin(k, sites))
    missing_admin = sorted(k for k in literal if k not in fe and k not in fa
                           and (k.startswith("admin_") or looks_admin(k, sites)))

    report = {
        "main": {"total": groups["main"]["total"], "used": groups["main"]["used"],
                 "unused_count": len(groups["main"]["unused"]),
                 "unused": groups["main"]["unused"]},
        "admin": {"total": groups["admin"]["total"], "used": groups["admin"]["used"],
                  "unused_count": len(groups["admin"]["unused"]),
                  "unused": groups["admin"]["unused"]},
        "dynamic_prefixes": sorted(prefixes),
        "dynamic_sites": len(sites),
        "missing_literal_keys": {"main": missing_main, "admin": missing_admin},
        "ru_leaf_count": len(ru_keys),
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return
    for name in ("main", "admin"):
        g = groups[name]
        print(f"{name:5s} en.json: {g['total']} keys | used {g['used']} | UNUSED {len(g['unused'])}")
    print(f"dynamic families: {len(prefixes)}  | dynamic call sites: {len(sites)}")
    print("prefixes:", ", ".join(sorted(prefixes))[:600])
    if groups["main"]["unused"] or groups["admin"]["unused"]:
        print("\nunused (main):", ", ".join(groups["main"]["unused"][:args.show or 30]))
        print("unused (admin):", ", ".join(groups["admin"]["unused"][:args.show or 30]))


def flatten_paths(p: Path):
    if not p.exists():
        return []
    return list(flat(json.loads(p.read_text(encoding="utf-8"))).keys())


def looks_admin(key, sites):
    hits = [s for s in sites if key in s[2]]
    return bool(hits) and all("admin" in h[0] for h in hits)


if __name__ == "__main__":
    main()
