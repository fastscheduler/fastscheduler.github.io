import io
p = 'tools/build_ru_pages3.py'
s = io.open(p, encoding='utf-8').read()
a = 'data-(?:art|cat)="([a-z0-9_]+)">'
assert a in s
s = s.replace(a, 'data-(?:art|cat)="([a-z0-9_]+)"[^>]*>', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('section pattern fixed')
