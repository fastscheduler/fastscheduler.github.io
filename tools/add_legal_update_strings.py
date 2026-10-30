"""Add the legal-update strings to the bot translation bundles (idempotent).

Text-level insertion rather than a json round-trip: several bundles carry a
BOM and CRLF line endings, and a ``json.dump`` rewrite would strip the BOM,
renumber the whole file and bury the real change in diff noise.

Run: py -3 tools/add_legal_update_strings.py
"""
import json
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── user-facing (Main bot gate + notice + SetDate prompt) ─────────────────
USER = {
    'en': {
        'legal_doc_privacy': 'Privacy Policy',
        'legal_doc_terms': 'Terms of Service',
        'legal_doc_refundpolicy': 'Refund Policy',
        'legal_doc_all': 'our legal documents',
        'legal_update_title': '⚖️ <b>We updated our legal documents</b>',
        'legal_update_body': 'Updated: <b>{pages}</b>.',
        'legal_update_what_changed': '<b>What changed:</b> {summary}',
        'legal_update_effective': '<b>Effective from:</b> {effective}',
        'legal_update_required': ('Please review and accept the updated documents to keep using Fast Scheduler and '
                                  'SetDate. Accepting is needed once — Fast Support stays available either way.'),
        'legal_update_accept_btn': '✅ I accept the updated documents',
        'legal_update_accepted': '✅ Thank you — the updated documents are accepted.',
        'legal_update_none_pending': '✅ No legal update is waiting for you. Everything is up to date.',
        'legal_update_pages_unknown': 'our legal documents',
        'legal_update_notice': ('⚖️ <b>Our legal documents were updated</b>\n\nUpdated: <b>{pages}</b>.\n'
                                'Effective from: {effective}\n\nPlease review and accept them to keep using '
                                'SetDate. Accepting is needed once — Fast Support stays available either way.'),
    },
    'ru': {
        'legal_doc_privacy': 'Политика конфиденциальности',
        'legal_doc_terms': 'Условия использования',
        'legal_doc_refundpolicy': 'Политика возвратов',
        'legal_doc_all': 'наши юридические документы',
        'legal_update_title': '⚖️ <b>Мы обновили юридические документы</b>',
        'legal_update_body': 'Обновлено: <b>{pages}</b>.',
        'legal_update_what_changed': '<b>Что изменилось:</b> {summary}',
        'legal_update_effective': '<b>Действует с:</b> {effective}',
        'legal_update_required': ('Пожалуйста, ознакомьтесь с обновлёнными документами и примите их, чтобы '
                                  'продолжить пользоваться Fast Scheduler и SetDate. Принять нужно один раз — '
                                  'Fast Support остаётся доступным в любом случае.'),
        'legal_update_accept_btn': '✅ Принимаю обновлённые документы',
        'legal_update_accepted': '✅ Спасибо — обновлённые документы приняты.',
        'legal_update_none_pending': '✅ Ожидающих обновлений документов нет. Всё в порядке.',
        'legal_update_pages_unknown': 'наши юридические документы',
        'legal_update_notice': ('⚖️ <b>Мы обновили юридические документы</b>\n\nОбновлено: <b>{pages}</b>.\n'
                                'Действует с: {effective}\n\nПожалуйста, ознакомьтесь и примите их, чтобы '
                                'продолжить пользоваться SetDate. Принять нужно один раз — Fast Support '
                                'остаётся доступным в любом случае.'),
    },
    'es': {
        'legal_doc_privacy': 'Política de Privacidad',
        'legal_doc_terms': 'Términos de Servicio',
        'legal_doc_refundpolicy': 'Política de Reembolsos',
        'legal_doc_all': 'nuestros documentos legales',
        'legal_update_title': '⚖️ <b>Actualizamos nuestros documentos legales</b>',
        'legal_update_body': 'Actualizado: <b>{pages}</b>.',
        'legal_update_what_changed': '<b>Qué cambió:</b> {summary}',
        'legal_update_effective': '<b>Vigente desde:</b> {effective}',
        'legal_update_required': ('Revisa y acepta los documentos actualizados para seguir usando Fast Scheduler y '
                                  'SetDate. Solo hace falta aceptar una vez — Fast Support sigue disponible en '
                                  'cualquier caso.'),
        'legal_update_accept_btn': '✅ Acepto los documentos actualizados',
        'legal_update_accepted': '✅ Gracias — los documentos actualizados quedan aceptados.',
        'legal_update_none_pending': '✅ No hay ninguna actualización legal pendiente. Todo está al día.',
        'legal_update_pages_unknown': 'nuestros documentos legales',
        'legal_update_notice': ('⚖️ <b>Actualizamos nuestros documentos legales</b>\n\nActualizado: '
                                '<b>{pages}</b>.\nVigente desde: {effective}\n\nRevisa y acepta los documentos '
                                'para seguir usando SetDate. Solo hace falta aceptar una vez — Fast Support '
                                'sigue disponible en cualquier caso.'),
    },
}

# ── admin-panel strings ───────────────────────────────────────────────────
ADMIN = {
    'en': {
        'admin_legal_updates': '⚖️ Legal updates',
        'admin_legal_title': ('⚖️ <b>Legal updates</b>\n\n'
                              'Documents: {docs}\n'
                              'Edition: <code>{stamp}</code>\n'
                              'Effective from: {effective}\n'
                              'Parsed “what changed”: {changes}\n\n'
                              'Accepted by {accepted}/{total} users\n'
                              'Gate: {gate}\n\n'
                              'Pick the documents that changed, check the parsed details, preview the message, '
                              'then send it. Sending arms the gate: until a user accepts, the Main bot and SetDate '
                              'answer with this notice (Fast Support keeps working).'),
        'admin_legal_none': 'none selected',
        'admin_legal_no_stamp': 'not set',
        'admin_legal_gate_on': '🔒 on (users must accept)',
        'admin_legal_gate_off': '🔓 off (nobody is blocked)',
        'admin_legal_doc_privacy': 'Privacy Policy',
        'admin_legal_doc_terms': 'Terms of Service',
        'admin_legal_doc_refundpolicy': 'Refund Policy',
        'admin_legal_parse_btn': '🔎 Parse details from the website',
        'admin_legal_edit_dates_btn': '✏️ Set date / “what changed”',
        'admin_legal_enable_gate_btn': '🔒 Require acceptance',
        'admin_legal_disable_gate_btn': '🔓 Stop requiring acceptance',
        'admin_legal_send_btn': '🚀 Send to all users',
        'admin_legal_reset_btn': '♻️ Reset acceptances',
        'admin_legal_reset_confirm': ('⚠️ <b>Reset acceptances?</b>\n\n'
                                      'This forgets who accepted the current edition, so every user will be asked '
                                      'again and the gate will block them again. Use it to re-test the flow or to '
                                      'undo an accidental send.'),
        'admin_legal_reset_yes_btn': '♻️ Yes, reset acceptances',
        'admin_legal_reset_done': '✅ Acceptances cleared ({count} entries). Users will be asked again.',
        'admin_legal_parsed': ('🔎 <b>Parsed from the website</b>\n\n'
                               'Edition date: <code>{stamp}</code>\n'
                               'Effective from: {effective}\n'
                               'Documents with a “what changed” note: {changes}'),
        'admin_legal_preview_title': '👀 <b>Preview — {lang}</b>',
        'admin_legal_await_text': ('✏️ Send the edition metadata as:\n\n'
                                   '<code>YYYY-MM-DD | effective date text | what changed</code>\n\n'
                                   'Only the first part is required. Example:\n'
                                   '<code>2026-10-26 | October 26, 2026 | Added the analytics disclosure</code>\n\n'
                                   '/cancel to abort.'),
        'admin_legal_edit_saved': '✅ Saved. Edition <code>{stamp}</code>, effective {effective}.',
        'admin_legal_edit_cancelled': '↩️ Editing cancelled — nothing changed.',
        'admin_legal_bad_date': '❌ The date must look like <code>YYYY-MM-DD</code>. Try again or /cancel.',
        'admin_legal_gate_toggled': '✅ Gate {state}.',
        'admin_legal_no_docs': '❌ Select at least one document above, then try again.',
        'admin_legal_confirm': ('🚀 <b>Send the legal-update notice?</b>\n\n'
                               'Documents: {docs}\n'
                               'Recipients: {total} users, each in their own language.\n\n'
                               'Sending also arms the gate, so until a user accepts, the Main bot and SetDate '
                               'answer with the notice.'),
        'admin_legal_send_confirm_btn': '✅ Send now and require acceptance',
        'admin_legal_sending': '📤 Sending to {total} users… you can keep using the panel.',
        'admin_legal_done': ('✅ <b>Legal update sent</b>\n\nDelivered: {sent}\nFailed: {failed}\n'
                             'Skipped (blocked/unreachable): {skipped}\nAudience: {total}'),
    },
    'ru': {
        'admin_legal_updates': '⚖️ Обновления документов',
        'admin_legal_title': ('⚖️ <b>Обновления документов</b>\n\n'
                              'Документы: {docs}\n'
                              'Редакция: <code>{stamp}</code>\n'
                              'Действует с: {effective}\n'
                              'Распознано «что изменилось»: {changes}\n\n'
                              'Приняли {accepted}/{total} пользователей\n'
                              'Блокировка: {gate}\n\n'
                              'Отметьте изменившиеся документы, проверьте распознанные данные, посмотрите '
                              'предпросмотр и отправьте. Отправка включает блокировку: пока пользователь не '
                              'примет, основной бот и SetDate отвечают этим сообщением (Fast Support работает).'),
        'admin_legal_none': 'ничего не выбрано',
        'admin_legal_no_stamp': 'не задано',
        'admin_legal_gate_on': '🔒 включена (нужно принять)',
        'admin_legal_gate_off': '🔓 выключена (никого не блокируем)',
        'admin_legal_doc_privacy': 'Политика конфиденциальности',
        'admin_legal_doc_terms': 'Условия использования',
        'admin_legal_doc_refundpolicy': 'Политика возвратов',
        'admin_legal_parse_btn': '🔎 Распознать данные с сайта',
        'admin_legal_edit_dates_btn': '✏️ Задать дату / «что изменилось»',
        'admin_legal_enable_gate_btn': '🔒 Требовать принятие',
        'admin_legal_disable_gate_btn': '🔓 Не требовать принятие',
        'admin_legal_send_btn': '🚀 Отправить всем пользователям',
        'admin_legal_reset_btn': '♻️ Сбросить принятия',
        'admin_legal_reset_confirm': ('⚠️ <b>Сбросить принятия?</b>\n\n'
                                      'Кто принял текущую редакцию — будет забыто, поэтому у всех снова '
                                      'спросят, и блокировка снова сработает. Нужно для повторной проверки '
                                      'или отмены случайной отправки.'),
        'admin_legal_reset_yes_btn': '♻️ Да, сбросить принятия',
        'admin_legal_reset_done': '✅ Принятия сброшены (записей: {count}). Пользователей спросят снова.',
        'admin_legal_parsed': ('🔎 <b>Распознано с сайта</b>\n\n'
                               'Дата редакции: <code>{stamp}</code>\n'
                               'Действует с: {effective}\n'
                               'Документов с описанием изменений: {changes}'),
        'admin_legal_preview_title': '👀 <b>Предпросмотр — {lang}</b>',
        'admin_legal_await_text': ('✏️ Отправьте данные редакции в формате:\n\n'
                                   '<code>ГГГГ-ММ-ДД | текст даты вступления | что изменилось</code>\n\n'
                                   'Обязательна только первая часть. Пример:\n'
                                   '<code>2026-10-26 | 26 октября 2026 | Добавлено описание аналитики</code>\n\n'
                                   '/cancel для отмены.'),
        'admin_legal_edit_saved': '✅ Сохранено. Редакция <code>{stamp}</code>, действует с {effective}.',
        'admin_legal_edit_cancelled': '↩️ Редактирование отменено — ничего не изменилось.',
        'admin_legal_bad_date': '❌ Дата должна быть в виде <code>ГГГГ-ММ-ДД</code>. Попробуйте снова или /cancel.',
        'admin_legal_gate_toggled': '✅ Блокировка {state}.',
        'admin_legal_no_docs': '❌ Выберите хотя бы один документ выше и повторите.',
        'admin_legal_confirm': ('🚀 <b>Отправить уведомление об обновлении документов?</b>\n\n'
                               'Документы: {docs}\n'
                               'Получатели: {total} пользователей, каждый на своём языке.\n\n'
                               'Отправка также включает блокировку: пока пользователь не примет, основной бот '
                               'и SetDate отвечают этим сообщением.'),
        'admin_legal_send_confirm_btn': '✅ Отправить и требовать принятие',
        'admin_legal_sending': '📤 Отправляем {total} пользователям… панель можно использовать дальше.',
        'admin_legal_done': ('✅ <b>Уведомление отправлено</b>\n\nДоставлено: {sent}\nОшибок: {failed}\n'
                             'Пропущено (заблокировали/недоступны): {skipped}\nВсего: {total}'),
    },
}

TARGETS = [
    (os.path.join('translations', 'en.json'), USER['en']),
    (os.path.join('translations', 'ru.json'), USER['ru']),
    (os.path.join('translations', 'es.json'), USER['es']),
    (os.path.join('SetDate', 'translations', 'en.json'), {
        k: USER['en'][k] for k in ('legal_doc_privacy', 'legal_doc_terms', 'legal_doc_refundpolicy',
                                   'legal_doc_all', 'legal_update_notice',
                                   'legal_update_accept_btn', 'legal_update_accepted')
    }),
    (os.path.join('SetDate', 'translations', 'ru.json'), {
        k: USER['ru'][k] for k in ('legal_doc_privacy', 'legal_doc_terms', 'legal_doc_refundpolicy',
                                   'legal_doc_all', 'legal_update_notice',
                                   'legal_update_accept_btn', 'legal_update_accepted')
    }),
    (os.path.join('SetDate', 'translations', 'es.json'), {
        k: USER['es'][k] for k in ('legal_doc_privacy', 'legal_doc_terms', 'legal_doc_refundpolicy',
                                   'legal_doc_all', 'legal_update_notice',
                                   'legal_update_accept_btn', 'legal_update_accepted')
    }),
    (os.path.join('translations', 'admin', 'en.json'), ADMIN['en']),
    (os.path.join('translations', 'admin', 'ru.json'), ADMIN['ru']),
]


def insert(path: str, pairs: dict) -> str:
    full = os.path.join(REPO, path)
    if not os.path.exists(full):
        return f'{path}: MISSING (skipped)'
    raw = open(full, 'r', encoding='utf-8-sig', newline='').read()
    bom = open(full, 'rb').read(3) == b'\xef\xbb\xbf'
    try:
        existing = json.loads(raw)
    except Exception as exc:
        return f'{path}: BROKEN JSON ({exc}) — refused to touch'
    nl = '\r\n' if '\r\n' in raw else '\n'
    m = re.match(r'\s*\{\s*\r?\n', raw)
    if not m:
        return f'{path}: unexpected shape — refused to touch'
    indent = re.match(r'(\s*)"', raw[m.end():])
    pad = indent.group(1) if indent else '  '
    fresh = {k: v for k, v in pairs.items() if k not in existing}
    if not fresh:
        return f'{path}: already up to date'
    lines = ''.join(
        f'{pad}{json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)},{nl}'
        for k, v in fresh.items())
    out = raw[:m.end()] + lines + raw[m.end():]
    # Verify before writing: a broken bundle would take the whole bot's text down.
    json.loads(out)
    with open(full, 'w', encoding='utf-8-sig' if bom else 'utf-8', newline='') as f:
        f.write(out)
    return f'{path}: added {len(fresh)} key(s)'


if __name__ == '__main__':
    for path, pairs in TARGETS:
        print(insert(path, pairs))
