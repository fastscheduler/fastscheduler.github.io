import io
p = 'tools/tmpwork/patch_nav.py'
s = io.open(p, encoding='utf-8').read()
old = '"Search the help center" + chr(226) + chr(128) + chr(166) + chr(34)'
new = '"Search the help center" + chr(8230) + chr(34)'
assert old in s
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('fixed')
