import io, re, sys
sys.path.insert(0, 'tools')
from build_ru_pages import load_ru_articles
from build_ru_pages3 import split_sections, global_swaps
html = io.open('website/help.html', encoding='utf-8').read()
spans, home = split_sections(html)
kinds = {}
for k, ident, a, b in spans:
    kinds[k] = kinds.get(k, 0) + 1
io.open('tools/tmpwork/dbg1.txt', 'w', encoding='utf-8').write(
    'spans=%d kinds=%s%s' % (len(spans), kinds, chr(10))
    + chr(10).join('%s %s %d-%d' % (k, ident, a, b) for k, ident, a, b in spans[:8]))
print('spans:', len(spans), kinds)
t2 = global_swaps(html, load_ru_articles())
left = len(re.findall('hc-row-t', t2))
ml = len(re.findall('Message List', t2))
io.open('tools/tmpwork/dbg2.txt', 'w', encoding='utf-8').write('rows-left=%d msglist-left=%d' % (left, ml))
print('rows:', left, 'msglist:', ml)
