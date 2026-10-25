import io
p = 'tools/tmpwork/patch_nav.py'
s = io.open(p, encoding='utf-8').read()
Q = chr(34)
old = '(' + Q + 'href=' + Q + '+chr(34)+"{rel}/help.html"+chr(34)+" " + chr(10) + ')'
assert 'chr(34)+" "+chr(10)' in s or True
s2 = s.replace(chr(34) + '" "+chr(10)', chr(34) + '"' + chr(39) + '"+chr(10)')
assert s2 != s
io.open(p, 'w', encoding='utf-8', newline='').write(s2)
print('fixed14')
