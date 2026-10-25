# -*- coding: utf-8 -*-
"""Add a short "Keep reading" line with real cross-links to core articles.

Every target is an existing page next to the source page, so the links work
from help/a/ without a rewrite. Idempotent: pages that already carry the block
are skipped.
"""
import io
import os
import re

MAP = {
    'start': [
        ('guide_overview', 'The complete guide to every menu and button'),
        ('guide_schedule_format', 'How to write a schedule'),
    ],
    'getting_started': [
        ('guide_overview', 'The complete guide to every menu and button'),
        ('connect_bot', 'Connecting a sender bot'),
    ],
    'scheduling': [
        ('guide_schedule_format', 'Dates, text and inline buttons in one message'),
        ('guide_batch_file', 'Bulk scheduling from a .txt file'),
    ],
    'schedule_one_time': [
        ('guide_schedule_format', 'The exact schedule format'),
        ('guide_media_modes', 'Media modes explained'),
    ],
    'schedule_media': [
        ('guide_media_modes', 'Normal, Random, Sequential and From Storage'),
        ('media_storage', 'Media Storage'),
    ],
    'message_list': [
        ('guide_fix_duplicates', 'Editing, duplicating or deleting one post'),
        ('edit', 'Edit a scheduled message'),
    ],
    'edit': [
        ('guide_fix_duplicates', 'Duplicates and mistakes'),
        ('message_list', 'Message List'),
    ],
    'delete': [
        ('guide_fix_duplicates', 'Deleting one post without wiping the queue'),
        ('message_list', 'Message List'),
    ],
    'import_data': [
        ('guide_batch_file', 'Scheduling from a .txt file'),
        ('import_formats', 'Supported import formats'),
    ],
    'formatting': [
        ('guide_schedule_format', 'Button layouts inside a schedule'),
        ('glossary_recurring', 'Recurring posts'),
    ],
}

CLOSE = '</div>\n    \n'


def build(links):
    items = ' &middot; '.join('<a href="%s.html">%s</a>' % (tid, label) for tid, label in links)
    return '<p class="hc-more"><b>Keep reading:</b> %s</p>' % items


for aid, links in MAP.items():
    rel = os.path.join('help', 'a', aid + '.html')
    for base in ('', 'website'):
        path = os.path.join(base, rel) if base else rel
        if not os.path.exists(path):
            print('[skip]', path)
            continue
        s = io.open(path, encoding='utf-8').read()
        # Repair mode: drop any block this script inserted earlier so a re-run
        # always lands inside the body, exactly once.
        s = re.sub(r'\s*<p class="hc-more">.*?</p>', '', s, count=1)
        i = s.find('<div class="hc-body">')
        if i == -1:
            print('[warn] no hc-body in', path)
            continue
        # Walk to the </div> that closes hc-body, counting nested divs.
        depth = 1
        pos = i + len('<div class="hc-body">')
        close_at = -1
        while depth > 0:
            nxt_open = s.find('<div', pos)
            nxt_close = s.find('</div>', pos)
            if nxt_close == -1:
                break
            if nxt_open != -1 and nxt_open < nxt_close:
                depth += 1
                pos = nxt_open + 4
            else:
                depth -= 1
                if depth == 0:
                    close_at = nxt_close
                pos = nxt_close + 6
        if close_at == -1:
            print('[warn] unbalanced hc-body in', path)
            continue
        s = s[:close_at] + build(links) + s[close_at:]
        io.open(path, 'w', encoding='utf-8', newline='\n').write(s)
        print('[ok] linked', path)
