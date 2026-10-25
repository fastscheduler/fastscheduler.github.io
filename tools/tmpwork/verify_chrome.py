import io, os
ROOT = os.getcwd()
checks = []
p = 'website/ru/help/a/qa_free_limits.html'
s = io.open(p, encoding='utf-8').read()
en_marks = ['<span>Dark mode</span>', '<span>Support chat</span>', '>Terms<', '>Privacy<',
            '>Refunds<', 'placeholder="Search the help center', '>Popular articles<',
            '<span>Open Help Center</span>', '<span>Blog</span>', '>Help Center<', '>Open Bot<']
ru_marks = ['<span>Тёмная тема</span>', '<span>Чат поддержки</span>', '>Условия<', '>Конфиденциальность<',
            '>Возвраты<', 'placeholder="Поиск по справке', '>Популярные статьи<',
            '<span>Открыть Центр помощи</span>', '<span>Блог</span>', '>Центр помощи<', '>Открыть бота<']
bad_en = [m for m in en_marks if m in s]
miss_ru = [m for m in ru_marks if m not in s]
out = ['EN-LEFT: %d %s' % (len(bad_en), bad_en[:6]), 'RU-MISS: %d %s' % (len(miss_ru), miss_ru[:6])]
p2 = 'website/ru/legal/privacy.html'
s2 = io.open(p2, encoding='utf-8').read()
bad2 = [m for m in en_marks if m in s2]
out.append('LEGAL EN-LEFT: %d %s' % (len(bad2), bad2[:6]))
io.open('tools/tmpwork/chrome_report.txt', 'w', encoding='utf-8').write(chr(10).join(out))
print('report written')
