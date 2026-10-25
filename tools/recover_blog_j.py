# -*- coding: utf-8 -*-
"""Rebuild the two blog source records that lived in website/_build/blog_articles_j.py.

That directory is gitignored, and the file was accidentally overwritten while
adding a new batch, so the only surviving copy of the prose is the generated
page. This extracts title, description, date, category, body HTML and FAQ from
website/blog/a/<id>/index.html and writes a normal `_a(...)` source file.

Run from the repo root:

    python tools/recover_blog_j.py            # writes _build/blog_articles_j.py
    python tools/recover_blog_j.py --check    # prints what would be written
"""

import html
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDS = ['october-2026-legal-refresh', 'media-storage-premium-toolkit']
OUT = os.path.join(ROOT, '_build', 'blog_articles_j.py')

SECTION_TO_ID = {
    'Growth': 'growth',
    'Content': 'content',
    'Bots & Tools': 'tools',
    'Platform': 'platform',
    'Premium & Safety': 'premium',
    'Monetization': 'money',
    'Releases': 'releases',
    'Updates': 'updates',
    'Company': 'company',
}

MONTHS = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
    'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11,
    'December': 12,
}


def read(path):
    with io.open(path, encoding='utf-8') as f:
        return f.read()


def cut_inner(page, start_marker, end_marker):
    start = page.find(start_marker)
    if start < 0:
        return ''
    start = page.find('>', start) + 1
    end = page.find(end_marker, start)
    if end < 0:
        return ''
    return page[start:end]


def extract(article_id):
    page = read(os.path.join(ROOT, 'website', 'blog', 'a', article_id, 'index.html'))

    title = html.unescape(re.search(r'<h1>(.*?)</h1>', page, re.S).group(1)).strip()

    desc_m = re.search(r'<meta name="description" content="([^"]*)"', page)
    description = html.unescape(desc_m.group(1)).strip() if desc_m else ''

    date = ''
    by_m = re.search(r'class="blog-byline">([A-Z][a-z]+) (\d+), (\d{4})', page)
    if by_m:
        date = '%s-%02d-%02d' % (by_m.group(3), MONTHS[by_m.group(1)], int(by_m.group(2)))

    category = ''
    cat_m = re.search(r'"articleSection"\s*:\s*"([^"]+)"', page)
    if cat_m:
        category = SECTION_TO_ID.get(cat_m.group(1).strip(), '')
        if not category:
            category = cat_m.group(1).strip().lower().replace(' & ', '-').replace(' ', '-')

    body = cut_inner(page, '<div class="hc-body">', '<div class="hc-faq"')
    body = body.replace('<button type="button" class="hc-more"', '<!--')
    body = re.sub(r'<!--.*', '', body, flags=re.S)
    body = body.strip()
    # cut_inner stops at the opening tag of the next block, so the body still
    # carries the closing tag of its own container.
    body = re.sub(r'</div>\s*$', '', body).strip()

    faq = []
    faq_block = cut_inner(page, '<div class="hc-faq"', '<div class="blog-moreq"')
    for item in re.findall(r'<div class="hc-fa[^"]*">(.*?)</div>\s*</div>', faq_block, re.S):
        q_m = re.search(r'<summary[^>]*>(.*?)</summary>', item, re.S)
        a_m = re.search(r'<div class="hc-fa-a">(.*?)</div>', item, re.S)
        if not a_m:
            a_m = re.search(r'<p>(.*?)</p>', item, re.S)
        if not q_m or not a_m:
            continue
        q = html.unescape(re.sub(r'<[^>]+>', '', q_m.group(1))).strip()
        a = html.unescape(re.sub(r'<[^>]+>', ' ', a_m.group(1)))
        a = re.sub(r'\s+', ' ', a).strip()
        if q and a:
            faq.append((q, a))

    return {
        'id': article_id,
        'title': title,
        'description': description,
        'date': date,
        'category': category,
        'content': body,
        'faq': faq,
    }


def py_str(text):
    """Single-line Python string literal safe for the generated module."""
    return json.dumps(text, ensure_ascii=False)


def render(records):
    lines = [
        '# -*- coding: utf-8 -*-',
        '"""Blog articles, part 10 — recovered release notes.',
        '',
        'The original untracked source was lost when the build directory was',
        'overwritten; this file is rebuilt from the generated pages by',
        'tools/recover_blog_j.py so the next build keeps both articles byte-for-byte',
        '(modulo whitespace) instead of dropping them.',
        '"""',
        '',
        'BLOG_ARTICLES_J = []',
        '',
        '',
        'def _a(i, **kw):',
        "    kw['id'] = i",
        '    BLOG_ARTICLES_J.append(kw)',
        '',
        '',
    ]
    for rec in records:
        lines.append("_a(%s," % py_str(rec['id']))
        lines.append("   category=%s," % py_str(rec['category']))
        lines.append("   title=%s," % py_str(rec['title']))
        lines.append("   description=%s," % py_str(rec['description']))
        lines.append("   date=%s," % py_str(rec['date']))
        lines.append("   content=")
        body = rec['content']
        # One literal per line keeps the generated file readable and diffable.
        for chunk in body.splitlines(True):
            lines.append('       ' + py_str(chunk))
        lines[-1] = lines[-1] + '),'
        if rec['faq']:
            lines.append('   faq=[')
            for q, a in rec['faq']:
                lines.append('       {\'q\': %s,' % py_str(q))
                lines.append('        \'a\': %s},' % py_str(a))
            lines.append('   ]')
        lines.append('')
        lines.append('')
    return '\n'.join(lines) + '\n'


def main(argv):
    records = [extract(i) for i in IDS]
    for rec in records:
        ok = all([rec['title'], rec['description'], rec['date'], rec['content']])
        print(f"{rec['id']}: title={bool(rec['title'])} desc={len(rec['description'])} "
              f"date={rec['date']} category={rec['category']!r} "
              f"body={len(rec['content'])} faq={len(rec['faq'])}"
              + ('' if ok else '  <-- INCOMPLETE'))
    if '--check' in argv:
        return
    text = render(records)
    with io.open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print('wrote', os.path.relpath(OUT, ROOT))


if __name__ == '__main__':
    main(sys.argv[1:])
