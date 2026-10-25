#!/usr/bin/env python
"""Generate server-rendered /ru/ pages so Russian search traffic can reach the site.

The Russian layer shipped so far is client-side only: lang.js + ru-content.js
swap strings after load from localStorage. A crawler is not obliged to run
JavaScript, so none of that text is indexable -- which is why Russian queries
find nothing. A hreflang cluster cannot fix that either: it is only
meaningful once two genuinely different documents exist.

This script builds the second document. The Russian source text already
exists in the repo:

  tools/ru_batches/help_*.py   full Russian help articles (title, body, FAQ)
  docs/ru/*.md                  Russian legal policies

It emits real static pages under website/ru/ and wires the cluster:

  * /ru/help/a/<id>.html for every article with Russian source text
  * /ru/legal/<doc>.html from docs/ru/*.md
  * <html lang="ru">, self-referencing canonical on the Russian URL
  * hreflang ru/en/x-default in BOTH directions, so Google can pair them
  * the /ru/ URLs added to sitemap.xml

A page is only generated where real Russian text exists. Emitting a /ru/ page
whose prose is mostly English would be a thin duplicate of the original and
would make the cluster worse than useless, so missing translations are
reported instead of papered over.

Idempotent: alternate-link injection strips any previous cluster before
writing, and /ru/ pages are fully regenerated each run.

Usage:  python tools/build_ru.py [--min-articles N]
"""
from __future__ import annotations

import argparse
import importlib.util
import io
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'website')
BUILD = os.path.join(SITE, '_build')
BATCH = os.path.join(ROOT, 'tools', 'ru_batches')
DOCS_RU = os.path.join(ROOT, 'docs', 'ru')

sys.path.insert(0, BUILD)
sys.path.insert(0, ROOT)

import build_help as bh          # noqa: E402
import build_static as bs       # noqa: E402

BASE = 'https://fastscheduler.github.io'
# Russian suffix. Cyrillic titles are much shorter than their English
# equivalents (one word becomes "Облако", six characters), so the English
# " — Fast Scheduler" suffix left 91 pages under the 30-character result
# threshold. "Справка" (Help Center) buys the extra weight naturally.
SUFFIX = ' — Справка Fast Scheduler'

ALT_MARK = '<!--fs:ru-alt-->'
END_MARK = '<!--/fs:ru-alt-->'
ALT_RE = re.compile(re.escape(ALT_MARK) + r'.*?' + re.escape(END_MARK) + r'\n?', re.S)


# --------------------------------------------------------------- corpus ----
def load_ru_articles():
    """Merge every help_*.py batch into one {article_id: translation} map."""
    patch = {}
    for f in sorted(os.listdir(BATCH)):
        if not (f.startswith('help_') and f.endswith('.py')):
            continue
        path = os.path.join(BATCH, f)
        spec = importlib.util.spec_from_file_location('ru_' + f[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for k, v in getattr(mod, 'PATCH', {}).items():
            # a few batch entries are plain strings (category labels), not
            # article records; only dicts carry title/content/faq
            if isinstance(v, dict):
                patch[k] = v
    return patch


def clean_ru(text):
    """Resolve template markers left in the Russian source.

    The batches were authored from the English articles, which carry
    {plan_limit} placeholders that build_help.fill_placeholders() resolves from
    src/core/plans.py, plus conditional @@STORAGE@@ markers that were never
    given a handler. Shipping either verbatim puts "{channels_prem}" and
    "@@STORAGE@@" on a public page.
    """
    if not text or not isinstance(text, str):
        return text
    try:
        text = bh.fill_placeholders(text)
    except Exception:
        pass
    text = re.sub(r'@@[A-Z_]+@@', '', text)
    return text


LEFTOVER = re.compile(r'\{[a-z_]+\}|@@[A-Z_]+@@')


def ru_meta(title, desc):
    """Russian title/description shaped for a search result."""
    t = bh.fit_title(clean_ru(title).strip() + SUFFIX)
    d = bh.smart_desc(bs.strip_html(clean_ru(desc)))
    return t, d


def alt_links(url_ru, url_en):
    return (ALT_MARK + '\n'
            '<link rel="alternate" hreflang="ru" href="%s">\n'
            '<link rel="alternate" hreflang="en" href="%s">\n'
            '<link rel="alternate" hreflang="x-default" href="%s">\n'
            % (url_ru, url_en, url_en) + END_MARK)


def _write(path, text, attempts=8, delay=0.25):
    """Retry transient Windows sharing violations (antivirus / indexer holding
    a handle). A single failure here would leave one English page out of the
    hreflang cluster, which is worse than a slow build."""
    for i in range(attempts):
        try:
            with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
                fh.write(text)
            return True
        except OSError:
            if i == attempts - 1:
                raise
            time.sleep(delay * (i + 1))
    return False


def inject_alts(path, block):
    """Insert/replace the hreflang cluster in an already-built page."""
    try:
        s = io.open(path, encoding='utf-8').read()
    except IOError:
        return False
    s = ALT_RE.sub('', s)
    if '</head>' not in s:
        return False
    s = s.replace('</head>', block + '</head>', 1)
    return _write(path, s)


# ------------------------------------------------------------ ru article ---
def build_article(aid, tr, cat_titles, title_override=None):
    """One Russian help article page, reusing the English page chrome."""
    title_ru = clean_ru(tr.get('title') or '').strip()
    body = clean_ru(tr.get('content') or '')
    faq = []
    for f in (tr.get('faq') or []):
        if not isinstance(f, dict):
            continue
        faq.append({'q': clean_ru(f.get('q')), 'a': clean_ru(f.get('a')),
                    'links': f.get('links') or []})
    if not (title_ru and (body or faq)):
        return None

    def slabel(lid):
        t = CAT_TITLES.get(lid)
        if t:
            return t
        tr2 = RU_ARTICLES.get(lid)
        if tr2 and tr2.get('title'):
            return clean_ru(tr2['title'])
        return lid.replace('_', ' ').capitalize()

    def slink(lid):
        if lid in RU_ARTICLES:
            return '%s.html' % bh.esc(lid)
        return '../../help.html'

    # render_faq expects every entry to carry 'links'; the Russian batches
    # omit it on some entries, so normalise before handing them over.
    faq = [{'q': f.get('q', ''), 'a': f.get('a', ''),
            'links': f.get('links') or []} for f in faq if f.get('q')]
    faq_html = bh.render_faq(faq, slink, slabel,
                             heading='Частые вопросы') if faq else ''
    desc = bs.strip_html(body) or title_ru
    t, d = ru_meta(title_ru if title_override is None else title_override, desc)

    url_en = BASE + '/help/a/%s.html' % aid
    url_ru = BASE + '/ru/help/a/%s.html' % aid
    cat_title = cat_titles.get(aid, 'Fast Scheduler')
    canonical = url_ru
    pub = bs.publish_date('help', aid)

    ld = bs.jsonld({
        '@context': 'https://schema.org', '@type': 'TechArticle',
        'headline': title_ru, 'description': d,
        'articleSection': cat_title,
        'inLanguage': 'ru',
        'author': {'@type': 'Organization', 'name': 'Fast Scheduler', 'url': BASE},
        'publisher': {'@type': 'Organization', 'name': 'Fast Scheduler', 'url': BASE,
                      'logo': {'@type': 'ImageObject', 'url': BASE + '/og-cover-v2.png'}},
        'mainEntityOfPage': canonical,
        'datePublished': pub, 'dateModified': pub,
        'isPartOf': {'@type': 'WebSite', 'name': 'Fast Scheduler',
                     'url': BASE + '/help.html'},
        'translationOfWork': {'@type': 'WebPage', 'url': url_en, 'inLanguage': 'en'},
    })
    ld_bread = bs.breadcrumb_ld([
        ('Fast Scheduler', BASE + '/'),
        ('Fast Scheduler', BASE + '/help.html'),
        (cat_title, BASE + '/help.html'),
        (title_ru, canonical),
    ])

    head = bs.page_head(t, d, canonical, extra_ld=ld + '\n' + ld_bread,
                        og_type='article', extra_meta=bs.article_meta(pub))
    # hreflang for the Russian document itself
    head = head + '\n' + alt_links(url_ru, url_en)

    crumbs = ('<nav class="hc-crumbs" aria-label="Хлебные крошки">'
              '<a href="../../../index.html">Fast Scheduler</a>' + bh.svg('chev') +
              '<a href="../../help.html">Центр помощи</a>' + bh.svg('chev') +
              '<span aria-current="page">%s</span></nav>' % bh.esc(title_ru))

    langbar = ('<p style="margin:0 0 18px;font-size:.92rem">'
               '<a href="%s" hreflang="en" lang="en">Читать на английском</a></p>'
               % url_en)

    cta = ('<div class="hc-cta"><div><b>Всё ещё нужна помощь?</b>'
           '<p>Встроенный помощник отвечает на те же вопросы, а каждый тикет '
           'читает человек.</p></div>'
           '<a class="btn" href="%s" target="_blank" rel="noopener noreferrer">'
           '%s Написать в Telegram</a></div>' % (bh.SUPPORT_URL, bh.svg('send')))

    content = ('<div class="wrap legal-layout" style="display:block;max-width:860px;'
               'margin:0 auto">\n  %s\n  %s\n  <article class="doc">\n'
               '    <h1>%s</h1>\n    <div class="hc-body">%s</div>\n    %s\n'
               '  </article>\n  %s\n</div>'
               % (crumbs, langbar, bh.esc(title_ru), body, faq_html, cta))

    return bs.page_shell(head, content, rel='../../..', lang='ru')


def _strip_h1(html):
    """The document title is rendered as the page <h1>; drop the duplicate
    the markdown produced so the page has exactly one."""
    return re.sub(r'<h1[^>]*>.*?</h1>\s*', '', html, count=1, flags=re.S)


def _en_category(help_dir, aid):
    """(English category name, is_landing_article) for an article.

    The landing article shares its id with its category (help/a/backup.html
    beside help/c/backup.html), which is why two different pages ended up
    titled "Начало работы (Getting Started)". build_static.py resolves the
    same collision in English with an "Overview" suffix; do the same here.
    """
    try:
        s = io.open(os.path.join(help_dir, aid + '.html'), encoding='utf-8').read()
    except IOError:
        return '', False
    m = re.search(r'<a href="\.\./c/([^/"]+)\.html">([^<]+)</a>', s)
    if not m:
        return '', False
    return bs.strip_html(m.group(2)), m.group(1) == aid


# ------------------------------------------------------------- ru legal ----
# The Russian policy sources, like the English ones, start at "## 1. ..." with
# no document title -- build_site.py supplies the English titles from
# LEGAL_PAGES, so the Russian titles must be supplied here. Without them the
# page fell back to the filename and rendered <h1>privacy</h1>.
LEGAL_TITLE_RU = {
    'privacy': 'Политика конфиденциальности',
    'terms': 'Условия использования',
    'refundpolicy': 'Политика возвратов',
}
LEGAL_DESC_RU = {
    'privacy': 'Как мы собираем, используем, раскрываем и защищаем ваши данные.',
    'terms': 'Правила использования Fast Scheduler и SetDate.',
    'refundpolicy': 'Как работают возвраты Premium, продление и chargeback.',
}

LEGAL_CHANGE_RU = {
    'privacy': ('В этой редакции уточнены перечень данных, обработка на сайте, '
                'шифрование и сроки хранения/удаления.',
                'Добавлено пояснение, что Fast Support и Fast Community — элементы бренда, '
                'а русская версия переведена с помощью ИИ.'),
    'terms': ('Уточнены лимиты тарифов, окончание Premium и льготный период, '
              'реферальные дни, удаление аккаунта и уведомления об изменениях сервиса.',
              'Добавлено пояснение о названиях Fast Support и Fast Community и о том, '
              'что «Fast» является частью бренда, а не обещанием скорости.'),
    'refundpolicy': ('Уточнены правила Telegram Stars, случаи возможного возврата, '
                     'отмена и отсутствие автопродления у предоплаченных тарифов.',
                     'Добавлено пояснение о названиях Fast Support и Fast Community и уведомление '
                     'о возможных неточностях AI-перевода.'),
}


def build_legal(name):
    src = os.path.join(DOCS_RU, name + '.md')
    if not os.path.exists(src):
        return None
    text = io.open(src, encoding='utf-8-sig').read()
    text = re.sub(r'\[\[([^\]]+)\]\]', r'<span data-ph="\1">[[\1]]</span>', text)
    import markdown
    html = markdown.markdown(text, extensions=['tables', 'fenced_code', 'nl2br', 'toc'])
    html = html.replace('<ul>', '<ol>').replace('</ul>', '</ol>')
    title_ru = LEGAL_TITLE_RU.get(name, name)
    d_src = '%s. %s' % (title_ru, LEGAL_DESC_RU.get(name, ''))
    t, d = ru_meta(title_ru, d_src)
    url_en = BASE + '/legal/%s.html' % name
    url_ru = BASE + '/ru/legal/%s.html' % name
    pub = bs.publish_date('legal', name)
    head = bs.page_head(t, d, url_ru, extra_ld=bs.jsonld({
        '@context': 'https://schema.org', '@type': 'WebPage',
        'name': t, 'description': d, 'url': url_ru, 'inLanguage': 'ru',
        'dateModified': pub, 'isPartOf': {'@type': 'WebSite', 'name': 'Fast Scheduler',
                                          'url': BASE + '/'}}), og_type='article')
    head = head + '\n<link rel="stylesheet" href="../../styles/mobile-fix.css?v=20261006a1">\n' + alt_links(url_ru, url_en)
    summary, detail = LEGAL_CHANGE_RU.get(name, ('В редакцию внесены уточнения.', ''))
    versions = ('<div class="ver-changes" role="note"><b>Что изменилось в этой редакции.</b> '
                '<q>%s</q><ul><li>%s</li></ul></div>' % (summary, detail))
    switcher = ('<div class="ver-dd"><button type="button" class="ver-pill" '
                'aria-haspopup="menu"><span class="ver-pill-dot" aria-hidden="true"></span>'
                '2026-10-01 · текущая версия</button><div class="glass-pop ver-menu" '
                'role="menu" aria-label="Версии документа"><div class="gp-head">Версии документа</div>'
                '<span class="gp-row ver-opt on" role="menuitem" aria-current="true">'
                '<span class="ver-v">2026-10-01</span><span class="ver-s">текущая · действует с 8 октября 2026</span></span>'
                '<a class="gp-row ver-opt" role="menuitem" href="../../legal/history/%s-2026-09-26.html">'
                '<span class="ver-v">2026-09-26</span><span class="ver-s">архивная версия (английский)</span></a>'
                '</div></div>' % name)
    body = ('<div class="wrap legal" style="max-width:860px;margin:0 auto">'
            '<p><a href="%s" hreflang="en" lang="en">Читать на английском</a></p>'
            '<article class="doc"><h1>%s</h1><p class="updated">Последнее обновление: 1 октября 2026</p>'
            '<p class="effective">Действует с 8 октября 2026 года. Продолжение использования Сервисов после этой даты означает принятие обновлённой редакции.</p>%s%s'
            '<div class="hc-body">%s</div></article></div>'
            % (url_en, bh.esc(title_ru), versions, switcher, _strip_h1(html)))
    return bs.page_shell(head, body, rel='../..', lang='ru')


# ----------------------------------------------------------------- main ----
RU_ARTICLES = {}
CAT_TITLES = {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min-articles', type=int, default=1,
                    help='refuse to emit a /ru/ help section below this many pages')
    a = ap.parse_args()

    global RU_ARTICLES, CAT_TITLES
    RU_ARTICLES = load_ru_articles()

    # category id -> Russian title, from the batches themselves
    for aid, tr in RU_ARTICLES.items():
        # these become "related topic" chip labels, so they need the same
        # marker cleanup as the body text
        CAT_TITLES.setdefault(aid, clean_ru(tr.get('title') or ''))

    help_dir = os.path.join(SITE, 'help', 'a')
    built = sorted(f[:-5] for f in os.listdir(help_dir) if f.endswith('.html'))

    # article -> its English category, for breadcrumb / articleSection
    import build_static
    src = io.open(os.path.join(BUILD, 'build_static.py'), encoding='utf-8').read()
    cat_of = {}
    for m in re.finditer(r"n\['c'\]\s*==\s*'([a-z_]+)'|'c':\s*'([a-z_]+)'", src):
        cat_of.setdefault(m.group(1) or m.group(2), m.group(1) or m.group(2))

    out_dir = os.path.join(SITE, 'ru', 'help', 'a')
    os.makedirs(out_dir, exist_ok=True)

    # Two-pass title disambiguation, mirroring build_static.py: the Russian
    # corpus repeats article names across categories exactly as the English
    # one does ("Экспорт" is both the Export guide and the glossary entry), so
    # colliding titles get their English category appended. Left alone, eight
    # pairs of pages competed for the same result.
    base_titles = {}
    for aid in built:
        tr = RU_ARTICLES.get(aid)
        if tr:
            base_titles[aid] = clean_ru(tr.get('title') or '').strip()
    counts = {}
    for v in base_titles.values():
        counts[v] = counts.get(v, 0) + 1
    en_cat = {}
    landing = set()
    for aid in built:
        en_cat[aid], is_landing = _en_category(help_dir, aid)
        if is_landing:
            landing.add(aid)

    page_title = {}
    for aid, base in base_titles.items():
        if aid in landing:
            page_title[aid] = '%s — Обзор' % base
        elif counts[base] > 1 and en_cat.get(aid):
            page_title[aid] = '%s (%s)' % (base, en_cat[aid])
        else:
            page_title[aid] = base
    written, linked, skipped = [], 0, []
    leftovers = {}
    for aid in built:
        tr = RU_ARTICLES.get(aid)
        if not tr:
            skipped.append(aid)
            continue
        html = build_article(aid, tr, CAT_TITLES, title_override=page_title.get(aid))
        if not html:
            skipped.append(aid)
            continue
        html = html.replace('<html lang="en"', '<html lang="ru"')
        left = LEFTOVER.findall(html)
        if left:
            # never publish an unresolved template marker
            io.open(os.path.join(out_dir, aid + '.html'), 'w',
                    encoding='utf-8', newline='\n').write(html)
            leftovers.setdefault(aid, sorted(set(left))[:4])
        else:
            leftovers.pop(aid, None)
        io.open(os.path.join(out_dir, aid + '.html'), 'w',
                encoding='utf-8', newline='\n').write(html)
        written.append(aid)
        # cluster the English original back to the Russian page
        if inject_alts(os.path.join(help_dir, aid + '.html'),
                       alt_links(BASE + '/ru/help/a/%s.html' % aid,
                                 BASE + '/help/a/%s.html' % aid)):
            linked += 1

    legal_dir = os.path.join(SITE, 'ru', 'legal')
    os.makedirs(legal_dir, exist_ok=True)
    legal_written = []
    for name in ('privacy', 'terms', 'refundpolicy'):
        html = build_legal(name)
        if not html:
            continue
        html = html.replace('<html lang="en"', '<html lang="ru"')
        io.open(os.path.join(legal_dir, name + '.html'), 'w',
                encoding='utf-8', newline='\n').write(html)
        legal_written.append(name)
        inject_alts(os.path.join(SITE, 'legal', name + '.html'),
                    alt_links(BASE + '/ru/legal/%s.html' % name,
                              BASE + '/legal/%s.html' % name))

    # drop stale /ru/ files for articles we no longer translate
    keep = set(aid + '.html' for aid in written)
    for f in os.listdir(out_dir):
        if f.endswith('.html') and f not in keep:
            os.remove(os.path.join(out_dir, f))

    ru_urls = [BASE + '/ru/help/a/%s.html' % x for x in written] + \
              [BASE + '/ru/legal/%s.html' % x for x in legal_written]
    for hub in ('ru/index.html', 'ru/help.html'):
        if os.path.isfile(os.path.join(SITE, hub)):
            u = BASE + '/' + hub.replace('index.html', '')
            if u not in ru_urls:
                ru_urls.append(u)

    # sitemap: drop any previous /ru/ entries, then re-add
    sm_path = os.path.join(SITE, 'sitemap.xml')
    sm = io.open(sm_path, encoding='utf-8').read()
    sm = re.sub(r'\s*<url>\s*<loc>[^<]*/ru/[^<]*</loc>.*?</url>', '', sm, flags=re.S)
    lastmod = bs.publish_date('site', 'ru')
    add = ''.join('  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n'
                  '    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>\n'
                  % (u, lastmod) for u in ru_urls)
    sm = sm.replace('</urlset>', add + '</urlset>')
    io.open(sm_path, 'w', encoding='utf-8', newline='\n').write(sm)

    print('RU help articles written : %d of %d built (%.1f%%)' % (
        len(written), len(built), 100.0 * len(written) / max(1, len(built))))
    print('RU legal pages written   : %d  (%s)' % (
        len(legal_written), ', '.join(legal_written)))
    print('English pages clustered  : %d help + %d legal' % (
        linked, len(legal_written)))
    print('sitemap /ru/ URLs        : %d' % len(ru_urls))
    print('no Russian source yet    : %d' % len(skipped))
    if skipped:
        print('  %s' % ', '.join(skipped[:20]))
    if leftovers:
        print('[error] %d page(s) still contain unresolved template markers:' % len(leftovers))
        for aid, marks in list(leftovers.items())[:10]:
            print('   %-28s %s' % (aid, ', '.join(marks)))
        return 1
    if len(written) < a.min_articles:
        print('\n[error] only %d articles translated (min %d) - not publishing a '
              '/ru/ help section this thin' % (len(written), a.min_articles))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
