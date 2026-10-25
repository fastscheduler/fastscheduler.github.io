import io
chrome = io.open('website/scripts/ru-chrome.js', encoding='utf-8').read()
lang = io.open('website/scripts/lang.js', encoding='utf-8').read()
longs = io.open('tools/tmpwork/index_long.txt', encoding='utf-8').read().split(chr(10))
pool = (chrome + lang).replace(chr(92)+chr(39), chr(39))
out = []
for t in longs:
    out.append('IN-MAP' if t in pool else 'NOT-IN-MAP')
    out.append(t[:150])
io.open('tools/tmpwork/long_check.txt', 'w', encoding='utf-8').write(chr(10).join(out))
print('checked', len(longs))
cfg = io.open('website/scripts/site-config.js', encoding='utf-8').read()
print('site-config bytes:', len(cfg))
io.open('tools/tmpwork/cfg_head.txt', 'w', encoding='utf-8').write(cfg[:1500])
