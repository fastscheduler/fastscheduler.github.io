import io
BS = chr(92)
SQ = chr(39)
def pairs_in(s):
    out = []
    n = len(s)
    i = 0
    while i < n:
        if s[i] == SQ:
            j = i + 1
            buf = []
            while j < n:
                c = s[j]
                if c == BS and j + 1 < n:
                    buf.append(s[j+1]); j += 2; continue
                if c == SQ:
                    break
                buf.append(c); j += 1
            else:
                i += 1; continue
            key = ''.join(buf)
            k = j + 1
            while k < n and s[k] in ' :\t\r\n':
                k += 1
            if k < n and s[k] == SQ:
                j = k + 1
                buf = []
                while j < n:
                    c = s[j]
                    if c == BS and j + 1 < n:
                        buf.append(s[j+1]); j += 2; continue
                    if c == SQ:
                        break
                    buf.append(c); j += 1
                else:
                    i += 1; continue
                out.append((key, ''.join(buf)))
                i = j + 1
                continue
            i = j + 1
        else:
            i += 1
    return out
chrome = io.open('website/scripts/ru-chrome.js', encoding='utf-8').read()
lang = io.open('website/scripts/lang.js', encoding='utf-8').read()
pairs = pairs_in(chrome) + pairs_in(lang)
MAP = {}
for k, v in pairs:
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
