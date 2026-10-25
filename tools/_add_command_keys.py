"""Add the /commands + /settings translation keys to en/ru/es (idempotent)."""
import json
from collections import OrderedDict
from pathlib import Path

TEXT = {
    'en': {
        'title': '📋 <b>Commands</b>',
        'hint': '🎯 Short forms work too: /ch, /sched, /recMessages, /newSignature, /calendar_may …',
        'total': '🔢 <b>{count}</b> user commands (admin panel not included).',
        'btn': '📋 All commands',
        'group_core': '🧭 General',
        'group_channels': '📢 Channels',
        'group_bots': '🤖 Bots',
        'group_scheduling': '⏰ Scheduling',
        'group_messages': '💬 Messages',
        'group_storage': '🗄 Media storage',
        'group_stats': '📊 Statistics & reports',
        'group_signature': '✍️ Signature',
        'group_language': '🌐 Language',
    },
    'ru': {
        'title': '📋 <b>Команды</b>',
        'hint': '🎯 Короткие формы тоже работают: /ch, /sched, /recMessages, /newSignature, /calendar_may …',
        'total': '🔢 <b>{count}</b> пользовательских команд (админ-панель не считается).',
        'btn': '📋 Все команды',
        'group_core': '🧭 Основное',
        'group_channels': '📢 Каналы',
        'group_bots': '🤖 Боты',
        'group_scheduling': '⏰ Планирование',
        'group_messages': '💬 Сообщения',
        'group_storage': '🗄 Медиахранилище',
        'group_stats': '📊 Статистика и отчёты',
        'group_signature': '✍️ Подпись',
        'group_language': '🌐 Язык',
    },
    'es': {
        'title': '📋 <b>Comandos</b>',
        'hint': '🎯 Las formas cortas también funcionan: /ch, /sched, /recMessages, /newSignature, /calendar_may …',
        'total': '🔢 <b>{count}</b> comandos de usuario (el panel de administración no cuenta).',
        'btn': '📋 Todos los comandos',
        'group_core': '🧭 General',
        'group_channels': '📢 Canales',
        'group_bots': '🤖 Bots',
        'group_scheduling': '⏰ Programación',
        'group_messages': '💬 Mensajes',
        'group_storage': '🗄 Almacenamiento',
        'group_stats': '📊 Estadísticas e informes',
        'group_signature': '✍️ Firma',
        'group_language': '🌐 Idioma',
    },
}

SETTINGS = {
    'en': {
        'title': '⚙️ <b>Settings</b>',
        'hint': 'Everything you can configure, one tap away. Use /commands for the full command list.',
    },
    'ru': {
        'title': '⚙️ <b>Настройки</b>',
        'hint': 'Всё, что можно настроить — в одном месте. Полный список команд: /commands.',
    },
    'es': {
        'title': '⚙️ <b>Ajustes</b>',
        'hint': 'Todo lo que puedes configurar, a un toque. Usa /commands para ver todos los comandos.',
    },
}

for lang in ('en', 'ru', 'es'):
    path = Path('translations') / f'{lang}.json'
    data = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=OrderedDict)
    cmds = data.get('commands')
    if not isinstance(cmds, dict):
        cmds = OrderedDict()
        data['commands'] = cmds
    cmds.update(TEXT[lang])
    settings = data.get('settings')
    if not isinstance(settings, dict):
        settings = OrderedDict()
        data['settings'] = settings
    settings.update(SETTINGS[lang])
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{lang}: ok ({len(cmds)} commands keys, {len(settings)} settings keys)')
