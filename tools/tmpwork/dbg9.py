import re
t = '<span>+6 more</span>'
for pat in [r'<span>\+([0-9]+) more</span>']:
    print('match:', bool(re.search(pat, t)))
import io, sys
sys.path.insert(0, 'tools')
src = io.open('tools/build_ru_pages3.py', encoding='utf-8').read()
i = src.find('_spannn') if False else src.find("more</span>',")
print('file ctx:', src[i-60:i+40].replace(chr(10), ' '))
