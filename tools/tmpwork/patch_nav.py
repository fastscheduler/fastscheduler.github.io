import io
p = 'website/_build/build_help.py'
s = io.open(p, encoding='utf-8').read()
BS = chr(92)
insert = '    t = lambda k: tr(k, lang)  # noqa: E731' + chr(10) + "    R = rel + ('/ru' if lang == 'ru' else '')" + chr(10)
reps = [
("    cta = cta_html or (f'<a class=" + chr(34) + "btn btn-primary nav-cta" + chr(34) + " data-cta-short=" + chr(34) + "Open" + chr(34),
 insert + "    cta = cta_html or (f'<a class=" + chr(34) + "btn btn-primary nav-cta" + chr(34) + " data-cta-short=" + chr(34) + "{t(" + chr(34) + "open_short" + chr(34) + ")}" + chr(34)),
("<span>Open Bot</span>'", "<span>{t(" + chr(34) + "open_bot" + chr(34) + ")}</span>'"),
("aria-label=" + chr(34) + "Settings" + chr(34) + " data-hk=", "aria-label=" + chr(34) + "{t(" + chr(34) + "settings" + chr(34) + ")}" + chr(34) + " data-hk="),
('role="menu" aria-label="Settings">', 'role="menu" aria-label="{t("settings")}">'),
('<a class="brand" href="{rel}/index.html" aria-label=', '<a class="brand" href="{R}/index.html" aria-label='),
("Fast Scheduler " + BS + "u2014 home", '{t("brand_home")}'),
('aria-label="Help center quick search">', 'aria-label="{t("pop_aria")}">'),
("placeholder=" + chr(34) + "Search the help center" + chr(8230) + chr(34), "placeholder=" + chr(34) + "{t(" + chr(34) + "search_ph" + chr(34) + ")}" + chr(34)),
('aria-label="Search the help center">', 'aria-label="{t("search_aria")}">'),
(">Popular articles</div>", ">{t(" + chr(34) + "popular" + chr(34) + ")}</div>"),
("href=" + chr(34) + "{rel}/help.html" + chr(34) + ">", "href=" + chr(34) + "{R}/help.html" + chr(34) + ">"),
("<span>Open Help Center</span>", "<span>{t(" + chr(34) + "open_help" + chr(34) + ")}</span>"),
("href=" + chr(34) + "{rel}/blog/index.html" + chr(34) + ">{svg(" + chr(34) + "megaphone" + chr(34) + ")}<span>Blog</span>", "href=" + chr(34) + "{R}/blog/index.html" + chr(34) + ">{svg(" + chr(34) + "megaphone" + chr(34) + ")}<span>{t(" + chr(34) + "blog" + chr(34) + ")}</span>"),
("href=" + chr(34) + "{rel}/help.html" + chr(34) + " " + chr(39) + chr(10), "href=" + chr(34) + "{R}/help.html" + chr(34) + " " + chr(39) + chr(10)),
("<span>Help Center</span></a>", "<span>{t(" + chr(34) + "help_center" + chr(34) + ")}</span></a>"),
]
for old, new in reps:
    assert old in s, 'MISS: ' + old[:60]
    s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('nav patched', len(reps))
