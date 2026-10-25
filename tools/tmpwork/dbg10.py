import io, re, sys
sys.path.insert(0, 'tools')
from build_ru_pages import load_ru_articles
from build_ru_pages3 import apply_surgery
html = io.open('website/help.html', encoding='utf-8').read()
out, stats = apply_surgery(html, load_ru_articles(), {})
CYR = '[' + chr(0x410) + '-' + chr(0x44F) + chr(0x401) + chr(0x451) + ']'
bad = []
for m in re.finditer(r'<section class="view" data-view="article" data-art="([a-z0-9_]+)"[^>]*>', out):
    a = m.start()
    b = out.find('</section>', a)
    sec = out[a:b]
    i = sec.find('<div class="hc-body">')
    if i < 0:
        bad.append((m.group(1), 'NO-BODY'))
        continue
    j = sec.find('<div class="hc-faq">', i)
    k = sec.find('<div class="hc-others"', i)
    ends = [x for x in (j, k) if x > 0]
    body = sec[i:min(ends) if ends else len(sec)]
    txt = re.sub(r'<[^>]+>', ' ', body)
    import re as _re
    cyr = len(_re.findall(CYR, txt))
    lat = len(_re.findall(r'[A-Za-z]', txt))
    if cyr < 50:
        bad.append((m.group(1), 'cyr=%d lat=%d' % (cyr, lat)))
io.open('tools/tmpwork/badbody.txt', 'w', encoding='utf-8').write(chr(10).join('%s %s' % x for x in bad))
print('bad bodies:', len(bad))
