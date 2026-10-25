# -*- coding: utf-8 -*-
"""Strip help-link markers from FAQ JSON-LD answers.

Article bodies use the [[article_id|Label]] marker (see HELP_LINK_RE in
build_help.py); every renderer is supposed to resolve it. The FAQPage JSON-LD
builder did not, so a question whose answer pointed at another article shipped
literal "[[" text into the structured data Google reads — invisible on the page,
visible to the crawler, and a warning in Rich Results.

This patch applies plain_links() (the helper that exists for exactly this:
"marker-free copy for search snippets, meta descriptions and llms.txt") before
the tag strip, in both copies of the builder. Idempotent: a second run reports
"already patched" and writes nothing.

    python tools/patch_faq_ld_links.py            # apply
    python tools/patch_faq_ld_links.py --check     # report only
"""

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TARGETS = (
    os.path.join(ROOT, 'website', '_build', 'build_help.py'),
    os.path.join(ROOT, '_build', 'build_help.py'),
)

OLD = """    ents = []
    for f in n['faq']:
        a = ' '.join(re.sub(r'<[^>]+>', ' ', f['a']).split())
        ents.append({'@type': 'Question', 'name': ' '.join(re.sub(r'<[^>]+>', ' ', f['q']).split()),
                     'acceptedAnswer': {'@type': 'Answer', 'text': a}})
"""

NEW = """    ents = []
    for f in n['faq']:
        # Wiki links ([[id|Label]]) must be resolved before the tags are
        # stripped: an unresolved marker is invisible on the page but ships
        # straight into the FAQPage JSON-LD that Google reads.
        a = ' '.join(re.sub(r'<[^>]+>', ' ', plain_links(f['a'])).split())
        ents.append({'@type': 'Question', 'name': ' '.join(re.sub(r'<[^>]+>', ' ', plain_links(f['q'])).split()),
                     'acceptedAnswer': {'@type': 'Answer', 'text': a}})
"""

MARKER = "plain_links(f['a'])"


def main(argv):
    check_only = '--check' in argv
    problems = []
    for path in TARGETS:
        if not os.path.exists(path):
            problems.append('missing file: %s' % os.path.relpath(path, ROOT))
            continue
        with io.open(path, encoding='utf-8') as f:
            src = f.read()
        if MARKER in src:
            print('%s: already patched' % os.path.relpath(path, ROOT))
            continue
        if OLD not in src:
            problems.append('%s: marker block not found (builder changed?)' % os.path.relpath(path, ROOT))
            continue
        if check_only:
            print('%s: would patch' % os.path.relpath(path, ROOT))
            continue
        with io.open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(src.replace(OLD, NEW, 1))
        print('%s: patched' % os.path.relpath(path, ROOT))
    if problems:
        for p in problems:
            print('  !', p)
        raise SystemExit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
