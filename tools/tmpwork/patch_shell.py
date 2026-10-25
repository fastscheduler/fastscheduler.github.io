import io
p = 'website/_build/build_static.py'
s = io.open(p, encoding='utf-8').read()

old_sig = "def page_shell(title_html, body, rel='../..'):"
assert old_sig in s, 'sig miss'

ru_func = '''def page_shell_ru(title_html, body, rel='../..'):
    """Server-side Russian chrome for /ru/ pages (EN shell untouched)."""
    R = rel + '/ru'
    _menu = bh.settings_menu(bh.SUPPORT_URL, 'ru')
    NAV = bh.unified_nav(rel, bh.BOT_URL, _menu, lang='ru')
    FOOT = ('<footer class="site">' + chr(10)
            + '  <div class="wrap foot">' + chr(10)
            + '    <span class="copy">' + bh.tr('footer_copy', 'ru') + '</span>' + chr(10)
            + '    <nav class="links" aria-label="' + bh.tr('footer_legal', 'ru') + '">' + chr(10)
            + '      <a href="' + R + '/legal/terms.html">' + bh.tr('footer_terms', 'ru') + '</a>' + chr(10)
            + '      <a href="' + R + '/legal/privacy.html">' + bh.tr('footer_privacy', 'ru') + '</a>' + chr(10)
            + '      <a href="' + R + '/legal/refundpolicy.html">' + bh.tr('footer_refunds', 'ru') + '</a>' + chr(10)
            + '      <a href="' + R + '/blog/index.html">' + bh.tr('blog', 'ru') + '</a>' + chr(10)
            + '      <a href="' + R + '/help.html">' + bh.tr('footer_help', 'ru') + '</a>' + chr(10)
            + '    </nav>' + chr(10)
            + '  </div>' + chr(10)
            + '</footer>')
    return ('<!DOCTYPE html>' + chr(10)
            + '<html lang="ru" data-theme="light">' + chr(10)
            + '<head>' + chr(10)
            + NOFLASH + chr(10)
            + title_html + chr(10)
            + '<link rel="stylesheet" href="' + rel + '/styles/main.css?v=20261005e3">' + chr(10)
            + '<link rel="stylesheet" href="' + rel + '/styles/hotkeys-modal.css?v=20260930a1">' + chr(10)
            + '<style>' + HC_COMPONENT_CSS + chr(10)
            + '  </style>' + chr(10)
            + '</head>' + chr(10)
            + '<body>' + chr(10)
            + NAV + chr(10)
            + '<main class="legal">' + chr(10)
            + body + chr(10)
            + '</main>' + chr(10)
            + FOOT + chr(10)
            + '<script src="' + rel + '/scripts/theme.js?v=20260930a1"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/settings.js?v=20261005d1"></script>' + chr(10)
            + '  <script src="/scripts/lang.js?v=20261001a1"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/help-search.js?v=20260930a1"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/hotkeys-modal.js?v=20260930a2"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/help-ai.js?v=20260930a1"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/hotkeys.js?v=20261005d1"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/scroll-jump.js?v=20261005a1"></script>' + chr(10)
            + '<script src="' + rel + '/scripts/article-nav.js?v=20260930a2"></script>' + chr(10)
            + '</body>' + chr(10)
            + '</html>')


def page_shell(title_html, body, rel='../..', lang='en'):
    """rel: prefix for assets from the page location (help/a|c are 2 levels deep)."""
    if lang == 'ru':
        return page_shell_ru(title_html, body, rel)
'''

s = s.replace(old_sig, ru_func, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('shell patched')
