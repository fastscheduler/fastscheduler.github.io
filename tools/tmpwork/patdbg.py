import io
src = io.open('tools/tmpwork/inv2.py', encoding='utf-8').read()
i = src.find('pat = SQ')
print('SRC-LINES:')
for ln in src.split(chr(10))[3:6]:
    print('L>', ln)
