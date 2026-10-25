import io, json, re
s = io.open('website/scripts/help-data.js', encoding='utf-8').read()
m = re.search(r'__HELP_DATA=(\[.*\])', s, re.S)
arr = json.loads(m.group(1))
print('DATA items:', len(arr), 'KEYS:', sorted(arr[0].keys()))
m2 = re.search(r'__HELP_SIDE=(\[.*?\])' + chr(59) + 'window', s, re.S)
if not m2:
    m2 = re.search(r'__HELP_SIDE=(\[.*?\])' + chr(59), s, re.S)
side = json.loads(m2.group(1))
print('SIDE items:', len(side), 'KEYS:', sorted(side[0].keys()))
io.open('tools/tmpwork/side_cats.txt', 'w', encoding='utf-8').write(
    chr(10).join(x.get('id', '') + ' | ' + x.get('title', '') for x in side))
for k in sorted(arr[0].keys()):
    v = arr[0][k]
    print(k, type(v).__name__, str(v)[:100].replace(chr(10), ' '))
