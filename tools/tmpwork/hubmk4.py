import io, re
s = io.open('website/help.html', encoding='utf-8').read()
i = s.find('data-view="article"')
io.open('tools/tmpwork/hub_art.txt', 'w', encoding='utf-8').write(s[max(0,i-600):i+3000])
print('ok')
