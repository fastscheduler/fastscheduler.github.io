"""Legal RU fragment pairs for the website language switcher.

Renders docs/*.md (EN) and docs/ru/*.md (RU) through the SAME markdown
pipeline website/_build/build_site.py uses (tables, fenced_code, nl2br,
toc + table-scroll wrap), splits both into text fragments in document
order, aligns them per <h2> section, and merges EN->RU pairs into
website/scripts/ru-content.js (preserving help/blog pairs).

lang.js applies these revert-safely on .doc scopes (exact nodes, 2-3
node windows for inline-tag splits, anchored substrings); archived
snapshots (.archived) are skipped by design.

Re-run after any legal text change:
    py -3 tools/build_ru_legal.py

Coverage goal: every EN fragment of the three current legal pages must
have an RU pair; sections whose fragment counts mismatch are reported
for manual fixing (usually a split/merged sentence or inline-tag drift
in docs/ru/*.md).
"""
import html as H
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    import markdown
except ImportError:
    print('need: py -3 -m pip install markdown')
    sys.exit(1)

DOCS = ['terms.md', 'privacy.md', 'refundpolicy.md']

# Lone title-nouns that need DIFFERENT Russian cases per sentence cannot
# share one whole-node key ('Privacy Policy' is nominative in h1/links but
# accusative in terms section 1, etc.). Titles are handled by scoped FIXUPs
# in ru-chrome.js; the sentences below are handled by multi-node window
# keys (lang.js pass 2), which require their neighbours to be keyless, so
# the listed neighbour fragments are deleted from the dict.
DELETE_KEYS = [
    'Privacy Policy',
    'Refund Policy',
    'These Terms incorporate our',
    'and, where you purchase a subscription, the refund terms in our',
    ', which is incorporated into these Terms by reference. See the',
]
WINDOW_KEYS = [
    # terms section 1: [pre + Privacy Policy + mid] 3-node window
    ('These Terms incorporate our Privacy Policy and, where you purchase '
     'a subscription, the refund terms in our',
     'Настоящие Условия включают нашу Политику конфиденциальности '
     'и, при покупке подписки, условия возврата из нашей'),
    # terms section 1: [Refund Policy + .] 2-node window (genitive)
    ('Refund Policy.',
     'Политики возвратов.'),
    # terms section 10: [Refund Policy + mid] 2-node window (instrumental)
    ('Refund Policy, which is incorporated into these Terms by reference. See the',
     'Политикой возвратов, включённой в настоящие Условия путём отсылки. '
     'Подробности см. в команде'),
]


def render(doc_path):
    with open(doc_path, encoding='utf-8-sig') as f:
        text = f.read()
    text = re.sub(r'\[\[([^\]]+)\]\]', r'<span data-ph="\1">[[\1]]</span>', text)
    out = markdown.markdown(text, extensions=['tables', 'fenced_code', 'nl2br', 'toc'])
    out = out.replace('<table>', '<div class="table-scroll"><table>')
    out = out.replace('</table>', '</table></div>')
    return out


def frags(html_text):
    """Same normalization as tools/build_ru_frag.py and lang.js normContent."""
    parts = re.split(r'<[^>]+>', html_text)
    out = []
    for p in parts:
        t = H.unescape(p)
        t = re.sub(r'\s+', ' ', t).strip()
        t = re.sub(r'([A-Za-z\u00c0-\u024f\u0400-\u04ff])(\d+\.)', r'\1 \2', t)
        t = re.sub(r'([.!?])([A-Z\u0410-\u042f\u0401])', r'\1 \2', t)
        if t:
            out.append(t)
    return out


def sections(html_text):
    """Split rendered HTML on <h2>: [(title, html)]."""
    idx = [m.start() for m in re.finditer(r'<h2[ >]', html_text)]
    bounds = [0] + idx + [len(html_text)]
    parts = []
    for i in range(len(bounds) - 1):
        chunk = html_text[bounds[i]:bounds[i + 1]]
        m = re.search(r'<h2[^>]*>(.*?)</h2>', chunk, re.S)
        title = re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else '(intro)'
        parts.append((title, chunk))
    return parts


def main():
    pairs = {}
    problems = []
    for doc in DOCS:
        en = render(os.path.join(REPO_ROOT, 'docs', doc))
        ru = render(os.path.join(REPO_ROOT, 'docs', 'ru', doc))
        en_sec = sections(en)
        ru_sec = sections(ru)
        if len(en_sec) != len(ru_sec):
            problems.append('%s: section count EN=%d RU=%d' % (doc, len(en_sec), len(ru_sec)))
            continue
        for (et, eh), (_rt, rh) in zip(en_sec, ru_sec):
            ef, rf = frags(eh), frags(rh)
            if len(ef) == len(rf):
                for a, b in zip(ef, rf):
                    if a != b and len(a) >= 2:
                        pairs[a] = b
            else:
                problems.append('%s [%s]: frag EN=%d RU=%d' % (doc, et, len(ef), len(rf)))
    print('new legal pairs:', len(pairs))
    if problems:
        print('MISMATCH (fix docs/ru then re-run):')
        for p in problems:
            print('  -', p)
    else:
        print('all sections aligned 1:1')
    # merge into existing dict (keep help/blog pairs)
    path = os.path.join(REPO_ROOT, 'website', 'scripts', 'ru-content.js')
    # The file is written with a trailing CRLF on Windows, and a rebuild that
    # assumed the semicolon was the very last character died with
    # "Extra data" instead of merging. Strip the wrapper explicitly.
    raw = open(path, encoding='utf-8').read().strip()
    assert raw.startswith('window.FS_RU_CONTENT='), 'unexpected ru-content.js format'
    payload = raw[len('window.FS_RU_CONTENT='):].strip()
    if payload.endswith(';'):
        payload = payload[:-1]
    cur = json.loads(payload)
    n0 = len(cur)
    cur.update(pairs)
    for k in DELETE_KEYS:
        cur.pop(k, None)
    for a, b in WINDOW_KEYS:
        if a in cur:
            assert cur[a] == b, 'window key changed: %r' % a[:60]
        else:
            cur[a] = b
    open(path, 'w', encoding='utf-8').write(
        'window.FS_RU_CONTENT=' + json.dumps(cur, ensure_ascii=False, separators=(',', ':')) + ';')
    print('ru-content.js: %d -> %d pairs' % (n0, len(cur)))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
