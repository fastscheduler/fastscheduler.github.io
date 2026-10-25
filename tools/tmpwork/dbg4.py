import io, sys
sys.path.insert(0, 'tools')
from build_ru_pages import load_ru_articles
from build_ru_pages3 import ru_title
patch = load_ru_articles()
for aid in ['premium', 'payment_stars', 'faq_telegram', 'commands_schedule', 'contact_email', 'glossary_premium']:
    io.open('tools/tmpwork/titles.txt', 'a', encoding='utf-8').write('%s :: %s%s' % (aid, ru_title(patch, aid, '?'), chr(10)))
print('titles ok')
s = io.open('website/index.html', encoding='utf-8').read()
import re
for key in ['Privacy Policy', '>premium<', '>your<', '~2.5 h']:
    ms = [m.start() for m in re.finditer(re.escape(key), s)][:3]
    ctx = []
    for i in ms:
        ctx.append(s[max(0,i-150):i+80].replace(chr(10), ' '))
    io.open('tools/tmpwork/idxctx.txt', 'a', encoding='utf-8').write('KEY ' + key + chr(10) + (chr(10).join(ctx)[:800]) + chr(10) + '---' + chr(10))
print('ctx ok')
