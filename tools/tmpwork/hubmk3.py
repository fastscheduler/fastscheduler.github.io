import io, re
s = io.open('website/help.html', encoding='utf-8').read()
outs = []
for pat in [r'<article[^>]*>', r'data-article[^>]*', r'id="a-[a-z_0-9-]+"', r'href="#/a/getting_started"[^>]*><', r'<section[^>]*id="[^"]*"[^>]*>']:
    ms = [m.group(0)[:120] for m in re.finditer(pat, s)][:6]
    outs.append('PAT %s -> %d' % (pat[:30], len(ms)))
    outs += ms[:4]
io.open('tools/tmpwork/hub_struct.txt', 'w', encoding='utf-8').write(chr(10).join(outs))
print('ok')
