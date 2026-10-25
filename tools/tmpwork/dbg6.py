import io, re, sys
sys.path.insert(0, 'tools')
from build_ru_pages import load_ru_articles
from build_ru_pages3 import global_swaps
html = io.open('website/help.html', encoding='utf-8').read()
out = global_swaps(html, load_ru_articles())
i = out.find('+6 more</span>')
io.open('tools/tmpwork/more6.txt', 'w', encoding='utf-8').write(out[max(0,i-500):i+100])
print('ctx ok')
