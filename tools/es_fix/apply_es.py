"""Apply Spanish translation batches to translations/es.json.

Usage: python tools/es_fix/apply_es.py
Reads tools/es_fix/batch_*.json ({dotted.key: spanish}), sets nested values,
validates {placeholder} parity with en.json, writes es.json back.
"""
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ES_PATH = os.path.join(ROOT, "translations", "es.json")
EN_PATH = os.path.join(ROOT, "translations", "en.json")
BATCH_GLOB = os.path.join(ROOT, "tools", "es_fix", "batch_*.json")


def flat(d, p=""):
    out = {}
    for k, v in d.items():
        kk = p + "." + k if p else k
        if isinstance(v, dict):
            out.update(flat(v, kk))
        elif isinstance(v, str):
            out[kk] = v
    return out


def set_nested(d, dotted, value):
    parts = dotted.split(".")
    cur = d
    for p in parts[:-1]:
        nxt = cur.get(p)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[p] = nxt
        cur = nxt
    cur[parts[-1]] = value


def placeholders(s):
    return sorted(set(re.findall(r"\{[^}]*\}", s or "")))


def main():
    with io.open(EN_PATH, encoding="utf-8") as f:
        en = json.load(f)
    with io.open(ES_PATH, encoding="utf-8") as f:
        es = json.load(f)
    en_flat = flat(en)

    batches = sorted(glob.glob(BATCH_GLOB))
    if not batches:
        print("no batches found")
        return 1
    total = 0
    errors = []
    for path in batches:
        with io.open(path, encoding="utf-8") as f:
            batch = json.load(f)
        for key, val in batch.items():
            if not isinstance(val, str) or not val.strip():
                errors.append(f"{path}: empty value for {key}")
                continue
            if "Guia en espanol" in val:
                errors.append(f"{path}: Guia residue in {key}")
                continue
            ref = en_flat.get(key)
            if ref is not None and placeholders(ref) != placeholders(val):
                errors.append(
                    f"{path}: placeholder mismatch {key}: "
                    f"en={placeholders(ref)} es={placeholders(val)}")
                continue
            set_nested(es, key, val)
            total += 1
    with io.open(ES_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(es, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"applied {total} keys from {len(batches)} batches")
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors[:50]:
            print("  " + e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
