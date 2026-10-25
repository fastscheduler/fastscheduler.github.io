import io
s = io.open('website/scripts/ru-chrome.js', encoding='utf-8').read()
i = s.find('FIXUPS')
io.open('tools/tmpwork/fixups.txt', 'w', encoding='utf-8').write(s[i:i+3000])
print('ok len', len(s))
