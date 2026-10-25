import io
s = io.open('tools/ru_batches/help_01_a_g.py', encoding='utf-8').read()
i = s.find('PATCH')
io.open('tools/tmpwork/batch_sample.txt', 'w', encoding='utf-8').write(s[i:i+2500])
print('ok')
