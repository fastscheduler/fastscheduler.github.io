# -*- coding: utf-8 -*-
"""Rewrite the bot's first screen (``tutorial_welcome``) in all three languages.

That screen is the only thing a new user sees before any setup, and it used to
say "two steps and your channel is automated" without ever saying what the bot
was or why to keep it — people opened it, read the two steps, and still asked
"what is this?". The replacement leads with the product, the reasons to use it
and the features that make it worth the two minutes, then the same two steps.

Text lives in tools/help_v2_getting_started.py (WELCOME) so the bot screen and
the "Get Started" article are edited in one place.

    python tools/apply_onboarding_intro.py           # apply
    python tools/apply_onboarding_intro.py --check   # report only
"""

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from help_v2_getting_started import WELCOME  # noqa: E402

KEY = 'tutorial_welcome'


def main(argv):
    check_only = '--check' in argv
    changed = 0
    for lang in ('en', 'es', 'ru'):
        path = os.path.join(ROOT, 'translations', lang + '.json')
        with io.open(path, encoding='utf-8-sig') as f:
            data = json.load(f)
        text = WELCOME[lang]
        if len(text) > 4000:
            raise SystemExit('%s: welcome text is %d chars (Telegram limit 4096)'
                             % (lang, len(text)))
        if data.get(KEY) == text:
            print('%s: already up to date (%d chars)' % (lang, len(text)))
            continue
        changed += 1
        if check_only:
            print('%s: would replace (%d chars)' % (lang, len(text)))
            continue
        data[KEY] = text
        with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print('%s: wrote %s (%d chars)' % (lang, KEY, len(text)))
    if check_only:
        print('check only — nothing written (%d would change)' % changed)


if __name__ == '__main__':
    main(sys.argv[1:])
