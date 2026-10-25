import io
p = 'tools/build_ru_pages.py'
lines = io.open(p, encoding='utf-8').read().split(chr(10))
assert 'm = re.search' in lines[264], lines[264][:60]
del lines[264]
io.open(p, 'w', encoding='utf-8', newline='').write(chr(10).join(lines))
print('line removed')
