import io, re, sys
sys.path.insert(0, 'tools')
import build_ru_pages3 as P3
from build_ru_pages import load_ru_articles
html = io.open('website/help.html', encoding='utf-8').read()
patch = load_ru_articles()
i = html.find('href="#/c/privacy"')
card = html[i-200:i+1200]
io.open('tools/tmpwork/privcard.txt', 'w', encoding='utf-8').write(card)
m = re.search(r'<a class="hc-cat hc-card" href="#/c/([a-z0-9_]+)">(.*?)</a>', card, re.S)
io.open('tools/tmpwork/dbg7.txt', 'w', encoding='utf-8').write('catmatch=' + str(bool(m)) + chr(10))
print('card ok')
