import io, re, html as H
s = io.open('website/index.html', encoding='utf-8').read()
print('INDEX bytes:', len(s))
s2 = re.sub(r'<script.*?</script>', '', s, flags=re.S | re.I)
s2 = re.sub(r'<style.*?</style>', '', s2, flags=re.S | re.I)
parts = re.split(r'<[^>]+>', s2)
texts = []
for p in parts:
    t = H.unescape(p)
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) >= 3 and re.search(r'[A-Za-z]', t):
        texts.append(t)
uniq = list(dict.fromkeys(texts))
io.open('tools/tmpwork/index_texts.txt', 'w', encoding='utf-8').write(chr(10).join(uniq))
print('INDEX text-nodes:', len(uniq))
links = sorted(set(re.findall(r'href="([^"]+)"', s)))
site_links = [l for l in links if not l.startswith(('http', '#', 'mailto', 'data:'))]
io.open('tools/tmpwork/index_links.txt', 'w', encoding='utf-8').write(chr(10).join(site_links))
print('INDEX site-links:', len(site_links))
h = io.open('website/help.html', encoding='utf-8').read()
print('HELP bytes:', len(h))
