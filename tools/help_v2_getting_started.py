# -*- coding: utf-8 -*-
"""The first thing a new user reads: bot intro + the "Get Started" article.

Two surfaces have to say the same thing:

* ``tutorial_welcome`` — the screen the bot shows after the terms gate, before
  any setup happens. People opened the bot, read "two steps and your channel is
  automated" and still asked what the product was for, because nothing said it:
  no description, no reason to keep it, no feature list.
* ``help.getting_started`` — the article the Help Center opens on, which still
  described the retired flow (connect the channel first, make the main bot an
  administrator, connect a sender bot last).

Both now lead with what the bot is and why someone would use it, then the honest
two-step setup. Numbers come from src/core/plans.py: 1 channel, 1 sender bot,
100 scheduled messages and 1 recurring rule on Free; 3/3/unlimited on Premium.

Applied by tools/apply_rbac_help_v2.py (help tree) and
tools/apply_onboarding_intro.py (the bot's tutorial screen).
"""

# ---------------------------------------------------------------- welcome ---
WELCOME = {
    'en': (
        "👋 <b>Fast Scheduler — the scheduler for your Telegram channel.</b>\n\n"
        "You write the posts; it publishes them at the exact minute you chose. "
        "Phone off, app closed, you asleep — the post still goes out. It is a "
        "publishing tool for channel owners, not a chat bot.\n\n"
        "<b>Why people keep it</b>\n"
        "• 🗓 <b>A whole week of posts in one message.</b> Send date + text pairs "
        "separated by a blank line — <code>24.12 18:00</code> then the post, an "
        "empty line, <code>25.12 12:00</code> then the next — and every pair is "
        "scheduled at once. No twelve trips through a form.\n"
        "• 🔁 <b>Recurring posts are free.</b> One repeating rule (daily, weekly, "
        "whatever you choose) is included on the Free plan; Premium lifts the "
        "limit.\n"
        "• 🖼 Photos, videos, albums and a reusable media library; bold, links, "
        "spoilers and custom emoji survive intact.\n"
        "• 📅 One list to edit, move, reschedule or cancel anything before it "
        "goes out, plus per-post views afterwards.\n"
        "• 🤖 Posts go out <i>from your own bot</i>, so the channel keeps its "
        "name and avatar — and co-admins can help without your account.\n\n"
        "Free includes 1 channel, 1 sender bot, 100 scheduled posts.\n\n"
        "<b>What happens now — two steps, under two minutes</b>\n"
        "1. 🤖 Connect your <b>sender bot</b>: your own Telegram bot, made in "
        "@BotFather in about two minutes. The green button prepares it for you.\n"
        "2. 📢 Open that bot: it links your channel and asks for the time zone.\n\n"
        "The main bot never needs to be an administrator in your channel."
    ),
    'es': (
        "👋 <b>Fast Scheduler — el programador de tu canal de Telegram.</b>\n\n"
        "Tú escribes las publicaciones; él las publica en el minuto exacto que "
        "elegiste. Móvil apagado, aplicación cerrada, tú durmiendo — la "
        "publicación sale igual. Es una herramienta de publicación para dueños "
        "de canales, no un bot de conversación.\n\n"
        "<b>Por qué la gente se lo queda</b>\n"
        "• 🗓 <b>Una semana de publicaciones en un solo mensaje.</b> Envía pares "
        "de fecha + texto separados por una línea vacía — <code>24.12 18:00</code> "
        "y el texto, línea vacía, <code>25.12 12:00</code> y el siguiente — y "
        "todos se programan de una vez. Sin doce vueltas por un formulario.\n"
        "• 🔁 <b>Las publicaciones recurrentes son gratis.</b> Una regla "
        "repetitiva (diaria, semanal, la que elijas) está incluida en el plan "
        "Free; Premium quita el límite.\n"
        "• 🖼 Fotos, vídeos, álbumes y una biblioteca de medios reutilizable; "
        "negrita, enlaces, spoilers y emoji personalizados llegan intactos.\n"
        "• 📅 Una sola lista para editar, mover, reprogramar o cancelar "
        "cualquier cosa antes de que salga, y vistas por publicación después.\n"
        "• 🤖 Las publicaciones salen <i>desde tu propio bot</i>, así el canal "
        "conserva su nombre y avatar — y los coadministradores pueden ayudar sin "
        "tu cuenta.\n\n"
        "Free incluye 1 canal, 1 bot emisor y 100 publicaciones programadas.\n\n"
        "<b>Qué pasa ahora — dos pasos, menos de dos minutos</b>\n"
        "1. 🤖 Conecta tu <b>bot emisor</b>: tu propio bot de Telegram, creado en "
        "@BotFather en unos dos minutos. El botón verde lo prepara por ti.\n"
        "2. 📢 Ábrelo: vincula tu canal y te pide la zona horaria.\n\n"
        "El bot principal nunca necesita ser administrador de tu canal."
    ),
    'ru': (
        "👋 <b>Fast Scheduler — планировщик для вашего Telegram-канала.</b>\n\n"
        "Вы пишете посты — он публикует их в выбранную минуту. Телефон "
        "выключен, приложение закрыто, вы спите — пост всё равно выйдет. Это "
        "инструмент публикации для владельцев каналов, а не чат-бот.\n\n"
        "<b>Почему им пользуются</b>\n"
        "• 🗓 <b>Неделя постов одним сообщением.</b> Отправьте пары «дата + "
        "текст» через пустую строку — <code>24.12 18:00</code> и текст, пустая "
        "строка, <code>25.12 12:00</code> и следующий — и все они встанут в "
        "расписание сразу. Без десятка проходов по форме.\n"
        "• 🔁 <b>Повторяющиеся посты бесплатны.</b> Одно правило повтора "
        "(ежедневно, еженедельно — на ваш выбор) входит в бесплатный план; "
        "Premium снимает ограничение.\n"
        "• 🖼 Фото, видео, альбомы и переиспользуемая медиатека; жирный текст, "
        "ссылки, спойлеры и кастомные эмодзи сохраняются.\n"
        "• 📅 Один список, где можно отредактировать, перенести, "
        "перепланировать или отменить что угодно до публикации, а после — "
        "посмотреть просмотры каждого поста.\n"
        "• 🤖 Посты выходят <i>от вашего собственного бота</i>, поэтому канал "
        "сохраняет имя и аватар — а соадминистраторы могут помогать без вашего "
        "аккаунта.\n\n"
        "Бесплатно: 1 канал, 1 бот-отправитель, 100 запланированных постов.\n\n"
        "<b>Что дальше — два шага, меньше двух минут</b>\n"
        "1. 🤖 Подключите <b>бота-отправителя</b>: своего Telegram-бота, "
        "созданного в @BotFather примерно за две минуты. Зелёная кнопка "
        "подготовит его за вас.\n"
        "2. 📢 Откройте его: он привяжет канал и спросит часовой пояс.\n\n"
        "Основному боту права администратора в вашем канале не нужны никогда."
    ),
}

# --------------------------------------------------------- getting_started ---
GS_EN = {
    'title': 'Get Started: What Fast Scheduler Does',
    'description': (
        'What Fast Scheduler is, why channel owners use it, the two-step setup '
        '(sender bot first, then the channel and its time zone) and your first post.'
    ),
    'content': (
        "<p><b>Fast Scheduler publishes posts to your Telegram channel at the date and time you "
        "choose.</b> You write the post once, tell the bot when it should go out, and it sends it "
        "later — even if your phone is off or the app is closed. It is a publishing tool for "
        "channel owners, not a chat bot: there is nothing to talk to, only a queue to fill.</p>"

        "<h2>Why people use it</h2>"
        "<p>• <b>A week of posts in one message.</b> Send date + text pairs separated by a blank "
        "line and all of them are scheduled at once — see the example below. This is the feature "
        "most owners switch for: it turns a weekend of writing into one send.</p>"
        "<p>• <b>Recurring posts are free.</b> One repeating rule — daily, weekly, every Monday at "
        "9:00 — is included on the Free plan, so a channel can run its regular slots without a "
        "subscription. Premium lifts the rule limit.</p>"
        "<p>• <b>Media that survives the trip.</b> Photos, videos, albums, a reusable media "
        "library, and formatting — bold, italic, links, code, spoilers, custom emoji — is "
        "preserved exactly as you sent it.</p>"
        "<p>• <b>One list for everything.</b> Edit, move, reschedule or cancel anything before it "
        "goes out; afterwards the same entry shows views and delivery status. Search and filters "
        "find a post without scrolling.</p>"
        "<p>• <b>Posts go out from your own bot.</b> The channel keeps its own name, avatar and "
        "posting identity, and co-administrators can schedule too — each with the permissions "
        "the owner grants them ([[admins|Admins &amp; Access]]).</p>"
        "<p>• <b>Plans in one line.</b> Free: 1 channel, 1 sender bot, 100 scheduled posts, 1 "
        "recurring rule. Premium: 3 channels, 3 sender bots, unlimited scheduled and recurring "
        "posts, longer media, exports and backups.</p>"

        "<h2>What you need before you start</h2>"
        "<p>• A Telegram channel where <b>you are an administrator</b> — the bot verifies this "
        "before it links anything.</p>"
        "<p>• A <b>sender bot</b>: your own Telegram bot, created in @BotFather in about two "
        "minutes. Every connected channel uses one, and it is the bot that actually publishes. "
        "You do not need to write code or host anything.</p>"

        "<h2>The two setup steps, in this order</h2>"
        "<p><b>1. Connect your sender bot.</b> In the bot, tap <b>➕ Create bot</b> (it opens "
        "@BotFather with the name already prepared) or <b>🔑 I Have a Token</b> if you already "
        "own a bot. The token is verified with Telegram and stored. Full detail: "
        "[[sender_bot_setup|Sender Bot First: the New Setup]].</p>"
        "<p><b>2. Open that bot to link the channel and set the time zone.</b> The sender bot "
        "opens on an <i>I'm live</i> screen whose first row is a green <b>Add bot to a channel</b> "
        "button: it opens Telegram's own channel picker with the bot pre-selected and <b>Post "
        "Messages</b> already ticked. After you confirm, the bot re-checks by itself ten seconds "
        "later. Then it asks for the zone — a city, your current time, a shared location or "
        "<b>📋 Choose from list</b> — and stores it <i>for that channel</i>. A zone you set for "
        "another channel is never overwritten.</p>"
        "<p>Forwarding a post from the channel, sending <code>@username</code> or a "
        "<code>t.me</code> link, and adding the bot from a private channel's own settings all "
        "still work: [[channel_connect|Connecting a Channel]]. If the channel already has a "
        "sender bot and you are one of its administrators, you do not need the owner — send that "
        "bot's @username or token and the bot verifies your rights: "
        "[[admins_attach|Join a Channel That Already Has a Bot]].</p>"
        "<p><b>The main bot never needs to be an administrator in your channel.</b> It is your "
        "account hub — channels, sender bots, Premium, help. Keeping it as an admin is optional "
        "and only matters if you want the stand-in safety net "
        "([[main_bot_stand_in|Main-Bot Stand-In]]).</p>"

        "<h2>What the first-run tutorial actually shows</h2>"
        "<p>After <code>/start</code> and the terms screen, the bot introduces itself — what it "
        "does, why it is worth using, and what the two steps are — then asks for the sender bot. "
        "That is the whole tutorial in the main bot; the channel and the time zone are handled "
        "inside the sender bot, where the actual publishing lives. Every screen can be skipped "
        "safely: nothing is deleted, and [[tutorial_walkthrough|the step-by-step walkthrough]] "
        "picks up wherever you left off.</p>"

        "<h2>Your very first post</h2>"
        "<p>Open the <b>sender bot</b> → <b>📅 Schedule a Message</b> and send the date and the "
        "text in one message:</p>"
        "<pre>25.12.2026 10:00\nHappy holidays from our channel!</pre>"
        "<p>To queue several at once, separate the pairs with one empty line:</p>"
        "<pre>24.12.2026 18:00\nChristmas Eve: doors open at 18:00\n\n"
        "25.12.2026 12:00\nToday's menu and the holiday playlist\n\n"
        "26.12.2026 09:00\nThank you for the year — see you in January</pre>"
        "<p>The bot shows a review card per message with the channel, the time and a preview. "
        "Check it, confirm, and the queue is built. Media, buttons and the per-post options are "
        "explained in [[start_schedule|Send Your First Post]].</p>"

        "<h2>If something does not work</h2>"
        "<p>• <b>\"A sender bot is required\"</b> — that channel has no bot yet: "
        "[[connect_bot|Connecting a Bot]].</p>"
        "<p>• <b>The channel looks locked in a picker</b> — it is managed by its sender bot; tap "
        "it and choose <b>🤖 Open Sender Bot</b>, scheduling happens there.</p>"
        "<p>• <b>\"Bot is not an admin\"</b> — promote the sender bot in the channel with Post "
        "Messages: [[channel_permissions|Channel Permissions]].</p>"
        "<p>• <b>Post went out at the wrong hour</b> — the channel's own time zone is used: "
        "[[troubleshoot_late|Why Was My Scheduled Post Published at the Wrong Time?]]</p>"

        "<h2>Where to go next</h2>"
        "<p>• [[interface_map|Every Menu and Button: the Interface Map]] — what each screen opens, "
        "written so a person or an AI assistant can follow the exact path.<br>"
        "• [[media_types|Media Modes Explained]] — Normal, Random, Sequential and Skip.<br>"
        "• [[commands_list|All Commands]] — every command the bot accepts.<br>"
        "• [[admins|Admins &amp; Access]] — letting a co-administrator schedule safely.</p>"
    ),
    'faq': [
        {'q': 'Do I need to know how to code to use Fast Scheduler?',
         'a': 'No. You create a bot in @BotFather by tapping a few buttons, and the bot walks you '
              'through the rest. Nothing is hosted, installed or programmed by you.',
         'links': ['sender_bot_setup']},
        {'q': 'How many posts can I schedule for free?',
         'a': 'One channel, one sender bot, 100 scheduled messages and one recurring rule. '
              'Premium raises this to three channels, three bots and unlimited scheduled and '
              'recurring posts.',
         'links': ['limits', 'premium']},
        {'q': 'Can I schedule a whole week at once?',
         'a': 'Yes — send date + text pairs separated by an empty line and every pair becomes its '
              'own scheduled post with its own time.',
         'links': ['qa_schedule_many_at_once']},
        {'q': 'Does the main bot need to be an administrator in my channel?',
         'a': 'No. Publishing runs through your sender bot. Adding the main bot as an admin is '
              'optional and only used for the stand-in when your sender bot breaks.',
         'links': ['main_bot_stand_in']},
    ],
}

GS_ES = {
    'title': 'Empezar: qué hace Fast Scheduler',
    'description': (
        'Qué es Fast Scheduler, por qué lo usan los dueños de canales, la '
        'configuración en dos pasos (primero el bot emisor, después el canal y su '
        'zona horaria) y tu primera publicación.'
    ),
    'content': (
        "<p><b>Fast Scheduler publica en tu canal de Telegram en la fecha y hora que elijas.</b> "
        "Escribes la publicación una vez, le dices al bot cuándo debe salir y la envía más tarde — "
        "aunque tu móvil esté apagado o la aplicación cerrada. Es una herramienta de publicación "
        "para dueños de canales, no un bot de conversación: no hay nada de qué hablar, solo una "
        "cola que llenar.</p>"

        "<h2>Por qué se usa</h2>"
        "<p>• <b>Una semana de publicaciones en un solo mensaje.</b> Envía pares de fecha + texto "
        "separados por una línea vacía y todos se programan de una vez. Es la función por la que "
        "la mayoría cambia de herramienta: un fin de semana de escritura se convierte en un solo "
        "envío.</p>"
        "<p>• <b>Las publicaciones recurrentes son gratis.</b> Una regla repetitiva —diaria, "
        "semanal, cada lunes a las 9:00— está incluida en el plan Free, así que un canal mantiene "
        "sus franjas fijas sin suscripción. Premium quita el límite de reglas.</p>"
        "<p>• <b>Los medios llegan intactos.</b> Fotos, vídeos, álbumes, una biblioteca de medios "
        "reutilizable y el formato —negrita, cursiva, enlaces, código, spoilers, emoji "
        "personalizados— se conservan tal como los enviaste.</p>"
        "<p>• <b>Una sola lista para todo.</b> Edita, mueve, reprograma o cancela antes de que "
        "salga; después la misma entrada muestra vistas y estado de entrega. Búsqueda y filtros "
        "encuentran una publicación sin recorrer la lista.</p>"
        "<p>• <b>Las publicaciones salen desde tu propio bot.</b> El canal conserva su nombre, "
        "avatar e identidad de publicación, y los coadministradores también pueden programar, "
        "cada uno con los permisos que conceda el dueño ([[admins|Administradores y acceso]]).</p>"
        "<p>• <b>Planes en una línea.</b> Free: 1 canal, 1 bot emisor, 100 publicaciones "
        "programadas y 1 regla recurrente. Premium: 3 canales, 3 bots, publicaciones programadas "
        "y recurrentes ilimitadas, medios más grandes, exportaciones y copias de seguridad.</p>"

        "<h2>Qué necesitas antes de empezar</h2>"
        "<p>• Un canal de Telegram del que <b>seas administrador</b>: el bot lo comprueba antes "
        "de vincular nada.</p>"
        "<p>• Un <b>bot emisor</b>: tu propio bot de Telegram, creado en @BotFather en unos dos "
        "minutos. Cada canal conectado usa uno, y es el bot que publica de verdad. No necesitas "
        "programar ni alojar nada.</p>"

        "<h2>Los dos pasos, en este orden</h2>"
        "<p><b>1. Conecta tu bot emisor.</b> En el bot, toca <b>➕ Crear bot</b> (abre @BotFather "
        "con el nombre ya preparado) o <b>🔑 Tengo un token</b> si ya tienes un bot. El token se "
        "verifica con Telegram y se guarda. Detalle completo: "
        "[[sender_bot_setup|Primero el bot emisor: la nueva configuración]].</p>"
        "<p><b>2. Ábrelo para vincular el canal y fijar la zona horaria.</b> El bot emisor se "
        "abre en una pantalla <i>ya estoy activo</i> cuya primera fila es el botón verde "
        "<b>Añadir el bot a un canal</b>: abre el selector de canales de Telegram con el bot "
        "preseleccionado y <b>Publicar mensajes</b> ya marcado. Cuando confirmas, el bot "
        "recomprueba solo diez segundos después. Luego pide la zona —una ciudad, tu hora actual, "
        "una ubicación compartida o <b>📋 Elegir de la lista</b>— y la guarda <i>para ese "
        "canal</i>. La zona de otro canal nunca se sobrescribe.</p>"
        "<p>Reenviar una publicación del canal, enviar <code>@usuario</code> o un enlace "
        "<code>t.me</code>, y añadir el bot desde los ajustes de un canal privado siguen "
        "funcionando: [[channel_connect|Conectar un canal]]. Si el canal ya tiene bot emisor y tú "
        "eres uno de sus administradores, no necesitas al dueño: envía el @usuario o el token de "
        "ese bot y el bot verifica tus permisos: [[admins_attach|Entrar en un canal que ya tiene "
        "bot]].</p>"
        "<p><b>El bot principal nunca necesita ser administrador de tu canal.</b> Es tu centro de "
        "cuenta —canales, bots emisores, Premium, ayuda—. Mantenerlo como admin es opcional y "
        "solo importa si quieres la red de seguridad de sustitución "
        "([[main_bot_stand_in|Sustituto del bot principal]]).</p>"

        "<h2>Qué muestra el tutorial inicial</h2>"
        "<p>Tras <code>/start</code> y la pantalla de términos, el bot se presenta —qué hace, por "
        "qué merece la pena y cuáles son los dos pasos— y luego pide el bot emisor. Ese es todo "
        "el tutorial en el bot principal; el canal y la zona horaria se gestionan dentro del bot "
        "emisor, donde vive la publicación real. Cada pantalla se puede omitir sin riesgo: no se "
        "borra nada y [[tutorial_walkthrough|la guía paso a paso]] continúa donde lo dejaste.</p>"

        "<h2>Tu primera publicación</h2>"
        "<p>Abre el <b>bot emisor</b> → <b>📅 Programar un mensaje</b> y envía la fecha y el texto "
        "en un solo mensaje:</p>"
        "<pre>25.12.2026 10:00\n¡Felices fiestas de parte de nuestro canal!</pre>"
        "<p>Para encolar varias a la vez, separa los pares con una línea vacía:</p>"
        "<pre>24.12.2026 18:00\nNochebuena: abrimos a las 18:00\n\n"
        "25.12.2026 12:00\nMenú de hoy y la lista de villancicos\n\n"
        "26.12.2026 09:00\nGracias por el año — nos vemos en enero</pre>"
        "<p>El bot muestra una tarjeta de revisión por mensaje con el canal, la hora y la vista "
        "previa. Revísala, confirma y la cola queda armada. Medios, botones y las opciones por "
        "publicación están en [[start_schedule|Envía tu primera publicación]].</p>"

        "<h2>Si algo no funciona</h2>"
        "<p>• <b>«Se requiere un bot emisor»</b> — ese canal aún no tiene bot: "
        "[[connect_bot|Conectar un bot]].</p>"
        "<p>• <b>El canal aparece bloqueado en el selector</b> — lo gestiona su bot emisor; "
        "tócalo y elige <b>🤖 Abrir bot emisor</b>, ahí ocurre la programación.</p>"
        "<p>• <b>«El bot no es administrador»</b> — promueve el bot emisor en el canal con "
        "Publicar mensajes: [[channel_permissions|Permisos del canal]].</p>"
        "<p>• <b>La publicación salió a la hora equivocada</b> — se usa la zona horaria del "
        "canal: [[troubleshoot_late|¿Por qué se publicó a la hora equivocada?]]</p>"

        "<h2>Por dónde seguir</h2>"
        "<p>• [[media_types|Modos de medios explicados]]<br>"
        "• [[commands_list|Todos los comandos]]<br>"
        "• [[admins|Administradores y acceso]]</p>"
    ),
    'faq': [
        {'q': '¿Hay que saber programar para usar Fast Scheduler?',
         'a': 'No. Creas un bot en @BotFather pulsando unos botones y el bot te guía por el '
              'resto. No alojas, instalas ni programas nada.',
         'links': ['sender_bot_setup']},
        {'q': '¿Cuántas publicaciones puedo programar gratis?',
         'a': 'Un canal, un bot emisor, 100 mensajes programados y una regla recurrente. '
              'Premium lo eleva a tres canales, tres bots y publicaciones ilimitadas.',
         'links': ['limits', 'premium']},
        {'q': '¿Puedo programar una semana entera de una vez?',
         'a': 'Sí: envía pares de fecha + texto separados por una línea vacía y cada par se '
              'convierte en su propia publicación programada con su hora.',
         'links': ['qa_schedule_many_at_once']},
        {'q': '¿El bot principal debe ser administrador de mi canal?',
         'a': 'No. La publicación va por tu bot emisor. Añadir el bot principal como admin es '
              'opcional y solo se usa para la sustitución cuando tu bot emisor falla.',
         'links': ['main_bot_stand_in']},
    ],
}

GS_RU = {
    'title': 'С чего начать: что умеет бот',
    'description': (
        'Что такое Fast Scheduler, зачем он владельцам каналов, настройка в два '
        'шага (сначала бот-отправитель, затем канал и его часовой пояс) и первый пост.'
    ),
    'content': (
        "<p><b>Fast Scheduler публикует посты в вашем Telegram-канале в выбранные вами дату и "
        "время.</b> Вы пишете пост один раз, говорите боту, когда его выпустить, — и он "
        "отправляет его позже, даже если телефон выключен или приложение закрыто. Это "
        "инструмент публикации для владельцев каналов, а не чат-бот: говорить не с кем, есть "
        "только очередь, которую нужно заполнить.</p>"

        "<h2>Зачем он нужен</h2>"
        "<p>• <b>Неделя постов одним сообщением.</b> Отправьте пары «дата + текст» через пустую "
        "строку — и все они встанут в расписание сразу. Именно из-за этой функции чаще всего "
        "переходят: выходные, потраченные на тексты, превращаются в одну отправку.</p>"
        "<p>• <b>Повторяющиеся посты бесплатны.</b> Одно правило повтора — ежедневно, "
        "еженедельно, каждый понедельник в 9:00 — входит в бесплатный план, так что канал "
        "держит свои постоянные слоты без подписки. Premium снимает лимит правил.</p>"
        "<p>• <b>Медиа доходят целыми.</b> Фото, видео, альбомы, переиспользуемая медиатека и "
        "форматирование — жирный, курсив, ссылки, код, спойлеры, кастомные эмодзи — "
        "сохраняются ровно так, как вы отправили.</p>"
        "<p>• <b>Один список для всего.</b> Редактируйте, переносите, перепланируйте или "
        "отменяйте до публикации; после — та же запись показывает просмотры и статус доставки. "
        "Поиск и фильтры находят пост без прокрутки.</p>"
        "<p>• <b>Посты выходят от вашего собственного бота.</b> Канал сохраняет имя, аватар и "
        "лицо публикаций, а соадминистраторы тоже могут планировать — каждый с правами, "
        "которые выдал владелец ([[admins|Админы и доступ]]).</p>"
        "<p>• <b>Тарифы в одну строку.</b> Бесплатно: 1 канал, 1 бот-отправитель, 100 "
        "запланированных постов, 1 правило повтора. Premium: 3 канала, 3 бота, неограниченные "
        "посты и повторы, большие медиа, экспорт и резервные копии.</p>"

        "<h2>Что нужно до начала</h2>"
        "<p>• Telegram-канал, в котором <b>вы администратор</b>: бот проверяет это до привязки.</p>"
        "<p>• <b>Бот-отправитель</b>: ваш собственный Telegram-бот, созданный в @BotFather "
        "примерно за две минуты. Каждый подключённый канал использует одного, и публикует "
        "именно он. Программировать и что-то размещать на сервере не нужно.</p>"

        "<h2>Два шага, именно в этом порядке</h2>"
        "<p><b>1. Подключите бота-отправителя.</b> В боте нажмите <b>➕ Создать бота</b> "
        "(откроется @BotFather с уже подготовленным именем) или <b>🔑 У меня есть токен</b>, "
        "если бот уже есть. Токен проверяется через Telegram и сохраняется. Подробно: "
        "[[sender_bot_setup|Сначала бот-отправитель]].</p>"
        "<p><b>2. Откройте его, чтобы привязать канал и задать часовой пояс.</b> Бот-отправитель "
        "открывается на экране <i>я на связи</i>, первая строка которого — зелёная кнопка "
        "<b>Добавить бота в канал</b>: она открывает выбор канала Telegram с уже выбранным "
        "ботом и отмеченным правом <b>Публикация сообщений</b>. После подтверждения бот сам "
        "перепроверит через десять секунд. Затем он спросит пояс — город, текущее время, "
        "геолокацию или <b>📋 Выбрать из списка</b> — и сохранит его <i>для этого канала</i>. "
        "Пояс другого канала никогда не перезаписывается.</p>"
        "<p>Пересылка любого поста из канала, отправка <code>@username</code> или ссылки "
        "<code>t.me</code> и добавление бота из настроек приватного канала тоже работают: "
        "[[channel_connect|Подключение канала]]. Если у канала уже есть бот-отправитель, а вы "
        "один из его администраторов, владелец не нужен: отправьте @username или токен этого "
        "бота, и он проверит ваши права: [[admins_attach|Вход в канал, где уже есть бот]].</p>"
        "<p><b>Основному боту права администратора в вашем канале не нужны никогда.</b> Он — "
        "центр аккаунта: каналы, боты-отправители, Premium, справка. Оставлять его админом "
        "необязательно, и это нужно только для подстраховки, если ваш бот-отправитель "
        "сломается ([[main_bot_stand_in|Подмена главным ботом]]).</p>"

        "<h2>Что показывает первый запуск</h2>"
        "<p>После <code>/start</code> и экрана условий бот представляется: что он делает, "
        "почему им стоит пользоваться и какие два шага впереди, — а затем просит "
        "бота-отправителя. Это весь туториал в главном боте; канал и часовой пояс настраиваются "
        "внутри бота-отправителя, где живёт публикация. Любой экран можно пропустить без "
        "риска: ничего не удаляется, а [[tutorial_walkthrough|пошаговая инструкция]] продолжит "
        "с того места, где вы остановились.</p>"

        "<h2>Ваш первый пост</h2>"
        "<p>Откройте <b>бота-отправителя</b> → <b>📅 Запланировать сообщение</b> и отправьте "
        "дату и текст одним сообщением:</p>"
        "<pre>25.12.2026 10:00\nС праздником, дорогие подписчики!</pre>"
        "<p>Чтобы поставить в очередь несколько сразу, разделите пары одной пустой строкой:</p>"
        "<pre>24.12.2026 18:00\nСочельник: открываемся в 18:00\n\n"
        "25.12.2026 12:00\nПраздничное меню и плейлист\n\n"
        "26.12.2026 09:00\nСпасибо за этот год — до встречи в январе</pre>"
        "<p>Бот покажет карточку проверки для каждого сообщения: канал, время и предпросмотр. "
        "Проверьте, подтвердите — и очередь собрана. Медиа, кнопки и настройки отдельного поста "
        "описаны в [[start_schedule|Отправьте свой первый пост]].</p>"

        "<h2>Если что-то не работает</h2>"
        "<p>• <b>«Требуется бот-отправитель»</b> — у этого канала ещё нет бота: "
        "[[connect_bot|Подключение бота]].</p>"
        "<p>• <b>Канал выглядит заблокированным в списке</b> — им управляет его "
        "бот-отправитель; нажмите на него и выберите <b>🤖 Открыть бота-отправителя</b>, "
        "планирование происходит там.</p>"
        "<p>• <b>«Бот не администратор»</b> — выдайте боту-отправителю право «Публикация "
        "сообщений» в канале: [[channel_permissions|Права канала]].</p>"
        "<p>• <b>Пост вышел не в тот час</b> — используется часовой пояс канала: "
        "[[troubleshoot_late|Почему пост опубликовался не вовремя?]]</p>"

        "<h2>Куда дальше</h2>"
        "<p>• [[media_types|Режимы медиа]]<br>"
        "• [[commands_list|Все команды]]<br>"
        "• [[admins|Админы и доступ]]</p>"
    ),
    'faq': [
        {'q': 'Нужно ли уметь программировать, чтобы пользоваться Fast Scheduler?',
         'a': 'Нет. Бот создаётся в @BotFather несколькими нажатиями, а дальше бот сам ведёт '
              'по шагам. Ничего не нужно устанавливать или размещать на сервере.',
         'links': ['sender_bot_setup']},
        {'q': 'Сколько постов можно запланировать бесплатно?',
         'a': 'Один канал, один бот-отправитель, 100 запланированных сообщений и одно правило '
              'повтора. Premium поднимает это до трёх каналов, трёх ботов и неограниченных '
              'постов и повторов.',
         'links': ['limits', 'premium']},
        {'q': 'Можно ли запланировать сразу целую неделю?',
         'a': 'Да: отправьте пары «дата + текст» через пустую строку — каждая пара станет '
              'отдельным запланированным постом со своим временем.',
         'links': ['qa_schedule_many_at_once']},
        {'q': 'Должен ли главный бот быть администратором моего канала?',
         'a': 'Нет. Публикация идёт через бота-отправителя. Добавлять главного бота админом '
              'необязательно — это нужно только для подмены, если бот-отправитель сломается.',
         'links': ['main_bot_stand_in']},
    ],
}

def _markup_to_source(html):
    """Convert the editorial markup above into what the builders render.

    Help article bodies are plain text with blank-line paragraphs, "## "
    headings and inline <b>/<i>/<code> only — raw block tags are escaped and
    would show up as "&lt;p&gt;" on the page. Authoring stays readable here and
    this pass produces the source format (same trick build_help uses for ASCII
    tables): block tags become blank lines, headings become "## ", <pre> lines
    become <code> lines.
    """
    import re
    text = html
    text = re.sub(r'<pre>(.*?)</pre>', lambda m: '\n\n' + '\n'.join(
        ('<code>%s</code>' % line) if line.strip() else ''
        for line in m.group(1).splitlines()) + '\n\n', text, flags=re.S)
    text = re.sub(r'<h2>(.*?)</h2>', lambda m: '\n\n## %s\n' % m.group(1).strip(), text, flags=re.S)
    text = re.sub(r'<p[^>]*>', '', text)
    text = text.replace('</p>', '')
    text = text.replace('<br>', '\n')
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


for _lang, _gs in (('en', GS_EN), ('es', GS_ES), ('ru', GS_RU)):
    _gs['content'] = _markup_to_source(_gs['content'])

CONTENT_GS = {'en': {'getting_started': GS_EN},
              'es': {'getting_started': GS_ES},
              'ru': {'getting_started': GS_RU}}
