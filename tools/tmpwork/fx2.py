import io
s = io.open('website/scripts/ru-chrome.js', encoding='utf-8').read()
i = s.find('FIXUPS')
j = s.find('});', s.find('FIXUPS: [') if 'FIXUPS: [' in s else i)
io.open('tools/tmpwork/fixups2.txt', 'w', encoding='utf-8').write(s[i:i+6000])
print('fx len region ok')
