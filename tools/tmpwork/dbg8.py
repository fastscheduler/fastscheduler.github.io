import io, sys
sys.path.insert(0, 'tools')
import build_ru_pages3 as P3
from build_ru_pages import load_ru_articles
html = io.open('website/help.html', encoding='utf-8').read()
patch = load_ru_articles()
i = html.find('href="#/c/privacy"')
card = html[i-200:i+1400]
out = P3._swap_misc_prev(card, patch)
io.open('tools/tmpwork/miscprev_out.txt', 'w', encoding='utf-8').write(out)
print('misc test ok')
