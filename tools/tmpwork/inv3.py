import io, re, json, importlib.util, os
s = io.open('website/scripts/help-data.js', encoding='utf-8').read()
m2 = re.search(r'__HELP_SIDE=(\[.*?\])' + chr(59), s, re.S)
side = json.loads(m2.group(1))
side_ids = [x['id'] for x in side]
BATCH = 'tools/ru_batches'
patch = {}
for f in sorted(os.listdir(BATCH)):
    if f.startswith('help_') and f.endswith('.py'):
        spec = importlib.util.spec_from_file_location('rux_' + f[:-3], os.path.join(BATCH, f))
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        for k, v in getattr(mod, 'PATCH', {}).items():
            if isinstance(v, dict):
                patch[k] = v
catrec = [k for k, v in patch.items() if 'children' in v]
out = ['SIDE cats: %d' % len(side_ids)]
out.append('batch records: %d (%d with children)' % (len(patch), len(catrec)))
missing_cats = [c for c in side_ids if c not in patch]
out.append('SIDE cats missing in batches: %s' % missing_cats)
m = re.search(r'__HELP_DATA=(\[.*\])', s, re.S)
arr = json.loads(m.group(1))
data_ids = [x['id'] for x in arr]
blog_items = [x['id'] for x in arr if 'href' in x]
out.append('DATA items: %d, with href(blog): %d' % (len(arr), len(blog_items)))
help_ids = [x for x in data_ids if x not in blog_items]
missing_ru = [x for x in help_ids if x not in patch]
out.append('help DATA ids missing RU: %d %s' % (len(missing_ru), missing_ru[:10]))
kids_ids = set()
for x in side:
    for k in x.get('kids', []):
        kids_ids.add(k['id'])
out.append('SIDE kids total: %d, kids missing RU: %s' % (len(kids_ids), sorted(kids_ids - set(patch))[:10]))
io.open('tools/tmpwork/inv3.txt', 'w', encoding='utf-8').write(chr(10).join(out))
print('written')
