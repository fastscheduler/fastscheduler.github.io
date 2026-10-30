"""Make the support-CTA subtitle readable on its green strip.

The help pages ship two `.hc-cta` blocks in one document: the tinted strip used
by the hub (`color: var(--text-dim)` subtitle) and the solid green strip used by
articles. The green block wins the cascade, so the hub's subtitle was painted in
`--text-dim` on top of dark green - grey on green.

styles/main.css already overrides it with `.hc-cta.hc-cta ...`; this bakes the
fix into the inline stylesheet too, so the strip stays readable even when the
external sheet is cached, blocked or not yet loaded.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OLD = ".hc-cta-t span { color: var(--text-dim); font-size: .88rem; }"
NEW = ".hc-cta-t span { color: rgba(255, 255, 255, .92); font-size: .88rem; }"

TARGETS = [ROOT / "help", ROOT / "help.html", ROOT / "ru", ROOT / "website"]

changed = 0
for target in TARGETS:
    if not target.exists():
        continue
    files = [target] if target.is_file() else list(target.rglob("*.html"))
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if OLD not in text:
            continue
        f.write_text(text.replace(OLD, NEW), encoding="utf-8")
        changed += 1

# keep the generators in sync so a rebuild does not undo the fix
for gen in (ROOT / "website" / "_build" / "build_help.py",
            ROOT / "website" / "_build" / "_hc_component_css.txt"):
    if not gen.exists():
        continue
    text = gen.read_text(encoding="utf-8")
    if OLD in text:
        gen.write_text(text.replace(OLD, NEW), encoding="utf-8")
        changed += 1

print(f"patched {changed} files")
