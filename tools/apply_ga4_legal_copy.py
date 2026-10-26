"""Switch the legal documents from "Google Tag Manager container GTM-P9L5JD26"
to the Google tag / GA4 measurement ID that is actually loaded (G-ESSXSFV4XZ).

The GTM container was installed but has never contained a tag, so the wording
described something that collected nothing. Applies the same wording to the
Markdown sources and to the generated HTML copies (root + website/ mirror).

Idempotent: already-updated files are reported and left alone.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EN = [
    ('consent-gated analytics through Google Tag Manager); and',
     'consent-gated analytics through Google Analytics 4); and'),

    ('the Website uses <strong>Google Tag Manager</strong> (container '
     '<code>GTM-P9L5JD26</code>, Google Ireland Limited / Google LLC) to load '
     '<strong>Google Analytics 4</strong> measurement tags.',
     'the Website loads <strong>Google Analytics 4</strong> through Google\'s '
     '<code>gtag.js</code> (measurement ID <code>G-ESSXSFV4XZ</code>, Google '
     'Ireland Limited / Google LLC).'),

    ('the Website uses **Google Tag Manager** (container `GTM-P9L5JD26`, Google '
     'Ireland Limited / Google LLC) to load **Google Analytics 4** measurement tags.',
     'the Website loads **Google Analytics 4** through Google\'s `gtag.js` '
     '(measurement ID `G-ESSXSFV4XZ`, Google Ireland Limited / Google LLC).'),

    ('**Nothing loads before you choose.** The Tag Manager script is not merely '
     'paused or configured off',
     '**Nothing loads before you choose.** The analytics script is not merely '
     'paused or configured off'),

    ('<strong>Nothing loads before you choose.</strong> The Tag Manager script is '
     'not merely paused or configured off',
     '<strong>Nothing loads before you choose.</strong> The analytics script is '
     'not merely paused or configured off'),

    ('<code>_ga_&lt;container-id&gt;</code>', '<code>_ga_&lt;property-id&gt;</code>'),
    ('`_ga_<container-id>`', '`_ga_<property-id>`'),

    ('and we do not enable Google Signals or ad-personalisation in the container.',
     'and we do not enable Google Signals or ad-personalisation.'),

    ('The only third-party code that can run on the Website is <strong>Google Tag '
     'Manager with Google Analytics 4</strong>, and only after',
     'The only third-party code that can run on the Website is <strong>Google '
     'Analytics 4</strong>, and only after'),

    ('The only third-party code that can run on the Website is **Google Tag Manager '
     'with Google Analytics 4**, and only after',
     'The only third-party code that can run on the Website is **Google Analytics '
     '4**, and only after'),

    ('Website analytics via Google Tag Manager / Google Analytics 4 (pages',
     'Website analytics via Google Analytics 4 (pages'),

    ('Analytics on the Website runs through Google Tag Manager '
     '(<code>GTM-P9L5JD26</code>, loading Google Analytics 4) and is loaded only after',
     'Analytics on the Website runs through Google Analytics 4 '
     '(<code>G-ESSXSFV4XZ</code>, loaded with <code>gtag.js</code>) and is loaded only after'),

    ('Analytics on the Website runs through Google Tag Manager (`GTM-P9L5JD26`, '
     'loading Google Analytics 4) and is loaded only after',
     'Analytics on the Website runs through Google Analytics 4 (`G-ESSXSFV4XZ`, '
     'loaded with `gtag.js`) and is loaded only after'),
]

RU = [
    ('на Сайте используется <strong>Google Tag Manager</strong> (контейнер '
     '<code>GTM-P9L5JD26</code>, Google Ireland Limited / Google LLC), через '
     'который загружаются счётчики <strong>Google Analytics 4</strong>.',
     'на Сайте используется <strong>Google Analytics 4</strong> (счётчик '
     '<code>G-ESSXSFV4XZ</code>, загружается через <code>gtag.js</code>, Google '
     'Ireland Limited / Google LLC).'),

    ('<strong>До вашего выбора ничего не загружается.</strong> Скрипт Tag Manager '
     'не «приостановлен»',
     '<strong>До вашего выбора ничего не загружается.</strong> Скрипт аналитики '
     'не «приостановлен»'),

    ('— <strong>Google Tag Manager с Google Analytics 4</strong>, и только после',
     '— <strong>Google Analytics 4</strong>, и только после'),

    ('Аналитика Сайта через Google Tag Manager / Google Analytics 4',
     'Аналитика Сайта через Google Analytics 4'),

    ('Аналитика на Сайте работает через Google Tag Manager '
     '(<code>GTM-P9L5JD26</code>, загружает Google Analytics 4)',
     'Аналитика на Сайте работает через Google Analytics 4 '
     '(<code>G-ESSXSFV4XZ</code>, загружается через <code>gtag.js</code>)'),

    # Markdown sources use ** and backticks instead of <strong>/<code>
    ('на Сайте используется **Google Tag Manager** (контейнер `GTM-P9L5JD26`, '
     'Google Ireland Limited / Google LLC), через который загружаются счётчики '
     '**Google Analytics 4**.',
     'на Сайте используется **Google Analytics 4** (счётчик `G-ESSXSFV4XZ`, '
     'загружается через `gtag.js`, Google Ireland Limited / Google LLC).'),

    ('**До вашего выбора ничего не загружается.** Скрипт Tag Manager не '
     '«приостановлен»',
     '**До вашего выбора ничего не загружается.** Скрипт аналитики не '
     '«приостановлен»'),

    ('— **Google Tag Manager с Google Analytics 4**, и только после',
     '— **Google Analytics 4**, и только после'),

    ('Аналитика на Сайте работает через Google Tag Manager (`GTM-P9L5JD26`, '
     'загружает Google Analytics 4)',
     'Аналитика на Сайте работает через Google Analytics 4 (`G-ESSXSFV4XZ`, '
     'загружается через `gtag.js`)'),
]

FILES = [
    ('docs/privacy.md', EN),
    ('docs/terms.md', EN),
    ('docs/ru/privacy.md', RU),
    ('docs/ru/terms.md', RU),
    ('legal/privacy.html', EN),
    ('legal/terms.html', EN),
    ('ru/legal/privacy.html', RU),
    ('ru/legal/terms.html', RU),
    ('website/legal/privacy.html', EN),
    ('website/legal/terms.html', EN),
    ('website/ru/legal/privacy.html', RU),
    ('website/ru/legal/terms.html', RU),
]

total = 0
for rel, pairs in FILES:
    path = os.path.join(REPO, rel)
    if not os.path.exists(path):
        print('MISSING', rel)
        continue
    with open(path, encoding='utf-8') as f:
        text = f.read()
    before = text
    hits = 0
    for old, new in pairs:
        if old in text:
            text = text.replace(old, new)
            hits += 1
    if text != before:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        total += hits
        print('%2d replacements  %s' % (hits, rel))
    else:
        print('   unchanged      %s' % rel)

print('\ntotal replacements:', total)

stale = []
for rel, _ in FILES:
    path = os.path.join(REPO, rel)
    if not os.path.exists(path):
        continue
    with open(path, encoding='utf-8') as f:
        t = f.read()
    if 'Tag Manager' in t or 'GTM-P9L5JD26' in t:
        stale.append(rel)
print('files still mentioning Tag Manager / GTM id:', stale or 'none')
sys.exit(1 if stale else 0)
