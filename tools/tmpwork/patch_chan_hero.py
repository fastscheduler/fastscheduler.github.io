# -*- coding: utf-8 -*-
"""One-shot: hero channel -> real Telegram iOS look + static image fallbacks."""
import io
import re
import sys

ARTS = [l for l in io.open('tools/tmpwork/chan_art.txt', encoding='utf-8').read().splitlines() if l]
assert len(ARTS) == 4, len(ARTS)

OLD_HEAD = """              <div class="sl-head chan-head">
                <svg class="tg-back" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
                <span class="chan-avatar" aria-hidden="true">FT</span>
                <div class="sl-titles"><span class="sl-name">fastschedule_test3</span><span class="sl-sub">1 284 subscribers</span></div>
                <span class="hd-ics" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20.4 20.4l-3.9-3.9"/></svg>
                  <svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="12" cy="19" r="1.6"/></svg>
                </span>
              </div>"""

NEW_HEAD = """              <div class="sl-head chan-head">
                <svg class="tg-back" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
                <span class="tg-back-t">{back}</span>
                <div class="sl-titles chan-titles"><span class="sl-name">Fast Schedule</span><span class="sl-sub">@fastschedule_test3</span></div>
                <span class="chan-avatar" aria-hidden="true">FS</span>
              </div>"""

OLD_FOOT = """              <div class="sl-foot chan-compose"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M4 9.5v5a1.5 1.5 0 0 0 1.5 1.5H8l8.5 4.3V3.7L8 8H5.5A1.5 1.5 0 0 0 4 9.5z"/><path d="M19.5 8.6a5 5 0 0 1 0 6.8"/><path d="M17.6 6.6a8 8 0 0 1 0 10.8"/></svg><span>Channel · only admins can post</span></div>"""

NEW_FOOT = """              <div class="sl-foot chan-actions" aria-hidden="true">
                <span class="ca-btn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20.4 20.4l-3.9-3.9"/></svg></span>
                <span class="ca-mute">{mute}</span>
                <span class="ca-btn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></span>
                <span class="ca-btn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13M5 12v9h14v-9"/><path d="M12 8s-4 0-5.5-1.5S5 3.5 6.5 3.5 12 8 12 8zm0 0s4 0 5.5-1.5S19 3.5 17.5 3.5 12 8 12 8z"/></svg></span>
              </div>"""

SENDER = '<span class="cp-sender"><b>Fast Schedule</b><i>{chantag}</i></span>'

COMMENTS = ('<span class="cp-comments">'
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>'
            '<b>{leave}</b>'
            '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M9 18l6-6-6-6"/></svg></span>')

DATE_BADGE = '<div class="cp-date" id="chanDate">{today}</div>'

LOCALES = {
    'website/index.html': {'back': 'Chats', 'chantag': 'channel',
                            'leave': 'Leave a comment', 'mute': 'Mute', 'today': 'Today'},
    'website/ru/index.html': {'back': 'Чаты', 'chantag': 'канал',
                              'leave': 'Оставить комментарий', 'mute': 'Выкл. звук',
                              'today': 'Сегодня'},
}


def patch(path, loc):
    s = io.open(path, encoding='utf-8').read()
    assert s.count(OLD_HEAD) == 1, (path, 'head', s.count(OLD_HEAD))
    s = s.replace(OLD_HEAD, NEW_HEAD.format(**loc))
    assert s.count(OLD_FOOT) == 1, (path, 'foot', s.count(OLD_FOOT))
    s = s.replace(OLD_FOOT, NEW_FOOT.format(**loc))
    feed_key = '<div class="chan-msgs" id="chanFeed">'
    assert s.count(feed_key) == 1, (path, 'feed', s.count(feed_key))
    s = s.replace(feed_key, feed_key + DATE_BADGE.format(**loc), 1)

    idx = [0]

    def post_sub(m):
        cls, extra, inner = m.group(1), m.group(2) or '', m.group(3)
        art = ARTS[idx[0] % 4]
        idx[0] += 1
        inner = inner.replace('<span class="chan-media"></span>',
                              '<span class="chan-media" style="background-image:' + art + '"></span>')
        inner = inner.replace('<span class="chan-media" id="chanImg">',
                              '<span class="chan-media" id="chanImg" style="background-image:' + art + '">')
        inner = re.sub(r'<span class="cp-share">.*?</span>', '', inner, flags=re.S)
        return ('<div class="chan-msg' + cls + '"' + extra + '>' + SENDER.format(**loc)
                + inner + COMMENTS.format(**loc) + '</div>')

    s2, n = re.subn(r'<div class="chan-msg(?="| )([^"]*)"( [^>]*)?>(.*?)</div>', post_sub, s, flags=re.S)
    assert n == 5, (path, 'posts', n)
    assert '<span class="chan-media"></span>' not in s2, (path, 'bare media left')
    assert 'cp-share' not in s2, (path, 'share left')
    assert s2.count('cp-sender') == 5, (path, 'sender', s2.count('cp-sender'))
    assert s2.count('cp-comments') == 5, (path, 'comments', s2.count('cp-comments'))
    io.open(path, 'w', encoding='utf-8', newline='').write(s2)
    print('patched ' + path)


for p, loc in LOCALES.items():
    patch(p, loc)
