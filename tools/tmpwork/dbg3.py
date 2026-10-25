import io, re, sys
sys.path.insert(0, 'tools')
from build_ru_pages import load_ru_articles
from build_ru_pages3 import apply_surgery
html = io.open('website/help.html', encoding='utf-8').read()
patch = load_ru_articles()
out, stats = apply_surgery(html, patch, {})
io.open('tools/tmpwork/surg.txt', 'w', encoding='utf-8').write(out)
print('stats:', stats)
left_h2 = re.findall(r'data-art="([a-z0-9_]+)">(?:(?!</section>).)*?<h2>(.*?)</h2>', out[:5000000], re.S)
en_h2 = [(a, t) for a, t in re.finditer(r'data-art="([a-z0-9_]+)"', out) and []]
CYR = chr(0x410)
bad = []
for m in re.finditer(r'<section class="view" data-view="article" data-art="([a-z0-9_]+)"[^>]*>', out):
    sec = out[m.start():m.start()+3000]
    h = re.search(r'<h2>(.*?)</h2>', sec)
    if h and not re.search('[' + chr(0x410) + '-' + chr(0x44F) + chr(0x401) + chr(0x451) + ']', h.group(1)):
        bad.append((m.group(1), h.group(1)[:60]))
io.open('tools/tmpwork/badh2.txt', 'w', encoding='utf-8').write(chr(10).join('%s :: %s' % b for b in bad))
print('EN-h2 sections:', len(bad))
i = out.find('1 Q&amp;A')
io.open('tools/tmpwork/qa1.txt', 'w', encoding='utf-8').write(out[max(0,i-300):i+200])
print('qa ctx written')
g = re.search(r'[0-9]+ guides', out)
io.open('tools/tmpwork/guides.txt', 'w', encoding='utf-8').write(out[max(0,g.start()-300):g.start()+200] if g else 'NONE')
print('guides ctx written')
