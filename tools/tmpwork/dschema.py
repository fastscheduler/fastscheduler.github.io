import io, json, re
s = io.open('website/scripts/help-data.js', encoding='utf-8').read()
m = re.search(r'window\.__HELP_DATA=(\[.*?\]);window', s, re.S)
print('data-found:', bool(m))
if m:
    arr = json.loads(m.group(1))
    print('items:', len(arr))
    print('KEYS:', sorted(arr[0].keys()))
    for k in sorted(arr[0].keys()):
        v = arr[0][k]
        print(k, type(v).__name__, str(v)[:120].replace(chr(10), ' '))
    ms = re.search(r'window\.__HELP_SIDE=(\[.*?\]);window', s, re.S)
    if ms:
        side = json.loads(ms.group(1))
        print('SIDE items:', len(side), 'KEYS:', sorted(side[0].keys()))
        io.open('tools/tmpwork/side_cats.txt', 'w', encoding='utf-8').write(
            chr(10).join(x.get('id', '') + ' | ' + x.get('title', '') for x in side))
