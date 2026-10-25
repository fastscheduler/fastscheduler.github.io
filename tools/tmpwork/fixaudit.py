import io, re
p = 'tools/build_ru_pages.py'
s = io.open(p, encoding='utf-8').read()
a = "            if len(key) >= 3 and re.search(r'[A-Za-z]', key):"
assert a in s
CYR = "[^" + chr(0x410) + "-" + chr(0x44F) + chr(0x401) + chr(0x451) + "]"
b = ("            if len(key) >= 3 and re.search(r'[A-Za-z]', key) and not re.search(r'[" + chr(0x410) + "-" + chr(0x44F) + chr(0x401) + chr(0x451) + "]', key):")
s = s.replace(a, b, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('audit cyr-filtered')
