import io, re
s = io.open('website/help.html', encoding='utf-8').read()
i = s.find('data-view="category"')
io.open('tools/tmpwork/hub_catsec.txt', 'w', encoding='utf-8').write(s[max(0,i-300):i+2500])
j = s.find('hc-faq')
io.open('tools/tmpwork/hub_faq.txt', 'w', encoding='utf-8').write(s[max(0,j-400):j+2500])
print('ok')
