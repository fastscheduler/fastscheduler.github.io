import io, re, sys
sys.path.insert(0, 'tools')
from build_ru_pages import load_ru_articles
from build_ru_pages3 import apply_surgery
html = io.open('website/help.html', encoding='utf-8').read()
out, _ = apply_surgery(html, load_ru_articles(), {})
for key in ['before day 17.', 'on the main menu', 'Step by step:', '1. Click']:
    i = out.find(key)
    ctx = out[max(0,i-400):i+200] if i >= 0 else 'NOT-FOUND'
    m = None
    if i >= 0:
        back = out[max(0,i-20000):i]
        ms = list(re.finditer(r'data-art="([a-z0-9_]+)"', back))
        m = ms[-1].group(1) if ms else '?'
    io.open('tools/tmpwork/fragctx.txt', 'a', encoding='utf-8').write('KEY=%s SEC=%s%s%s' % (key, m, chr(10), ctx[:700].replace(chr(10), ' ') + chr(10) + '====' + chr(10)))
print('frag ok')
