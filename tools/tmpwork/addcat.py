import io
p = 'tools/build_ru_pages3.py'
s = io.open(p, encoding='utf-8').read()

anchor = "    html = re.sub(r'<a href=\"#/c/([a-z0-9_]+)\">(.*?)</a>', others_sub, html, flags=re.S)" + chr(10) + "    return html"
assert anchor in s, 'anchor miss'

code = """    def _span_end(html, open_start):
        depth = 0
        i = open_start
        n = len(html)
        while i < n:
            if html.startswith('<span', i):
                j = html.find('>', i)
                if j < 0:
                    return None
                if html[j - 1] == '/':
                    i = j + 1
                    continue
                depth += 1
                i = j + 1
            elif html.startswith('</span>', i):
                depth -= 1
                i += 7
                if depth == 0:
                    return i
            else:
                i += 1
        return None

    def cat_sub(m):
        cid = m.group(1)
        inner = m.group(2)
        if cid == 'misc':
            title = 'Другие темы'
            kids = []
        else:
            rec = patch.get(cid, {})
            title = (clean_ru(rec.get('title', '')) or '').strip() or cid
            kids = []
            for k in (rec.get('children') or []):
                t = (clean_ru(patch.get(k, {}).get('title', '')) or '').strip()
                if t:
                    kids.append(t)
        inner = re.sub(r'(<span class="hc-cat-t">).*?(</span>)',
                       lambda mm: mm.group(1) + H.escape(title, quote=False) + mm.group(2),
                       inner, count=1, flags=re.S)
        nm = re.search(r'(<span class="hc-cat-c">)([0-9]+)( articles</span>)', inner)
        if nm:
            n = int(nm.group(2))
            inner = (inner[:nm.start()] + nm.group(1) + str(n) + ' '
                     + plural(n, 'статья', 'статьи', 'статей') + '</span>' + inner[nm.end():])
        ps = inner.find('<span class="hc-cat-prev">')
        if ps >= 0 and kids:
            pe = _span_end(inner, ps)
            if pe is not None:
                prev = ''.join('<span>' + H.escape(t, quote=False) + '</span>' for t in kids[:3])
                more_n = max(0, len(kids) - 3)
                if more_n:
                    prev += '<span>+' + str(more_n) + ' ещё</span>'
                inner = inner[:ps] + '<span class="hc-cat-prev">' + prev + '</span>' + inner[pe:]
        return '<a class="hc-cat hc-card" href="#/c/' + cid + '">' + inner + '</a>'

    html = re.sub(r'<a class="hc-cat hc-card" href="#/c/([a-z0-9_]+)">(.*?)</a>',
                  cat_sub, html, flags=re.S)
"""
s = s.replace(anchor, "    html = re.sub(r'<a href=\"#/c/([a-z0-9_]+)\">(.*?)</a>', others_sub, html, flags=re.S)" + chr(10) + code + "    return html", 1)

cta_anchor = "    'Unlimited sends': 'Безлимитные отправки'," + chr(10) + "}"
assert cta_anchor in s, 'cta anchor miss'
s = s.replace(cta_anchor,
              "    'Unlimited sends': 'Безлимитные отправки'," + chr(10)
              + "    'The in-bot assistant answers the same questions — and a human reads every ticket.': 'Встроенный помощник отвечает на те же вопросы — а каждый тикет читает человек.'," + chr(10) + "}", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('cat+cta added')
