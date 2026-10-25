import io, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'website', 'ru', 'help', 'a')
IDS = """ms_bulk qa_add_channel_guide qa_backup_full_guide qa_bot_management qa_delete_data qa_duplicate_posts qa_edit_scheduled_post qa_formatting qa_free_limits qa_fsback_vs_fspback qa_media_storage_guide qa_media_types qa_move_channel_account qa_pay_stars_crypto qa_post_not_sent qa_premium_worth qa_private_channel_connect qa_recurring_guide qa_refund_how qa_schedule_many_at_once qa_sender_bot_required qa_setdate_bulk qa_signature_guide qa_stats_views qa_timezone_wrong_time qa_timezones qa_what_is_fast_scheduler qa_which_plan referral_beta referral_credit referral_verify tg_best_posting_times tg_channel_vs_group tg_channels_explained""".split()
CYR = re.compile(r'[\u0410-\u044f\u0401\u0451]')
out = []
bad = 0
for aid in IDS:
    p = os.path.join(D, aid + '.html')
    if not os.path.exists(p):
        out.append('MISSING %s' % aid); bad += 1; continue
    s = io.open(p, encoding='utf-8').read()
    errs = []
    if '<html lang="ru"' not in s: errs.append('no-lang-ru')
    m = re.search(r'<article class="doc">(.*?)</article>', s, re.S)
    body = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m.group(1))).strip() if m else ''
    if not m: errs.append('no-article')
    ncyr = len(CYR.findall(body)); nlat = len(re.findall(r'[A-Za-z]', body))
    if ncyr < 200: errs.append('thin-ru-%d' % ncyr)
    if re.search(r'@@[A-Z_]+@@|\{[a-z_]+\}', body): errs.append('leftover-marker')
    if not re.search(r'<h1>.+</h1>', m.group(1) if m else ''): errs.append('no-h1')
    if '/ru/help/a/%s.html' % aid not in s: errs.append('no-self-canonical')
    if 'hreflang="en"' not in s: errs.append('no-hreflang')
    st = 'OK cyr=%d lat=%d' % (ncyr, nlat) if not errs else 'FAIL ' + ','.join(errs)
    if errs: bad += 1
    out.append('%-28s %s' % (aid, st))
out.append('BAD=%d/34' % bad)
io.open(os.path.join(ROOT, '_qa34.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('wrote _qa34.txt BAD=%d' % bad)
