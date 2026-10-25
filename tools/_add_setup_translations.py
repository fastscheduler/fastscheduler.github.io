"""Add/refresh the setup-flow translation keys (en/es/ru).

Run once. Dumps the JSON with the same formatting the files already use, so the
diff only contains the added/changed strings.
"""

import io
import json

EN = {
    "tutorial_welcome": (
        "👋 <b>Welcome to Fast Scheduler Bot!</b>\n\n"
        "Two steps and your channel is fully automated:\n"
        "1. 🤖 Connect your <b>sender bot</b> — your own bot that runs the channel.\n"
        "2. 📢 Open it to link your channel and set the time zone.\n\n"
        "⏱ Under two minutes. The main bot never needs to be an admin of your channel."
    ),
    "tutorial_start_btn": "▶️ Start",
    "sender_bot_connected_open": (
        "✅ <b>@{bot} is connected.</b>\n\n"
        "Open it with the button below — that's where you link the channel and set the "
        "time zone. Everything after this happens there."
    ),
    "sender_bot_live_text": (
        "🤖 <b>I'm live.</b>\n\n"
        "Through me you run the channel completely — scheduling, recurring posts, edits, "
        "stats, backups.\n\n"
        "<b>Connect the channel to start.</b> I must be an administrator there with "
        "<b>Post Messages</b>:\n"
        "1. Tap <b>Add bot to a channel</b> and pick your channel — admin + posting rights "
        "are pre-selected.\n"
        "2. I detect it within ~10 seconds and continue to the time zone.\n\n"
        "<b>Other ways to connect:</b>\n"
        "• Forward any post from the channel to me\n"
        "• Send the channel's <code>@username</code> or <code>t.me</code> link\n"
        "• Private channel: add me as an administrator from its settings — I pick it up "
        "automatically\n\n"
        "💡 Adding @{main} to the channel is <b>optional</b>. It only lets the main bot "
        "stand in for me for up to {days} days if I break — nothing else needs it.\n\n"
        "🔐 <b>Channel already has a sender bot?</b> If you are an admin there, don't tap "
        "anything: send me that bot's <b>@username</b> or <b>token</b>. I check your rights "
        "in that channel and give you access myself."
    ),
    "sender_bot_connect_prompt": (
        "📡 <b>Connect this channel</b>\n\n"
        "Make sure I'm an administrator in the channel with <b>Post Messages</b>, then:\n"
        "• Send the channel's <code>@username</code> or <code>t.me</code> link\n"
        "• Or forward any post from the channel\n\n"
        "Private channel? Add me as an administrator from its settings — I detect it "
        "automatically."
    ),
    "sender_bot_channel_linked": (
        "✅ <b>Channel linked: {channel}</b>\n\n"
        "🕐 <b>Last step — time zone.</b>\n"
        "Send a city (<code>Moscow</code>), your current time (<code>15:30</code>) or your "
        "location — or pick from the list.\n\n"
        "This sets the zone for <b>{channel}</b>. Your other channels keep theirs, and the "
        "account default changes only if it was never set."
    ),
    "sender_bot_setup_done": (
        "🎉 <b>All set — {tz}.</b>\n\n"
        "Your channel is ready. The dashboard is below — start with <b>📅 Schedule</b>."
    ),
    "sender_bot_already_connected": (
        "📢 This bot already manages {channel}. A sender bot runs exactly one channel — "
        "connect another sender bot to add a channel."
    ),
    "sender_bot_needs_admin": (
        "⚠️ <b>@{username} is not an administrator of the channel yet.</b>\n\n"
        "Tap <b>Add bot to a channel</b> below, pick the channel and give it "
        "<b>Post Messages</b>, then tap <b>Check Again</b>. The main bot does not need any "
        "rights here."
    ),
    "addbot_saved_open_bot": (
        "✅ <b>Token saved for @{bot}.</b>\n\n"
        "Open the bot with the button below — it connects your channel and sets the time "
        "zone there."
    ),
    "addbot_link_open_hint": (
        "Add @{bot} as an administrator with <b>Post Messages</b> permission, then come back."
    ),
    "admin_link_limit_reached": (
        "⏳ <b>Automatic checks are paused for today.</b>\n\n"
        "You used the 5 daily auto-checks. The button below still opens the channel picker — "
        "after adding the bot, tap <b>Check Again</b>."
    ),
    "add_channel_pick_bot": (
        "📢 <b>Add a new channel</b>\n\n"
        "Every channel is run by its own sender bot. Pick one below — it opens and walks you "
        "through adding the channel and setting the time zone."
    ),
    "add_channel_need_bot": (
        "📢 <b>Add a new channel</b>\n\n"
        "A channel is run by its own sender bot, and you don't have a free one yet.\n"
        "Create or connect a sender bot below — it connects the channel and sets the time zone."
    ),
    "connect_without_bot_btn": "Connect without a sender bot",
    "rbac_channel_has_bot": (
        "🔐 <b>This channel already has a sender bot: @{bot}</b>\n\n"
        "This bot supports <b>RBAC</b>. If you are an administrator of {channel}, you don't "
        "need any button: just send me that sender bot's <b>@username</b> or <b>token</b> "
        "here. I check your rights in that channel and grant you access — the owner is "
        "notified."
    ),
    "rbac_attach_ok": (
        "✅ <b>You're in.</b>\n\n"
        "@{bot} runs {channel} and you're now listed as its admin. Open it to schedule and "
        "manage messages; the owner can adjust your permissions in <b>Channel admins</b>."
    ),
    "rbac_attach_not_admin": (
        "🔒 I couldn't confirm you as an administrator of that channel, so I didn't grant "
        "anything."
    ),
    "rbac_attach_revoked": "🔒 Access to that channel was revoked by its owner.",
    "rbac_attach_no_channel": "ℹ️ @{bot} isn't connected to a channel yet.",
    "rbac_attach_failed": "⚠️ I couldn't verify that right now. Try again in a moment.",
    "rbac_attach_rate_limited": "⏳ Too many attempts. Try again in an hour.",
    "rbac_attach_owner_notice": (
        "👤 <b>{user}</b> joined {channel} as an admin through @{bot}.\n\n"
        "They can schedule and manage messages. Change their permissions in "
        "<b>Channel admins</b>."
    ),
    "rbac_attach_open_btn": "Open @{bot}",
    "fallback_offer": (
        "⚠️ <b>@{bot} couldn't post to {channel}</b> — I posted this one from the main bot so "
        "it wouldn't be lost.\n\n"
        "Want me to keep posting from the main bot for up to <b>{days} days</b> while it's "
        "broken? It stops automatically afterwards."
    ),
    "fallback_enable_btn": "✅ Use the main bot for {days} days",
    "fallback_decline_btn": "❌ No, I'll fix my bot",
    "fallback_enabled": (
        "✅ <b>Stand-in enabled for {channel}</b>\n\n"
        "The main bot will post there for up to {days} days if your sender bot fails. It "
        "stops automatically."
    ),
    "fallback_declined": (
        "👍 Understood — {channel} will only be posted from its sender bot. You'll get an "
        "error notice if it fails."
    ),
    "fallback_reverted": (
        "✅ Stand-in stopped for {channel}. Posts go through its sender bot again."
    ),
    "fallback_revert_btn": "⛔ Stop the stand-in now",
    "fallback_window_over": (
        "⏳ The main-bot stand-in for <code>{channel_id}</code> has ended, so I didn't post "
        "this one. Check your sender bot, or enable the stand-in again."
    ),
    "open_dashboard_btn": "📊 Open dashboard",
    "sb_tz_skip": "⏭ Use my current time zone",
    "sender_bot_admin_manual": (
        "⚠️ I couldn't add <b>@{username}</b> to the channel automatically. Add it as an "
        "administrator with <b>Post Messages</b> permission, then tap <b>Check Again</b>."
    ),
}

EN_SECTIONS = {
    "tutorial": {
        "bot_step_text": (
            "🤖 <b>Step 1/2 — Connect your sender bot</b>\n\n"
            "A sender bot is your own Telegram bot: it posts to your channel and gives you "
            "the full management menu.\n\n"
            "Tap <b>Create bot</b> and I'll open @BotFather with a name ready — or paste a "
            "token you already have.\n\n"
            "No channel is needed yet. In the next step you open the bot and it connects the "
            "channel and the time zone itself."
        ),
        "bot_done": (
            "🎉 <b>Sender bot connected.</b>\n\n"
            "Open @{bot} — it connects {channel} and sets the time zone there."
        ),
    },
    "bot": {
        "not_admin_channel": (
            "❌ The bot is not an administrator in that channel.\n\n"
            "Add it as an administrator with these permissions:\n"
            "• Post Messages\n• Edit Messages\n• Delete Messages\n\n"
            "Then tap Check Again."
        ),
    },
}

ES = {
    "tutorial_welcome": (
        "👋 <b>¡Bienvenido a Fast Scheduler Bot!</b>\n\n"
        "Dos pasos y tu canal queda totalmente automatizado:\n"
        "1. 🤖 Conecta tu <b>bot emisor</b> — tu propio bot que gestiona el canal.\n"
        "2. 📢 Ábrelo para vincular tu canal y configurar la zona horaria.\n\n"
        "⏱ Menos de dos minutos. El bot principal nunca necesita ser administrador del canal."
    ),
    "tutorial_start_btn": "▶️ Empezar",
    "sender_bot_connected_open": (
        "✅ <b>@{bot} está conectado.</b>\n\n"
        "Ábrelo con el botón de abajo: ahí vinculas el canal y configuras la zona horaria. "
        "Todo lo demás ocurre allí."
    ),
    "sender_bot_live_text": (
        "🤖 <b>Ya estoy activo.</b>\n\n"
        "Conmigo puedes gestionar el canal por completo: programación, mensajes recurrentes, "
        "ediciones, estadísticas y copias de seguridad.\n\n"
        "<b>Conecta el canal para empezar.</b> Debo ser administrador con "
        "<b>Publicar mensajes</b>:\n"
        "1. Pulsa <b>Añadir bot a un canal</b> y elige tu canal — los permisos de "
        "administrador y publicación vienen marcados.\n"
        "2. Lo detecto en unos 10 segundos y continúo con la zona horaria.\n\n"
        "<b>Otras formas de conectar:</b>\n"
        "• Reenvíame cualquier publicación del canal\n"
        "• Envía el <code>@usuario</code> o el enlace <code>t.me</code> del canal\n"
        "• Canal privado: añádeme como administrador desde sus ajustes y lo detecto "
        "automáticamente\n\n"
        "💡 Añadir @{main} al canal es <b>opcional</b>. Solo permite que el bot principal me "
        "sustituya hasta {days} días si fallo — nada más lo necesita.\n\n"
        "🔐 <b>¿El canal ya tiene un bot emisor?</b> Si eres administrador, no pulses nada: "
        "envíame el <b>@usuario</b> o el <b>token</b> de ese bot. Compruebo tus permisos en "
        "ese canal y te doy acceso."
    ),
    "sender_bot_connect_prompt": (
        "📡 <b>Conecta este canal</b>\n\n"
        "Asegúrate de que soy administrador del canal con <b>Publicar mensajes</b> y luego:\n"
        "• Envía el <code>@usuario</code> o el enlace <code>t.me</code> del canal\n"
        "• O reenvía cualquier publicación del canal\n\n"
        "¿Canal privado? Añádeme como administrador desde sus ajustes y lo detecto "
        "automáticamente."
    ),
    "sender_bot_channel_linked": (
        "✅ <b>Canal vinculado: {channel}</b>\n\n"
        "🕐 <b>Último paso: zona horaria.</b>\n"
        "Envía una ciudad (<code>Moscú</code>), tu hora actual (<code>15:30</code>) o tu "
        "ubicación — o elige de la lista.\n\n"
        "Esto fija la zona de <b>{channel}</b>. Tus otros canales conservan la suya y la "
        "zona predeterminada solo cambia si nunca se configuró."
    ),
    "sender_bot_setup_done": (
        "🎉 <b>Todo listo — {tz}.</b>\n\n"
        "Tu canal está preparado. El panel está abajo: empieza con <b>📅 Programar</b>."
    ),
    "sender_bot_already_connected": (
        "📢 Este bot ya gestiona {channel}. Un bot emisor gestiona un solo canal: conecta "
        "otro bot emisor para añadir un canal."
    ),
    "sender_bot_needs_admin": (
        "⚠️ <b>@{username} todavía no es administrador del canal.</b>\n\n"
        "Pulsa <b>Añadir bot a un canal</b>, elige el canal y dale <b>Publicar mensajes</b>; "
        "luego pulsa <b>Comprobar de nuevo</b>. El bot principal no necesita permisos aquí."
    ),
    "addbot_saved_open_bot": (
        "✅ <b>Token guardado para @{bot}.</b>\n\n"
        "Abre el bot con el botón de abajo: conecta tu canal y configura allí la zona horaria."
    ),
    "addbot_link_open_hint": (
        "Añade @{bot} como administrador con permiso de <b>Publicar mensajes</b> y vuelve."
    ),
    "admin_link_limit_reached": (
        "⏳ <b>Las comprobaciones automáticas están pausadas por hoy.</b>\n\n"
        "Usaste las 5 comprobaciones diarias. El botón de abajo sigue abriendo el selector de "
        "canales: tras añadir el bot, pulsa <b>Comprobar de nuevo</b>."
    ),
    "add_channel_pick_bot": (
        "📢 <b>Añadir un canal nuevo</b>\n\n"
        "Cada canal lo gestiona su propio bot emisor. Elige uno abajo: se abre y te guía para "
        "añadir el canal y configurar la zona horaria."
    ),
    "add_channel_need_bot": (
        "📢 <b>Añadir un canal nuevo</b>\n\n"
        "Cada canal lo gestiona su propio bot emisor y aún no tienes uno libre.\n"
        "Crea o conecta un bot emisor abajo: conectará el canal y configurará la zona horaria."
    ),
    "connect_without_bot_btn": "Conectar sin bot emisor",
    "rbac_channel_has_bot": (
        "🔐 <b>Este canal ya tiene un bot emisor: @{bot}</b>\n\n"
        "Este bot admite <b>RBAC</b>. Si eres administrador de {channel}, no necesitas ningún "
        "botón: envíame aquí el <b>@usuario</b> o el <b>token</b> de ese bot. Compruebo tus "
        "permisos en ese canal y te doy acceso — el propietario recibe un aviso."
    ),
    "rbac_attach_ok": (
        "✅ <b>Acceso concedido.</b>\n\n"
        "@{bot} gestiona {channel} y ahora figuras como su administrador. Ábrelo para "
        "programar y gestionar mensajes; el propietario puede ajustar tus permisos en "
        "<b>Administradores del canal</b>."
    ),
    "rbac_attach_not_admin": (
        "🔒 No pude confirmar que seas administrador de ese canal, así que no concedí nada."
    ),
    "rbac_attach_revoked": "🔒 El propietario revocó el acceso a ese canal.",
    "rbac_attach_no_channel": "ℹ️ @{bot} aún no está conectado a un canal.",
    "rbac_attach_failed": "⚠️ No pude verificarlo ahora. Inténtalo en un momento.",
    "rbac_attach_rate_limited": "⏳ Demasiados intentos. Inténtalo dentro de una hora.",
    "rbac_attach_owner_notice": (
        "👤 <b>{user}</b> se unió a {channel} como administrador mediante @{bot}.\n\n"
        "Puede programar y gestionar mensajes. Cambia sus permisos en "
        "<b>Administradores del canal</b>."
    ),
    "rbac_attach_open_btn": "Abrir @{bot}",
    "fallback_offer": (
        "⚠️ <b>@{bot} no pudo publicar en {channel}</b> — publiqué este desde el bot principal "
        "para no perderlo.\n\n"
        "¿Quieres que siga publicando desde el bot principal hasta <b>{days} días</b> mientras "
        "está averiado? Se detiene automáticamente después."
    ),
    "fallback_enable_btn": "✅ Usar el bot principal {days} días",
    "fallback_decline_btn": "❌ No, arreglaré mi bot",
    "fallback_enabled": (
        "✅ <b>Sustitución activada para {channel}</b>\n\n"
        "El bot principal publicará allí hasta {days} días si tu bot emisor falla. Se detiene "
        "automáticamente."
    ),
    "fallback_declined": (
        "👍 Entendido — {channel} solo se publicará desde su bot emisor. Recibirás un aviso "
        "de error si falla."
    ),
    "fallback_reverted": (
        "✅ Sustitución detenida para {channel}. Las publicaciones vuelven a su bot emisor."
    ),
    "fallback_revert_btn": "⛔ Detener la sustitución",
    "fallback_window_over": (
        "⏳ La sustitución del bot principal para <code>{channel_id}</code> ha terminado, así "
        "que no publiqué este mensaje. Revisa tu bot emisor o vuelve a activar la sustitución."
    ),
    "open_dashboard_btn": "📊 Abrir el panel",
    "sb_tz_skip": "⏭ Usar mi zona horaria actual",
    "sender_bot_admin_manual": (
        "⚠️ No pude añadir <b>@{username}</b> al canal automáticamente. Añádelo como "
        "administrador con permiso de <b>Publicar mensajes</b> y pulsa <b>Comprobar de "
        "nuevo</b>."
    ),
    "_sections": {
        "tutorial": {
            "bot_step_text": (
                "🤖 <b>Paso 1/2 — Conecta tu bot emisor</b>\n\n"
                "Un bot emisor es tu propio bot de Telegram: publica en tu canal y te da el "
                "menú de gestión completo.\n\n"
                "Pulsa <b>Crear bot</b> y abriré @BotFather con un nombre listo — o pega un "
                "token que ya tengas.\n\n"
                "Aún no hace falta ningún canal. En el siguiente paso abres el bot y él mismo "
                "conecta el canal y la zona horaria."
            ),
            "bot_done": (
                "🎉 <b>Bot emisor conectado.</b>\n\n"
                "Abre @{bot}: conecta {channel} y configura allí la zona horaria."
            ),
        },
        "bot": {
            "not_admin_channel": (
                "❌ El bot no es administrador de ese canal.\n\n"
                "Añádelo como administrador con estos permisos:\n"
                "• Publicar mensajes\n• Editar mensajes\n• Eliminar mensajes\n\n"
                "Luego pulsa Comprobar de nuevo."
            ),
        },
    },
}

RU = {
    "tutorial_welcome": (
        "👋 <b>Добро пожаловать в Fast Scheduler Bot!</b>\n\n"
        "Два шага — и канал полностью автоматизирован:\n"
        "1. 🤖 Подключите своего <b>бота-отправителя</b> — собственного бота для канала.\n"
        "2. 📢 Откройте его, чтобы привязать канал и настроить часовой пояс.\n\n"
        "⏱ Меньше двух минут. Основному боту не нужны права администратора в канале."
    ),
    "tutorial_start_btn": "▶️ Начать",
    "sender_bot_connected_open": (
        "✅ <b>@{bot} подключён.</b>\n\n"
        "Откройте его кнопкой ниже — там вы привяжете канал и настроите часовой пояс. "
        "Всё дальнейшее происходит там."
    ),
    "sender_bot_live_text": (
        "🤖 <b>Я запущен.</b>\n\n"
        "Через меня канал управляется полностью: публикации, повторы, правки, статистика, "
        "резервные копии.\n\n"
        "<b>Подключите канал, чтобы начать.</b> Я должен быть администратором с правом "
        "<b>Публикация сообщений</b>:\n"
        "1. Нажмите <b>Добавить бота в канал</b> и выберите канал — права администратора и "
        "публикации уже отмечены.\n"
        "2. Я обнаружу его примерно через 10 секунд и перейду к часовому поясу.\n\n"
        "<b>Другие способы:</b>\n"
        "• Перешлите мне любой пост из канала\n"
        "• Отправьте <code>@имя</code> или ссылку <code>t.me</code> канала\n"
        "• Закрытый канал: добавьте меня администратором в его настройках — я найду его сам\n\n"
        "💡 Добавлять @{main} в канал <b>не обязательно</b>. Это нужно только для того, "
        "чтобы основной бот подменял меня до {days} дней при сбое.\n\n"
        "🔐 <b>В канале уже есть бот-отправитель?</b> Если вы администратор, ничего не "
        "нажимайте: пришлите <b>@имя</b> или <b>токен</b> того бота. Я проверю ваши права "
        "в этом канале и выдам доступ."
    ),
    "sender_bot_connect_prompt": (
        "📡 <b>Подключение канала</b>\n\n"
        "Убедитесь, что я администратор канала с правом <b>Публикация сообщений</b>, затем:\n"
        "• Отправьте <code>@имя</code> или ссылку <code>t.me</code> канала\n"
        "• Или перешлите любой пост из канала\n\n"
        "Закрытый канал? Добавьте меня администратором в настройках — я найду его сам."
    ),
    "sender_bot_channel_linked": (
        "✅ <b>Канал привязан: {channel}</b>\n\n"
        "🕐 <b>Последний шаг — часовой пояс.</b>\n"
        "Отправьте город (<code>Москва</code>), текущее время (<code>15:30</code>) или "
        "геопозицию — либо выберите из списка.\n\n"
        "Пояс задаётся для <b>{channel}</b>. Другие каналы сохранят свои, а общий пояс "
        "изменится только если он не был задан."
    ),
    "sender_bot_setup_done": (
        "🎉 <b>Готово — {tz}.</b>\n\n"
        "Канал настроен. Панель ниже — начните с <b>📅 Запланировать</b>."
    ),
    "sender_bot_already_connected": (
        "📢 Этот бот уже управляет каналом {channel}. Один бот-отправитель — один канал: "
        "подключите другого бота, чтобы добавить канал."
    ),
    "sender_bot_needs_admin": (
        "⚠️ <b>@{username} пока не администратор канала.</b>\n\n"
        "Нажмите <b>Добавить бота в канал</b>, выберите канал и дайте право "
        "<b>Публикация сообщений</b>, затем нажмите <b>Проверить снова</b>. Основному боту "
        "права здесь не нужны."
    ),
    "addbot_saved_open_bot": (
        "✅ <b>Токен для @{bot} сохранён.</b>\n\n"
        "Откройте бота кнопкой ниже — он подключит канал и настроит часовой пояс."
    ),
    "addbot_link_open_hint": (
        "Добавьте @{bot} администратором с правом <b>Публикация сообщений</b> и вернитесь."
    ),
    "admin_link_limit_reached": (
        "⏳ <b>Автопроверки приостановлены на сегодня.</b>\n\n"
        "Вы использовали 5 проверок в день. Кнопка ниже по-прежнему открывает выбор канала — "
        "после добавления бота нажмите <b>Проверить снова</b>."
    ),
    "add_channel_pick_bot": (
        "📢 <b>Добавление канала</b>\n\n"
        "Каждым каналом управляет свой бот-отправитель. Выберите его ниже — он откроется и "
        "проведёт вас через подключение канала и настройку часового пояса."
    ),
    "add_channel_need_bot": (
        "📢 <b>Добавление канала</b>\n\n"
        "Каждым каналом управляет свой бот-отправитель, а свободного у вас пока нет.\n"
        "Создайте или подключите бота ниже — он подключит канал и настроит часовой пояс."
    ),
    "connect_without_bot_btn": "Подключить без бота-отправителя",
    "rbac_channel_has_bot": (
        "🔐 <b>В этом канале уже есть бот-отправитель: @{bot}</b>\n\n"
        "Бот поддерживает <b>RBAC</b>. Если вы администратор {channel}, кнопки не нужны: "
        "пришлите сюда <b>@имя</b> или <b>токен</b> того бота. Я проверю ваши права в этом "
        "канале и выдам доступ — владелец получит уведомление."
    ),
    "rbac_attach_ok": (
        "✅ <b>Доступ выдан.</b>\n\n"
        "@{bot} управляет {channel}, и вы теперь указаны его администратором. Откройте бота, "
        "чтобы планировать и управлять сообщениями; владелец может изменить ваши права в "
        "<b>Администраторы канала</b>."
    ),
    "rbac_attach_not_admin": (
        "🔒 Не удалось подтвердить, что вы администратор этого канала, поэтому доступ не выдан."
    ),
    "rbac_attach_revoked": "🔒 Владелец отозвал доступ к этому каналу.",
    "rbac_attach_no_channel": "ℹ️ @{bot} пока не подключён к каналу.",
    "rbac_attach_failed": "⚠️ Сейчас не удалось проверить. Попробуйте через минуту.",
    "rbac_attach_rate_limited": "⏳ Слишком много попыток. Повторите через час.",
    "rbac_attach_owner_notice": (
        "👤 <b>{user}</b> присоединился к {channel} как администратор через @{bot}.\n\n"
        "Он может планировать и управлять сообщениями. Измените его права в "
        "<b>Администраторы канала</b>."
    ),
    "rbac_attach_open_btn": "Открыть @{bot}",
    "fallback_offer": (
        "⚠️ <b>@{bot} не смог опубликовать в {channel}</b> — я отправил этот пост с "
        "основного бота, чтобы он не потерялся.\n\n"
        "Продолжать публикации с основного бота до <b>{days} дней</b>, пока бот неисправен? "
        "Потом подмена завершится автоматически."
    ),
    "fallback_enable_btn": "✅ Использовать основной бот {days} дней",
    "fallback_decline_btn": "❌ Нет, я исправлю своего бота",
    "fallback_enabled": (
        "✅ <b>Подмена включена для {channel}</b>\n\n"
        "Основной бот будет публиковать там до {days} дней при сбое вашего бота. Затем "
        "подмена прекратится автоматически."
    ),
    "fallback_declined": (
        "👍 Понятно — {channel} будет публиковаться только через своего бота. При сбое вы "
        "получите уведомление об ошибке."
    ),
    "fallback_reverted": (
        "✅ Подмена для {channel} остановлена. Публикации снова идут через его бота."
    ),
    "fallback_revert_btn": "⛔ Остановить подмену",
    "fallback_window_over": (
        "⏳ Подмена основным ботом для <code>{channel_id}</code> завершена, поэтому я не "
        "опубликовал этот пост. Проверьте своего бота или включите подмену снова."
    ),
    "open_dashboard_btn": "📊 Открыть панель",
    "sb_tz_skip": "⏭ Оставить текущий часовой пояс",
    "sender_bot_admin_manual": (
        "⚠️ Не удалось добавить <b>@{username}</b> в канал автоматически. Добавьте его "
        "администратором с правом <b>Публикация сообщений</b> и нажмите <b>Проверить "
        "снова</b>."
    ),
    "_sections": {
        "tutorial": {
            "bot_step_text": (
                "🤖 <b>Шаг 1/2 — Подключите бота-отправителя</b>\n\n"
                "Бот-отправитель — это ваш собственный бот в Telegram: он публикует в канал и "
                "даёт полное меню управления.\n\n"
                "Нажмите <b>Создать бота</b> — я открою @BotFather с готовым именем, либо "
                "вставьте токен, который у вас уже есть.\n\n"
                "Канал пока не нужен. На следующем шаге вы откроете бота, и он сам подключит "
                "канал и настроит часовой пояс."
            ),
            "bot_done": (
                "🎉 <b>Бот-отправитель подключён.</b>\n\n"
                "Откройте @{bot} — он подключит {channel} и настроит часовой пояс."
            ),
        },
        "bot": {
            "not_admin_channel": (
                "❌ Бот не администратор этого канала.\n\n"
                "Добавьте его администратором с правами:\n"
                "• Публикация сообщений\n• Редактирование сообщений\n• Удаление сообщений\n\n"
                "Затем нажмите «Проверить снова»."
            ),
        },
    },
}


def apply(path: str, data: dict) -> None:
    with io.open(path, encoding='utf-8') as fh:
        doc = json.load(fh)
    sections = data.pop('_sections', {})
    for key, value in data.items():
        doc[key] = value
    for section, values in sections.items():
        target = doc.get(section)
        if not isinstance(target, dict):
            target = {}
            doc[section] = target
        target.update(values)
    with io.open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=2))
        fh.write('\n')
    print(f'{path}: {len(data)} flat keys + {sum(len(v) for v in sections.values())} section keys')


apply('translations/en.json', dict(EN, _sections=EN_SECTIONS))
apply('translations/es.json', dict(ES))
apply('translations/ru.json', dict(RU))
