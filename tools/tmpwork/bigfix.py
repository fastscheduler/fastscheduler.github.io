import io
NL = chr(10)

# ---- P1: part2 uses merged_map ----
p = 'tools/build_ru_pages2.py'
s = io.open(p, encoding='utf-8').read()
a = 'from build_ru_pages import ('
assert a in s
s = s.replace(a, 'from build_ru_pages3 import merged_map' + NL + 'from build_ru_pages import (', 1)
a = '    html, unmapped = transform(html, MAP)' + NL + '    m = re.search'
assert a in s
s = s.replace(a, '    html, unmapped = transform(html, merged_map(MAP))' + NL + '    m = re.search', 1)
old404 = '    html, unmapped = transform(html, MAP)' + NL + "    html = set_head(html, NF_TITLE_RU"
assert old404 in s
s = s.replace(old404, '    html, unmapped = transform(html, merged_map(MAP))' + NL + "    html = set_head(html, NF_TITLE_RU", 1)
# index attr/i swaps before set_head in build_index
a = "    html = fix_asset_paths(html)" + NL + "    html = set_head(html, IDX_TITLE_RU"
assert a in s
s = s.replace(a, "    html = fix_asset_paths(html)" + NL
              + '    html = html.replace(\'<i>your</i>\', \'<i>ваши</i>\')' + NL
              + '    html = html.replace(\'aria-label="Previous plan"\', \'aria-label="Предыдущий тариф"\')' + NL
              + '    html = html.replace(\'aria-label="Next plan"\', \'aria-label="Следующий тариф"\')' + NL
              + '    html = html.replace(\'title="Fast Scheduler Blog"\', \'title="Блог Fast Scheduler"\')' + NL
              + "    html = set_head(html, IDX_TITLE_RU", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('P1 ok')

# ---- P2: part3 additions ----
p = 'tools/build_ru_pages3.py'
s = io.open(p, encoding='utf-8').read()
anchor = "    html = re.sub(r'<a href=\"#/c/([a-z0-9_]+)\">(.*?)</a>', others_sub, html, flags=re.S)" + NL
assert anchor in s
code = """    html = re.sub(r'<span class="dot">([0-9]+) Q&amp;A</span>',
                  lambda m: '<span class="dot">' + m.group(1) + ' '
                  + plural(int(m.group(1)), 'вопрос и ответ', 'вопроса и ответа', 'вопросов и ответов') + '</span>',
                  html, flags=re.S)
    html = _swap_idx(html, patch)
    html = _swap_misc_prev(html, patch)
"""
s = s.replace(anchor, anchor + code, 1)
helpers = '''
_EN_TITLES = None


def _en_titles():
    global _EN_TITLES
    if _EN_TITLES is None:
        import json
        from build_ru_pages import SITE as _SITE
        src = io_open(_SITE + '/scripts/help-data.js')
        import re as _re
        arr = json.loads(_re.search(r'__HELP_DATA=(\[.*\])', src, _re.S).group(1))
        _EN_TITLES = {x['id']: x.get('t', '') for x in arr}
    return _EN_TITLES


def io_open(path):
    import io as _io
    return _io.open(path, encoding='utf-8').read()


def _swap_idx(html, patch):
    def h3_sub(m):
        cid = m.group(1)
        if cid == 'misc':
            t = 'Другие темы'
        else:
            t = ru_title(patch, cid, m.group(2))
        n = int(m.group(3))
        return ('<h3><a href="#/c/' + cid + '">' + H.escape(t, quote=False) + '</a><span>'
                + str(n) + ' ' + plural(n, 'гайд', 'гайда', 'гайдов') + '</span></h3>')
    html = re.sub(r'<h3><a href="help/c/([a-z0-9_]+)\.html">(.*?)</a><span>([0-9]+) guides</span></h3>',
                  h3_sub, html, flags=re.S)
    html = re.sub(r'<li><a href="help/a/([a-z0-9_]+)\.html">(.*?)</a></li>',
                  lambda m: '<li><a href="#/a/' + m.group(1) + '">'
                  + H.escape(ru_title(patch, m.group(1), m.group(2)), quote=False) + '</a></li>',
                  html, flags=re.S)
    html = html.replace('<h2 id="hcIndexH">Every help article, by topic</h2>',
                        '<h2 id="hcIndexH">Все статьи помощи по темам</h2>')
    html = html.replace('Each guide below also has its own page, so you can link to it, bookmark it or search for it directly.',
                        'У каждого гайда ниже есть своя страница — можно делиться ссылкой, добавлять в закладки и искать напрямую.')
    return html


def _swap_misc_prev(html, patch):
    ent = _en_titles()
    rev = {}
    for aid, et in ent.items():
        t = ru_title(patch, aid, '')
        if et and t:
            rev[et] = t
    def prev_sub(m):
        inner = m.group(1)
        def sp(mm):
            return '<span>' + H.escape(rev.get(mm.group(1), mm.group(1)), quote=False) + '</span>'
        inner = re.sub(r'<span>(.*?)</span>', sp, inner, flags=re.S)
        inner = re.sub(r'<span>\+([0-9]+) more</span>',
                       lambda mm: '<span>+' + mm.group(1) + ' ещё</span>', inner, flags=re.S)
        return '<span class="hc-cat-prev">' + inner + '</span>'
    return re.sub(r'<span class="hc-cat-prev">(.*?)</span>\s*</span>', prev_sub, html, flags=re.S)
'''
s = s + helpers
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('P2 ok')
