import io, re
s = io.open('website/help.html', encoding='utf-8').read()
i = s.find('data-cat="misc"')
io.open('tools/tmpwork/misc_sec.txt', 'w', encoding='utf-8').write(s[i:i+1200])
print('ok')
