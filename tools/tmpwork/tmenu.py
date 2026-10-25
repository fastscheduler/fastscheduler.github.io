import io, sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'website', '_build'))
import build_help as bh
en = bh.settings_menu(bh.SUPPORT_URL, 'en')
ru = bh.settings_menu(bh.SUPPORT_URL, 'ru')
io.open('tools/tmpwork/menu_en.html', 'w', encoding='utf-8').write(en)
io.open('tools/tmpwork/menu_ru.html', 'w', encoding='utf-8').write(ru)
print('en:', len(en), 'ru:', len(ru))
