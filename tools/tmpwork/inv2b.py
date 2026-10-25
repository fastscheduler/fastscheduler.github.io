import io, re
BS = chr(92)
SQ = chr(39)
CLS = '[^' + SQ + BS + BS + ']'
ANY = BS + '.'
pat = SQ + '((?:' + CLS + '|' + ANY + ')*)' + SQ + BS + 's*' + ':'
pat += BS + 's*' + SQ + '((?:' + CLS + '|' + ANY + ')*)' + SQ
def js_str_pairs(s):
    return re.findall(pat, s)
chrome = io.open('website/scripts/ru-chrome.js', encoding='utf-8').read()
lang = io.open('website/scripts/lang.js', encoding='utf-8').read()
pairs = js_str_pairs(chrome) + js_str_pairs(lang)
MAP = {}
for k, v in pairs:
    k = k.replace(BS+SQ, SQ).replace(BS+chr(34), chr(34))
    v = v.replace(BS+SQ, SQ).replace(BS+chr(34), chr(34))
    MAP[k] = v
print('MAP keys:', len(MAP))
texts = io.open('tools/tmpwork/index_texts.txt', encoding='utf-8').read().split(chr(10))
SKIP = ('Fast Scheduler', 'FastScheduler', 't.me', '@', 'FS', '027', 'http')
missing = [t for t in texts if t not in MAP and not any(x in t for x in SKIP) and len(t) < 200]
io.open('tools/tmpwork/index_missing.txt', 'w', encoding='utf-8').write(chr(10).join(missing))
print('INDEX missing:', len(missing))
longnodes = [t for t in texts if len(t) >= 200]
print('INDEX long nodes:', len(longnodes))
io.open('tools/tmpwork/index_long.txt', 'w', encoding='utf-8').write(chr(10).join(longnodes))
