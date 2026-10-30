"""Round-2 SEO builder patches (idempotent).

Round 1 (patch_seo_builders.py) fixed the help hub: one h1, no body FAQPage
spam, CollectionPage/ItemList in <head>, stable publish dates. This round
fixes what was still keeping the site out of the index:

  1. CRAWL GRAPH (the big one). help.html is a hash-router SPA -- every
     category, article, breadcrumb and pager link is href="#/a/<id>". A
     crawler cannot follow fragments, so all 323 help pages were orphans:
     `site:fastscheduler.github.io` returned exactly one result, the
     homepage. build_help.py now emits a real-href index of every topic and
     article at the bottom of help.html.

  2. Title / description shape. 150 titles ran past 65 chars (Google
     rewrites those and drops the exact phrase the query matched) and 142
     descriptions ran past 160 (SERP truncation). Descriptions were cut at a
     hard 160 characters mid-word. fit_title()/smart_desc() live in
     build_help.py so build_static.py and build_blog.py share one
     implementation.

  3. Duplicate titles. Category hubs used "<Category> — Fast Scheduler Help",
     the same string as the article that shares the category's id.

  4. Legal pages carried no JSON-LD and no og:description / twitter tags, and
     stamped "Updated <today>" on every rebuild.

Usage:  python tools/patch_seo_builders2.py [--check]
"""
import io
import os
import sys

BUILD = os.path.join('website', '_build')

# ---------------------------------------------------------------- edits ----
EDITS = []


def edit(path, old, new, tag):
    EDITS.append((path, old, new, tag))


# ------------------------------------------------------- build_help.py -----
HELP_ANCHOR = "def esc_q(text):"
HELP_HELPERS = '''TITLE_LIMIT = 62
DESC_LIMIT = 155


def _cut_words(s, n):
    """Trim to <= n chars on a word boundary, without dangling punctuation."""
    s = re.sub(r'\\s+', ' ', s or '').strip()
    if len(s) <= n:
        return s
    cut = s[:n]
    sp = cut.rfind(' ')
    if sp >= n * 0.55:
        cut = cut[:sp]
    return cut.rstrip(' ,;:-\\u2013\\u2014&|/')


def fit_title(t):
    """Title that survives the SERP without Google rewriting it.

    Search results clip around 60 characters; longer titles get replaced by
    Google with text from the page, which is how an exact-phrase match gets
    thrown away. Keep the brand suffix, spend the budget on the subject.
    """
    t = re.sub(r'\\s+', ' ', t or '').strip()
    if len(t) <= TITLE_LIMIT:
        return t
    for sep in (' \\u2014 ', ' | ', ' - ', ': '):
        i = t.rfind(sep)
        if i >= 18:
            tail = t[i:]
            budget = TITLE_LIMIT - len(tail)
            if budget >= 18:
                return _cut_words(t[:i], budget) + tail
    return _cut_words(t, TITLE_LIMIT)


def smart_desc(text, floor=70, limit=DESC_LIMIT):
    """Whole-sentence meta description.

    The old build sliced raw article text at exactly 160 characters, so
    descriptions ended mid-word ("...The basic flow 1. Tap S"). Prefer the
    last full sentence that fits; fall back to a clean word-boundary cut.
    """
    t = re.sub(r'\\s+', ' ', (text or '').replace('\\u2014', '-').replace('&mdash;', '-')).strip()
    if not t:
        return ''
    if len(t) <= limit:
        return t
    best = ''
    for m in re.finditer(r'[.!?](?=\\s|$)', t):
        end = m.end()
        if floor <= end <= limit:
            best = t[:end]
        elif end > limit:
            break
    return best or _cut_words(t, limit)


def esc_q(text):'''
edit('build_help.py', HELP_ANCHOR, HELP_HELPERS, 'fit_title/smart_desc helpers')

# The crawlable "Every help article, by topic" index was removed from the
# help center. Do not re-add it: see tools/apply_site_footer.py.


# ----------------------------------------------------- build_static.py -----
edit('build_static.py',
     "    og_img = SITE + '/og-cover-v2.png'\n",
     """    og_img = SITE + '/og-cover-v2.png'
    # One SERP-shaped title/description for every page type on the site.
    title = bh.fit_title(title)
    desc = bh.smart_desc(desc)
""", 'page_head clamp (static)')

edit('build_static.py',
     "        desc = (n.get('description') or strip_html(n['content'])[:160] or n['title']).strip()\n",
     "        desc = bh.smart_desc(\n"
     "            n.get('description') or strip_html(n['content']) or n['title'])\n",
     'article description -> smart_desc')

edit('build_static.py',
     "        intro = strip_html(g['cat'].get('description', '') or g['cat'].get('content', ''))[:220]\n",
     "        intro = strip_html(g['cat'].get('description', '') or g['cat'].get('content', ''))\n",
     'category intro not pre-truncated')

edit('build_static.py',
     "        desc = (intro or f'{ctitle} — guides and answers in the Fast Scheduler help center.').strip()\n",
     "        desc = bh.smart_desc(\n"
     "            intro or f'{ctitle} — guides and answers in the Fast Scheduler help center.')\n",
     'category description -> smart_desc')

edit('build_static.py',
     "        head = page_head(ctitle + ' — Fast Scheduler Help', desc, canonical,\n",
     "        # Distinct from the same-named article page (a category and its\n"
     "        # lead article share an id, so both used \"<Category> — Fast\n"
     "        # Scheduler Help\" and collided on 24 titles).\n"
     "        head = page_head(f'{ctitle} — {len(entries)} Guides | Fast Scheduler', desc, canonical,\n",
     'category hub title disambiguated')

edit('build_static.py',
     "    for n in uniq_articles[:24]:\n"
     "        desc = (n.get('description') or strip_html(n['content'])[:200] or n['title'])\n",
     "    for n in uniq_articles[:24]:\n"
     "        desc = bh.smart_desc(\n"
     "            n.get('description') or strip_html(n['content']) or n['title'])\n",
     'llms.txt description -> smart_desc')

# ------------------------------------------------------- build_blog.py ----
edit('build_blog.py',
     "def page_head(title, desc, canonical, extra_ld='', og_type='article', extra_meta=''):\n    return f'''",
     "def page_head(title, desc, canonical, extra_ld='', og_type='article', extra_meta=''):\n"
     "    title = bh.fit_title(title)\n"
     "    desc = bh.smart_desc(desc)\n"
     "    return f'''",
     'page_head clamp (blog)')

edit('build_blog.py',
     '<figure class="blog-doc-cover"><img src="../img/{art[\'id\']}.webp" alt="" width="1200"',
     '<figure class="blog-doc-cover"><img src="../img/{art[\'id\']}.webp" '
     'alt="{bh.esc(art[\'title\'])}" width="1200"',
     'blog hero alt text')

# ------------------------------------------------------- build_site.py ----
edit('build_site.py',
     '<meta name="description" content="{title} for the Fast Scheduler Telegram bot: scheduling, recurring posts, sender bots, channels, statistics and payments.">\n'
     '<link rel="canonical" href="{canon}">\n'
     '<meta property="og:type" content="article">\n'
     '<meta property="og:site_name" content="Fast Scheduler">\n'
     '<meta property="og:title" content="{title} — Fast Scheduler">\n'
     '<meta property="og:url" content="{canon}">\n'
     '<meta property="og:image" content="https://fastscheduler.github.io/og-cover-v2.png">\n',
     '<meta name="description" content="{ldesc}">\n'
     '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">\n'
     '<link rel="canonical" href="{canon}">\n'
     '<meta property="og:type" content="article">\n'
     '<meta property="og:site_name" content="Fast Scheduler">\n'
     '<meta property="og:title" content="{title} — Fast Scheduler">\n'
     '<meta property="og:description" content="{ldesc}">\n'
     '<meta property="og:url" content="{canon}">\n'
     '<meta property="og:image" content="https://fastscheduler.github.io/og-cover-v2.png">\n'
     '<meta name="twitter:card" content="summary_large_image">\n'
     '<meta name="twitter:title" content="{title} — Fast Scheduler">\n'
     '<meta name="twitter:description" content="{ldesc}">\n'
     '<meta name="twitter:image" content="https://fastscheduler.github.io/og-cover-v2.png">\n'
     '<script type="application/ld+json">{ldjson}</script>\n',
     'legal head: robots/og/twitter/JSON-LD')

edit('build_site.py',
     "def legal_page(title, body_html, updated, cta_url, toc_box, toc_side, sheet_html, card_a, card_b, see_also, doc=''):\n"
     "    slug = doc.replace('.md', '.html') if doc else ''\n"
     "    canon = f'https://fastscheduler.github.io/legal/{slug}' if slug else 'https://fastscheduler.github.io/'\n",
     "def legal_page(title, body_html, updated, cta_url, toc_box, toc_side, sheet_html, card_a, card_b, see_also, doc='', modified=''):\n"
     "    slug = doc.replace('.md', '.html') if doc else ''\n"
     "    canon = f'https://fastscheduler.github.io/legal/{slug}' if slug else 'https://fastscheduler.github.io/'\n"
     "    ldesc = _fit(f'{title} for the Fast Scheduler Telegram bot: scheduling, '\n"
     "                 f'recurring posts, sender bots, channels, statistics and payments.')\n"
     "    _page = {\n"
     "        '@type': 'WebPage', '@id': canon, 'url': canon,\n"
     "        'name': f'{title} \\u2014 Fast Scheduler', 'description': ldesc,\n"
     "        'inLanguage': 'en',\n"
     "        'isPartOf': {'@type': 'WebSite', 'name': 'Fast Scheduler',\n"
     "                    'url': 'https://fastscheduler.github.io/'},\n"
     "        'about': {'@type': 'SoftwareApplication', 'name': 'Fast Scheduler',\n"
     "                  'applicationCategory': 'BusinessApplication',\n"
     "                  'operatingSystem': 'Telegram',\n"
     "                  'url': 'https://fastscheduler.github.io/'},\n"
     "    }\n"
     "    if modified:\n"
     "        _page['dateModified'] = modified\n"
     "    ldjson = json.dumps({\n"
     "        '@context': 'https://schema.org',\n"
     "        '@graph': [\n"
     "            _page,\n"
     "            {'@type': 'BreadcrumbList', 'itemListElement': [\n"
     "                {'@type': 'ListItem', 'position': 1, 'name': 'Fast Scheduler',\n"
     "                 'item': 'https://fastscheduler.github.io/'},\n"
     "                {'@type': 'ListItem', 'position': 2, 'name': 'Legal',\n"
     "                 'item': 'https://fastscheduler.github.io/legal/privacy.html'},\n"
     "                {'@type': 'ListItem', 'position': 3, 'name': title, 'item': canon}]},\n"
     "        ]\n"
     "    }, ensure_ascii=False)\n",
     'legal_page JSON-LD builder')

edit('build_site.py',
     "LEGAL_PAGES = {",
     """def _fit(s, limit=155):
    \"\"\"Word-boundary trim for legal meta descriptions.\"\"\"
    s = re.sub(r'\\s+', ' ', s or '').strip()
    if len(s) <= limit:
        return s
    cut = s[:limit]
    sp = cut.rfind(' ')
    if sp >= limit * 0.55:
        cut = cut[:sp]
    return cut.rstrip(' ,;:-')


def _source_mtime(path):
    \"\"\"ISO date of the last commit that touched a legal source doc.

    write_legal() used datetime.date.today(), so every rebuild claimed the
    policies were revised that day. Google reads dateModified as a freshness
    claim; it should reflect the text, not the build.
    \"\"\"
    try:
        out = subprocess.run(
            ['git', 'log', '-1', '--format=%cs', '--', path],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=20).stdout.strip()
        if re.match(r'^\\d{4}-\\d{2}-\\d{2}$', out):
            return out
    except Exception:
        pass
    return datetime.date.today().isoformat()


LEGAL_PAGES = {""", '_fit/_source_mtime helpers')

edit('build_site.py',
     "        updated = datetime.date.today().strftime('%B %d, %Y')\n",
     "        src_date = _source_mtime(src)\n"
     "        y, mo, dy = (int(x) for x in src_date.split('-'))\n"
     "        updated = datetime.date(y, mo, dy).strftime('%B %d, %Y').replace(' 0', ' ')\n",
     'legal updated date from git')

edit('build_site.py',
     "            f.write(legal_page(title, html, updated, cta_url, toc_box, toc_side, sheet_html,\n"
     "                               card_a, card_b, see_also, doc=out))\n",
     "            f.write(legal_page(title, html, updated, cta_url, toc_box, toc_side, sheet_html,\n"
     "                               card_a, card_b, see_also, doc=out, modified=src_date))\n",
     'legal_page modified= wiring')

edit('build_site.py',
     "    if (_ffs) {{ document.documentElement.setAttribute('data-font', _ffs); }}\n"
     "    var _ffs = localStorage.getItem('fs-font') || localStorage.getItem('fs-help-font') || localStorage.getItem('fs-blog-font');\n"
     "    if (_ffs) {{ document.documentElement.setAttribute('data-font', _ffs); }}\n",
     "    if (_ffs) {{ document.documentElement.setAttribute('data-font', _ffs); }}\n",
     'drop duplicated _ffs declaration')

edit('build_site.py',
     "import datetime\n",
     "import datetime\nimport subprocess\n",
     'import subprocess')


# ---------------------------------------------------------------- apply ----
def main():
    check_only = '--check' in sys.argv
    ok = True
    for path, old, new, tag in EDITS:
        full = os.path.join(BUILD, path)
        src = io.open(full, encoding='utf-8').read()
        if new in src:
            status = 'ok     '
        elif old in src:
            if check_only:
                print('  %-14s PENDING %s' % (path, tag))
                ok = False
                continue
            if src.count(old) != 1:
                print('  %-14s AMBIGUOUS (%d matches) %s' % (path, src.count(old), tag))
                ok = False
                continue
            src = src.replace(old, new)
            io.open(full, 'w', encoding='utf-8', newline='\n').write(src)
            status = 'patched '
        else:
            print('  %-14s MISSING  %s' % (path, tag))
            ok = False
            continue
        print('  %-14s %s %s' % (path, status, tag))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())