import io
p = 'tools/build_ru_pages3.py'
s = io.open(p, encoding='utf-8').read()
a = "    return re.sub(r'<span class=\"hc-cat-prev\">(.*?)</span>" + chr(92) + "s*</span>', prev_sub, html, flags=re.S)"
assert a in s, 'outer miss'
b = "    return re.sub(r'<span class=\"hc-cat-prev\">((?:(?!</a>).)*)</span>', prev_sub, html, flags=re.S)"
s = s.replace(a, b, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('more-pattern fixed')
