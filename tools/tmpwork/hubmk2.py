import io, re, json
s = io.open('website/help.html', encoding='utf-8').read()
m = re.search(r'<a class="hc-cat[^>]*>.*?</a>', s, re.S)
io.open('tools/tmpwork/hub_CAT.txt', 'w', encoding='utf-8').write(m.group(0)[:2000] if m else 'NONE')
blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
out = ['LD blocks: %d' % len(blocks)]
for b in blocks:
    try:
        d = json.loads(b)
        out.append('type: %s keys: %s' % (d.get('@type'), sorted(d.keys())[:8]))
        out.append(json.dumps(d, ensure_ascii=False)[:600])
    except Exception as e:
        out.append('parse-fail %s' % e)
io.open('tools/tmpwork/hub_ld2.txt', 'w', encoding='utf-8').write(chr(10).join(out))
print('ok')
