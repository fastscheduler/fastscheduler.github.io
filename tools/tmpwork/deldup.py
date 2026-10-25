import io
p = 'website/_build/build_static.py'
s = io.open(p, encoding='utf-8').read()
a = "        return page_shell_ru(title_html, body, rel)" + chr(10) + chr(10) + '    ' + chr(34)*3 + "rel: prefix for assets from the page location (help/a|c are 2 levels deep)." + chr(34)*3 + chr(10)
assert a in s
s = s.replace(a, "        return page_shell_ru(title_html, body, rel)" + chr(10), 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('dup removed')
