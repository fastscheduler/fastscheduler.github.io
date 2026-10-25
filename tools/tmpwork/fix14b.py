import io
p = 'tools/tmpwork/patch_nav.py'
s = io.open(p, encoding='utf-8').read()
a = 'help.html" + chr(34) + " " + chr(10)'
b = 'help.html" + chr(34) + chr(39) + chr(10)'
assert a in s
s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('fixed14b')
