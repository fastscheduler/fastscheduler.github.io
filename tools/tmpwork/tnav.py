import io, sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'website', '_build'))
import build_help as bh
menu_en = bh.settings_menu(bh.SUPPORT_URL, 'en')
nav_en = bh.unified_nav('../..', bh.BOT_URL, menu_en)
nav_ru = bh.unified_nav('../..', bh.BOT_URL, bh.settings_menu(bh.SUPPORT_URL, 'ru'), lang='ru')
io.open('tools/tmpwork/nav_en.html', 'w', encoding='utf-8').write(nav_en)
io.open('tools/tmpwork/nav_ru.html', 'w', encoding='utf-8').write(nav_ru)
print('en:', len(nav_en), 'ru:', len(nav_ru))
