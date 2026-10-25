import io, re
s = io.open('website/help.html', encoding='utf-8').read()
for pat, name in [(r'<a class="hc-card[^>]*>.*?</a>', 'CARD'), (r'<a class="hc-row"[^>]*>.*?</a>', 'ROW')]:
    m = re.search(pat, s, re.S)
    io.open('tools/tmpwork/hub_%s.txt' % name, 'w', encoding='utf-8').write(m.group(0)[:1500] if m else 'NONE')
lds = [m.group(0)[:400] for m in re.finditer(r'<script type="application/ld\+json">', s)]
io.open('tools/tmpwork/hub_ld.txt', 'w', encoding='utf-8').write(chr(10).join(['LD count: %d' % len(lds)] + lds[:4]))
print('cards ok')
