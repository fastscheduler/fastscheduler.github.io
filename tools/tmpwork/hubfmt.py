import io, re
s = io.open('website/help.html', encoding='utf-8').read()
tags = []
for m in re.finditer(r'window\.__[A-Z_]+', s):
    tags.append(m.group(0))
from collections import Counter
io.open('tools/tmpwork/hubvars.txt', 'w', encoding='utf-8').write(chr(10).join('%s x%d' % (k, v) for k, v in Counter(tags).items()))
print('vars:', len(set(tags)))
i = s.find('__HELP_SIDE')
io.open('tools/tmpwork/hubside.txt', 'w', encoding='utf-8').write(s[i:i+1200])
i2 = s.find('__HELP_DATA')
io.open('tools/tmpwork/hubdata.txt', 'w', encoding='utf-8').write(s[i2:i+2000])
print('head-title:', re.search(r'<title>(.*?)</title>', s, re.S).group(1)[:100])
