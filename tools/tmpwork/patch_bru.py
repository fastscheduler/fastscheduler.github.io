import io
p = 'tools/build_ru.py'
s = io.open(p, encoding='utf-8').read()
a = "return bs.page_shell(head, content, rel='../../..')"
b = "return bs.page_shell(head, content, rel='../../..', lang='ru')"
assert a in s
s = s.replace(a, b, 1)
a = "return bs.page_shell(head, body, rel='../..')"
b = "return bs.page_shell(head, body, rel='../..', lang='ru')"
assert a in s
s = s.replace(a, b, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('bru patched')
