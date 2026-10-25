import io, sys
sys.path.insert(0, 'tools')
from build_ru_pages import load_ru_articles
from build_ru_pages3 import global_swaps
html = io.open('website/help.html', encoding='utf-8').read()
patch = load_ru_articles()
out = global_swaps(html, patch)
for key in ['hc-row-m">1 Q', 'Every help article, by topic', 'help/a/start.html', 'class="dot">', '+6 more</span>', 'hc-cat-prev']:
    import re
    n = len(re.findall(re.escape(key), out))
    io.open('tools/tmpwork/dbg5.txt', 'a', encoding='utf-8').write('%s :: %d%s' % (key, n, chr(10)))
print('dbg5 ok')
