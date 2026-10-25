import io, re
s = io.open('website/help.html', encoding='utf-8').read()
outs = []
for m in re.finditer(r'<div class="hc-faq">|<section class="hc-faq">|<div class="hc-related">|<nav class="hc-pager">|<div class="hc-cta">', s):
    outs.append('%s at %d' % (m.group(0), m.start()))
io.open('tools/tmpwork/hub_blocks.txt', 'w', encoding='utf-8').write(chr(10).join(outs[:20]) + chr(10) + 'total-faq: %d' % len(re.findall(r'class="hc-faq"', s)))
i = s.find('<div class="hc-faq">')
if i > 0:
    io.open('tools/tmpwork/hub_faq2.txt', 'w', encoding='utf-8').write(s[i:i+2200])
print('ok')
