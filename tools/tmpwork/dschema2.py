import io
s = io.open('website/scripts/help-data.js', encoding='utf-8').read()
print('len:', len(s))
print('SIDE at:', s.find('__HELP_SIDE'))
print('DATA at:', s.find('__HELP_DATA'))
print('tail:', s[-200:])
