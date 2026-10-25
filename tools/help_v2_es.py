# -*- coding: utf-8 -*-
"""Spanish help content for the sender-bot-first setup and the RBAC rewrite.

Same structure as ``help_v2_en.py``; consumed by ``tools/apply_rbac_help_v2.py``.
Numbers mirror the bot's constants: 15 permissions, one request per permission
per week, 24-hour transfer, 5 automatic checks per day, 3-day default stand-in.
"""

CONTENT_ES = {}

CONTENT_ES['admins'] = {
    'title': 'Administradores y acceso (RBAC)',
    'description': (
        'Guía completa del acceso al canal: quién cuenta como administrador, las dos formas de '
        'entrar, qué puede hacer cada rol, cómo el dueño mantiene el control y qué no ve nunca nadie.'
    ),
    'content': (
        'Los administradores son otras cuentas de Telegram que trabajan en tu canal sin ser sus '
        'dueñas. El acceso se decide en dos capas: <b>Telegram</b> dice quién puede administrar el '
        'canal y <b>Fast Scheduler</b> decide qué puede hacer cada una dentro del bot. Las dos deben '
        'coincidir: un administrador de Telegram sin permisos en el bot abre el bot de envío y solo '
        've lo que se le concedió.\n\n'

        '## Los tres roles\n'
        '• <b>Dueño principal</b>: la cuenta que configuró el canal. Tiene todos los permisos, no se '
        'le puede limitar y es el único que puede cambiar permisos, quitar administradores o '
        'transferir la propiedad. Hay exactamente uno por canal.\n'
        '• <b>Administrador</b>: un administrador de Telegram de ese canal añadido al bot. Trabaja con '
        'los 15 permisos de [[admins_permissions|Permisos y solicitudes]]; al empezar tiene activos '
        'programar, recurrentes, lista de mensajes, vista previa, editar, buscar y estadísticas.\n'
        '• <b>Revocado</b>: alguien a quien el dueño quitó el acceso. Se guarda su registro (quién y '
        'cuándo) para que no pueda volver a entrar por su cuenta; solo el dueño puede restaurarlo.\n\n'

        '## Dos formas de ser administrador\n'
        '1. <b>El dueño lo añade.</b> En el <b>bot de envío</b> del canal → <b>⚙️ Ajustes</b> → '
        '<b>👥 Admins</b>. El bot sincroniza la lista de administradores de Telegram y crea el '
        'registro con los permisos por defecto.\n'
        '2. <b>Un coadministrador demuestra sus derechos.</b> Si el canal ya tiene bot de envío, '
        'cualquier administrador de Telegram puede enviar al bot el <b>@usuario</b> o el <b>token</b> '
        'de ese bot. El bot pregunta a Telegram, a través de ese bot, si quien escribe es '
        'administrador de su canal; si lo es, concede los permisos por defecto y avisa al dueño. '
        'Guía completa: [[admins_attach|Entrar en un canal que ya tiene bot]].\n\n'

        '## Dónde está y por qué\n'
        'La gestión de admins vive dentro del <b>bot de envío de ese canal</b>, nunca en el bot '
        'principal. Un bot de envío atiende un solo canal, así que un registro de permisos tiene un '
        'solo ámbito. El bot principal no sabe quién te ayuda.\n\n'

        '## Alcance: un canal y nada más\n'
        'Un registro está ligado a un id de canal. Un admin del canal A no ve el canal B: ni en la '
        'lista de canales, ni en mensajes, estadísticas, almacenamiento, menú de bots, exportación ni '
        'notificaciones. Tampoco ve otros canales del dueño ni recibe sus pagos o avisos de '
        'caducidad.\n\n'

        '## Control en el servidor, en el momento del clic\n'
        'Cada botón, cada paso escrito y cada enlace profundo vuelven a comprobar el permiso al usarse, '
        'no cuando se dibujó el teclado. Si un permiso desaparece mientras un mensaje viejo sigue en '
        'pantalla, su botón responde «no tienes permiso» y ofrece <b>Solicitar permiso al '
        'administrador</b>; nunca ejecuta la acción.\n\n'

        '## Privacidad: Ocultar canal a desconocidos\n'
        'Con <b>Ocultar canal a desconocidos</b> activo, todo el que no es dueño —incluidos los '
        'coadministradores y quien verifica con un @usuario— ve el canal como <i>este canal</i>: sin '
        'título, @usuario, enlace <code>t.me</code> ni id numérico, en confirmaciones, rechazos y '
        'avisos. El dueño siempre ve el nombre real. Ese ajuste es en sí un permiso '
        '(<code>settings_hide_channel</code>), así que un admin no puede desactivarlo para mirar.\n\n'

        '## Registro de auditoría\n'
        'Cada concesión, guardado de permisos, revocación, restauración, auto-vinculación y '
        'transferencia se escribe con actor, objetivo, canal, fecha y motivo. «¿Quién dio permiso de '
        'borrar?» tiene respuesta.\n\n'

        '## Revocación automática\n'
        'En cada sincronización el bot relee los administradores del canal. Si alguien fue quitado en '
        'Telegram, perdió <b>Publicar mensajes</b> o fue bloqueado por el dueño, su acceso se revoca '
        'solo: sin limpieza manual y sin ventana en la que siga trabajando desde un teclado viejo.\n\n'

        '## Lo que un admin no puede hacer nunca\n'
        '• Quedarse el canal sin que el dueño inicie una transferencia y el destino la acepte.\n'
        '• Ver o usar el token del bot de envío del dueño, ni añadir, quitar o renombrar bots.\n'
        '• Llegar a otro canal del mismo dueño.\n'
        '• Conceder permisos (salvo <code>settings_change_permissions</code>).\n'
        '• Borrar el canal, sus datos o su historial.\n'
        '• Activar el sustituto del bot principal (solo el dueño o ese permiso de ajustes).\n\n'

        '## Relacionado\n'
        '[[admins_attach|Entrar en un canal que ya tiene bot]], '
        '[[admins_permissions|Permisos y solicitudes]], [[admins_limits|Cómo se comparten los límites]], '
        '[[admins_transfer|Transferencia de propiedad]], '
        '[[sender_bot_setup|Primero el bot de envío: la nueva configuración]].'
    ),
    'children': ['admins_attach', 'admins_permissions', 'admins_limits', 'admins_transfer'],
    'faq': [
        {
            'q': '¿Puede un administrador quedarse con mi canal?',
            'a': 'No. La propiedad solo cambia si el dueño actual inicia la transferencia, escribe la '
                 'frase de confirmación y el destino la acepta en 24 horas. Un admin no puede '
                 'iniciarla ni darse ese permiso.',
            'links': ['admins_transfer'],
        },
        {
            'q': '¿Por qué el bot principal ya no tiene que ser administrador del canal?',
            'a': 'Porque ya no toca el canal: publica tu bot de envío y el principal solo habla '
                 'contigo. La única excepción es el sustituto opcional, que publica en tu nombre '
                 'durante una ventana limitada si tu bot de envío falla.',
            'links': ['sender_bot_setup', 'main_bot_stand_in'],
        },
        {
            'q': 'Un admin dice que el bot lo rechaza, pero en Telegram es administrador.',
            'a': 'Comprueba tres cosas: que abrió el <b>bot de envío</b> de ese canal (no el '
                 'principal), que tiene <b>Publicar mensajes</b> y que el dueño no lo revocó. Un admin '
                 'revocado sigue bloqueado hasta que el dueño lo restaure.',
            'links': ['admins_permissions', 'bot_permissions'],
        },
        {
            'q': '¿Pueden dos personas gestionar el mismo canal sin compartir cuenta?',
            'a': 'Sí, para eso están los admins. Cada persona conecta su cuenta de Telegram, recibe '
                 'sus permisos y cada acción queda atribuida en el registro de auditoría.',
            'links': ['admins_attach'],
        },
        {
            'q': '¿Los admins comparten los límites del canal?',
            'a': 'Sí. Los huecos de programación, los envíos mensuales, las reglas recurrentes y el '
                 'almacenamiento pertenecen al canal, así que todos tiran de la misma cuota.',
            'links': ['admins_limits'],
        },
        {
            'q': '¿Cómo quito a alguien por completo?',
            'a': 'Ajustes → Admins → su perfil → Quitar. El acceso termina al instante y el registro '
                 'pasa a Revocados con motivo y fecha. Los mensajes en cola se quedan en el canal.',
            'links': ['admins_permissions'],
        },
    ],
}

CONTENT_ES['admins_attach'] = {
    'title': 'Entrar en un canal que ya tiene bot',
    'description': (
        'Eres administrador del canal, el canal ya tiene bot de envío y el dueño no está: cómo '
        'demostrar tus derechos con el @usuario o el token del bot y obtener acceso sin pulsar nada.'
    ),
    'content': (
        'Un canal solo puede tener un bot de envío. Si acabas de ser administrador en Telegram y el '
        'canal ya está gestionado aquí, no necesitas al dueño: demuestra tus derechos una vez y el bot '
        'te concede los permisos por defecto.\n\n'

        '## Qué enviar\n'
        'Envía como mensaje normal, al bot principal o al propio bot de envío:\n'
        '• el <b>@usuario</b> del bot de envío — por ejemplo <code>@Mi_Bot_Canal</code>; o\n'
        '• su <b>token</b> — la línea <code>1234567890:ABCdef…</code> de @BotFather.\n'
        'No pulses ningún botón del menú antes: el mensaje es la solicitud.\n\n'

        '## Qué pasa después\n'
        '1. El bot resuelve el usuario (o llama a <code>getMe</code> con el token) y localiza el canal '
        'que sirve ese bot.\n'
        '2. Pregunta a Telegram, <i>a través de ese bot de envío</i>, cuál es tu estado en el canal.\n'
        '3. Si Telegram responde <b>administrator</b> o <b>creator</b>, te añade con los permisos por '
        'defecto: programar, recurrentes, lista, vista previa, editar, buscar y estadísticas.\n'
        '4. El dueño recibe un aviso con tu nombre (y el canal solo si no está oculto).\n'
        '5. Recibes un botón verde <b>Abrir @bot</b> que te lleva al bot de envío.\n\n'

        '## Si te rechaza\n'
        '• <b>«No pude confirmarte como administrador»</b>: Telegram no te lista como admin de ese '
        'canal o no eres la cuenta que escribe. Pide el rol primero y reintenta.\n'
        '• <b>«El acceso fue revocado»</b>: el dueño te quitó a propósito; solo él puede restaurarte.\n'
        '• <b>«Ese bot aún no está conectado a un canal»</b>: existe pero nunca se vinculó.\n'
        '• <b>«Demasiados intentos»</b>: la verificación tiene límite por hora y cuenta. Espera una '
        'hora; no se pierde nada.\n\n'

        '## Privacidad con el canal oculto\n'
        'Si el dueño activó <b>Ocultar canal a desconocidos</b>, la confirmación dice <i>este canal</i> '
        'y no muestra título, @usuario, enlace ni id. No es un fallo: es su ajuste y también se aplica '
        'a los admins. Tu acceso es real; pide el enlace al dueño si lo necesitas.\n\n'

        '## Sobre el token\n'
        'Enviar el token al bot al que quieres entrar es cómo la verificación lee tus derechos a '
        'través de ese bot. Se usa para la comprobación y no se devuelve. Aun así, trátalo como una '
        'contraseña: solo en chat privado con el bot, nunca en un grupo o captura. Si no quieres '
        'enviarlo, el @usuario basta.\n\n'

        '## Permisos que recibes\n'
        'Los valores por defecto son conservadores y están listados en '
        '[[admins_permissions|Permisos y solicitudes]]. Si necesitas más, usa <b>Solicitar permiso al '
        'administrador</b> en cualquier pantalla de rechazo: la solicitud lleva el permiso exacto.\n\n'

        '## Relacionado\n'
        '[[admins|Administradores y acceso]], [[sender_bot_setup|Primero el bot de envío]], '
        '[[channel_permissions|Permisos del canal]].'
    ),
    'children': None,
    'faq': [
        {
            'q': '¿Necesito saber la cuenta de Telegram del dueño?',
            'a': 'No. El bot localiza el canal desde el bot de envío y avisa al dueño por su cuenta.',
            'links': ['admins'],
        },
        {
            'q': '¿Verá el dueño que he entrado?',
            'a': 'Sí, al instante, con tu nombre y el bot usado. Además queda en el registro de '
                 'auditoría.',
            'links': ['admins'],
        },
        {
            'q': '¿Puedo hacerlo si aún no soy administrador en Telegram?',
            'a': 'No, y no es un fallo: el bot solo refleja derechos que Telegram ya concedió. Pide '
                 'primero que te asciendan.',
            'links': ['channel_permissions'],
        },
        {
            'q': 'El @usuario es correcto pero dice que no está conectado.',
            'a': 'Ese bot de envío existe pero no tiene canal vinculado. Pide al dueño que termine su '
                 'configuración.',
            'links': ['sender_bot_setup'],
        },
    ],
}

CONTENT_ES['admins_permissions'] = {
    'title': 'Permisos y solicitudes',
    'description': (
        'Los 15 permisos concedibles, qué desbloquea cada uno, los valores por defecto, cómo se '
        'guardan los cambios, cómo funcionan las solicitudes y cómo se revoca el acceso.'
    ),
    'content': (
        'El dueño principal controla exactamente qué puede hacer cada admin. Hay 15 permisos '
        'independientes; nada va escondido detrás de un «gestionar» genérico.\n\n'

        '## Lista completa (valor por defecto)\n'
        '• <code>schedule</code> — crear mensajes programados. <i>Activo.</i>\n'
        '• <code>recurring</code> — crear mensajes recurrentes. <i>Activo.</i>\n'
        '• <code>message_list</code> — abrir la lista de mensajes. <i>Activo.</i>\n'
        '• <code>message_preview</code> — ver la vista previa. <i>Activo.</i>\n'
        '• <code>message_edit</code> — editar un mensaje en cola. <i>Activo.</i>\n'
        '• <code>message_change</code> — mover un mensaje a otro canal. <i>Inactivo.</i>\n'
        '• <code>message_delete</code> — borrar un mensaje en cola. <i>Inactivo.</i>\n'
        '• <code>message_search</code> — buscar mensajes del canal. <i>Activo.</i>\n'
        '• <code>stats_view</code> — ver estadísticas. <i>Activo.</i>\n'
        '• <code>leaderboard_view</code> — ver la clasificación. <i>Inactivo.</i>\n'
        '• <code>data_export</code> — exportar datos del canal. <i>Inactivo.</i>\n'
        '• <code>data_import</code> — importar mensajes. <i>Inactivo.</i>\n'
        '• <code>data_backup</code> — crear copia de seguridad. <i>Inactivo.</i>\n'
        '• <code>settings_hide_channel</code> — ocultar el canal a desconocidos. <i>Inactivo.</i>\n'
        '• <code>settings_change_permissions</code> — cambiar permisos de otros admins. '
        '<i>Inactivo.</i>\n\n'

        '## Agrupados en pantalla, separados en la base de datos\n'
        'Mensajes, Estadísticas, Datos y Ajustes son solo agrupaciones para que el teclado se lea. Al '
        'abrir un grupo se ven sus interruptores individuales; guardar el grupo guarda cada uno tal '
        'como está. No hay desbloqueos ocultos.\n\n'

        '## Cambiarlos\n'
        'Dueño → <b>⚙️ Ajustes</b> → <b>👥 Admins</b> → elegir admin → alternar. Los cambios se '
        'acumulan como borrador; <b>Guardar cambios</b> los aplica y muestra un resumen. Salir con '
        'cambios sin guardar pregunta si guardar o descartar.\n\n'

        '## Efecto inmediato\n'
        'Las funciones desactivadas desaparecen del teclado del admin en la siguiente pantalla. Si '
        'pulsa un botón viejo del historial, el bot responde «no tienes permiso» y ofrece '
        '<b>Solicitar permiso al administrador</b>. La comprobación ocurre al pulsar.\n\n'

        '## Solicitudes\n'
        'Quien no tiene un permiso puede pedirlo, con un motivo de una línea. El dueño recibe la '
        'solicitud con <b>Conceder</b> / <b>Denegar</b>. Antispam: <b>una solicitud por permiso, '
        'usuario y canal por semana</b>. Una concesión queda en la auditoría; un rechazo no impide '
        'volver a pedirlo tras el plazo.\n\n'

        '## Quitar y restaurar\n'
        'Quitar un admin revoca el acceso al instante y guarda el registro en <b>Revocados</b> con '
        'motivo, actor y fecha. Un revocado no puede reentrar con el @usuario: solo el dueño lo '
        'restaura. Los mensajes en cola siguen en el canal.\n\n'

        '## Revocación automática desde Telegram\n'
        'Lo que Telegram quita, el bot lo quita: perder el rol de administrador o <b>Publicar '
        'mensajes</b> revoca el acceso en la siguiente sincronización. Lo contrario no es automático: '
        'ser admin en Telegram no concede permisos en el bot.\n\n'

        '## Lo que no se puede conceder\n'
        'La propiedad, el token del bot del dueño, añadir o renombrar bots, otros canales, datos de '
        'pago y el registro de auditoría. Para eso hace falta otro rol, no un permiso más amplio.\n\n'

        '## Relacionado\n'
        '[[admins|Administradores y acceso]], [[admins_attach|Entrar en un canal que ya tiene bot]], '
        '[[admins_transfer|Transferencia de propiedad]], [[bot_permissions|Permisos del bot]].'
    ),
    'children': None,
    'faq': [
        {
            'q': '¿Qué recibe exactamente un admin nuevo?',
            'a': 'Siete permisos activos: programar, recurrentes, lista, vista previa, editar, buscar '
                 'y estadísticas. El resto queda inactivo hasta que el dueño lo conceda.',
            'links': ['admins'],
        },
        {
            'q': '¿Cada cuánto puede pedir un permiso un admin?',
            'a': 'Una vez por permiso a la semana por canal. El plazo es por permiso: pedir exportar '
                 'no retrasa una solicitud posterior de estadísticas.',
            'links': ['admins'],
        },
        {
            'q': '¿Por qué un permiso concedido dejó de funcionar solo?',
            'a': 'O perdió la parte de Telegram (rol o Publicar mensajes) o el dueño guardó otro '
                 'conjunto. Ambas cosas quedan en la auditoría con hora y actor.',
            'links': ['bot_permissions'],
        },
        {
            'q': '¿«Cambiar permisos» permite ascenderse a sí mismo?',
            'a': 'No. Edita los interruptores de otros admins, nunca su propio registro ni la '
                 'propiedad.',
            'links': ['admins_transfer'],
        },
    ],
}

CONTENT_ES['admins_limits'] = {
    'title': 'Cómo se comparten los límites',
    'description': (
        'Los límites son del canal, no de la persona: cómo se reparten los huecos de programación, '
        'los envíos mensuales, las reglas recurrentes y el almacenamiento.'
    ),
    'content': (
        'Todos los límites de mensajes son <b>por canal</b>. Cada admin tira de la misma cuota: un '
        'canal no multiplica su cupo añadiendo personas.\n\n'

        '## Qué es compartido\n'
        '• mensajes programados pendientes ({scheduled_free} en Free por canal);\n'
        '• envíos por mes ({monthly_sent_free} por canal en Free);\n'
        '• reglas recurrentes activas ({recurring_free} en Free);\n'
        '• el almacenamiento multimedia del canal y el tamaño máximo por archivo;\n'
        '• el cupo de bots del canal (un bot de envío por canal).\n\n'

        '## En la práctica\n'
        'Si el tope de cola es 100 y un admin encola 90, al otro le quedan 10. El mensaje de límite no '
        'mira quién llenó la cola.\n\n'

        '## Contador mensual\n'
        'Cuenta mensajes <b>enviados</b>, no creados. Borrar un mensaje en cola no devuelve un envío; '
        'el contador se reinicia el día 1 del mes siguiente o cuando se activa Premium en el canal.\n\n'

        '## Premium\n'
        'Se compra por cuenta, pero sus ventajas se aplican a los canales de esa cuenta. Un '
        'coadministrador no aporta su Premium al canal de otra persona, ni se le puede cobrar por '
        'ello.\n\n'

        '## Planificar entre varios\n'
        'Ten abierta la Lista de mensajes: es la fuente de verdad de la cola. Borrar por ID es la '
        'forma segura de quitar un mensaje concreto sin tocar el trabajo de los demás. Dos admins '
        'pueden programar la misma hora: el bot no deduplica y se enviarán ambos.\n\n'

        '## Relacionado\n'
        '[[limits|Resumen de límites]], [[admins_permissions|Permisos y solicitudes]], '
        '[[limit_scheduled|Límite de programados]].'
    ),
    'children': None,
    'faq': [
        {
            'q': '¿Cada admin tiene su propio cupo mensual?',
            'a': 'No. Un canal, un cupo. Añadir admins añade manos, no cuota.',
            'links': ['limits'],
        },
        {
            'q': 'Si un admin borra un mensaje en cola, ¿se devuelve el envío?',
            'a': 'No. El contador mide envíos realizados. Borrar antes de la hora libera un hueco de '
                 'cola, pero el contador solo se mueve cuando algo se entrega.',
            'links': ['admins_permissions'],
        },
    ],
}

CONTENT_ES['admins_transfer'] = {
    'title': 'Transferencia de propiedad',
    'description': (
        'Mover el rol de Dueño principal con seguridad: frase escrita, botón final, aceptación del '
        'destino, caducidad de 24 horas y qué pasa después con ambas cuentas.'
    ),
    'content': (
        'Transferir la propiedad es difícil de hacer por accidente e imposible de hacer en solitario.\n\n'

        '## Requisitos\n'
        '• El destino debe ser ya <b>admin del canal en el bot</b>. Añádelo primero.\n'
        '• Debe seguir siendo administrador de Telegram con <b>Publicar mensajes</b>; el bot lo '
        'recomprueba en cada paso.\n'
        '• Solo puede haber una transferencia pendiente por canal.\n\n'

        '## El flujo\n'
        '1. El dueño abre el perfil del admin → <b>👑 Hacer dueño principal</b>.\n'
        '2. El bot pide escribir una frase exacta con el canal y el destino. Otra frase se rechaza.\n'
        '3. Aparece un botón final de confirmación; antes de pulsarlo no existe ninguna solicitud.\n'
        '4. El destino recibe la solicitud y debe <b>aceptar</b> o <b>rechazar</b>.\n\n'

        '## Mientras está pendiente\n'
        'El dueño actual puede cancelar en cualquier momento. La solicitud caduca a las <b>24 '
        'horas</b> y una caducada no cambia nada. Durante la espera el dueño conserva todos sus '
        'derechos: no hay estados intermedios.\n\n'

        '## Al aceptar\n'
        'El destino pasa a Dueño principal. El anterior queda como <b>admin con todos los '
        'permisos</b>: no pierde acceso, pero ya no puede cambiar permisos ni iniciar otra '
        'transferencia. Ambos reciben aviso y el cambio queda en la auditoría.\n\n'

        '## Si sale mal\n'
        'Antes de aceptar: cancela. Después: el nuevo dueño puede transferirlo de vuelta con el mismo '
        'flujo, que es justo para lo que existe la frase escrita.\n\n'

        '## Relacionado\n'
        '[[admins|Administradores y acceso]], [[admins_permissions|Permisos y solicitudes]], '
        '[[main_bot_stand_in|Sustituto del bot principal]].'
    ),
    'children': None,
    'faq': [
        {
            'q': '¿El antiguo dueño pierde el acceso?',
            'a': 'No. Pasa a admin con todos los permisos. Solo pierde los poderes exclusivos del '
                 'dueño: editar permisos, quitar admins e iniciar transferencias.',
            'links': ['admins'],
        },
        {
            'q': '¿Y si el destino no responde?',
            'a': 'La solicitud caduca en 24 horas y nada cambia. Inicia otra cuando ambos estéis '
                 'conectados.',
            'links': ['admins_permissions'],
        },
        {
            'q': '¿Puedo transferir a quien aún no es admin?',
            'a': 'No. Añádelo como admin, deja que abra el bot de envío una vez y luego inicia la '
                 'transferencia.',
            'links': ['admins_attach'],
        },
    ],
}

CONTENT_ES['sender_bot_setup'] = {
    'title': 'Primero el bot de envío: la nueva configuración',
    'description': (
        'El primer arranque reescrito: conecta tu bot de envío, añádelo al canal con un botón verde, '
        'espera diez segundos y ajusta la zona horaria del canal. Y por qué el bot principal ahora es '
        'opcional.'
    ),
    'content': (
        'La configuración empieza ahora por el bot que hace el trabajo: <b>tu bot de envío</b>. El bot '
        'principal ya no es administrador del canal y no tienes que añadirlo para empezar.\n\n'

        '## Por qué cambió el orden\n'
        'Hacer admin al bot principal era un desvío: no publica, no guarda los ajustes del canal y su '
        'único papel era verificar derechos para ceder el canal a un bot de envío. Ahora el bot de '
        'envío se verifica solo, en su propio chat.\n\n'

        '## Paso 1 — conectar el bot de envío\n'
        'Tras <code>/start</code>, la pantalla de bienvenida pide solo eso:\n'
        '• <b>➕ Crear bot</b> abre @BotFather con un nombre ya preparado;\n'
        '• <b>🔑 Tengo un token</b> acepta uno existente.\n'
        'El token se verifica con Telegram y el bot responde con un botón verde <b>Abrir '
        '@tu_bot</b>. Un bot de envío atiende exactamente un canal.\n\n'

        '## Paso 2 — añadirlo desde dentro\n'
        'Abre el bot de envío y verás la pantalla «Estoy en marcha». La primera fila es un botón verde '
        '<b>➕ Añadir bot a un canal</b>:\n'
        '1. Púlsalo. Se abre el selector de Telegram con el bot ya marcado como administrador y '
        '<b>Publicar mensajes</b> activado.\n'
        '2. Elige el canal y confirma.\n'
        '3. El bot recomprueba solo a los <b>10 segundos</b> y continúa con la zona horaria.\n\n'

        '## La regla de cinco al día\n'
        'La recomprobación automática está limitada a <b>5 pulsaciones al día</b> por cuenta, porque '
        'cada una es una llamada real a la API. La sexta sigue abriendo el selector, pero deja de '
        'vigilar; la pantalla lo dice. Después usa <b>🔄 Comprobar de nuevo</b>: las comprobaciones '
        'manuales no tienen límite.\n\n'

        '## Otras formas de conectar\n'
        '• <b>Reenviar un post</b> del canal al bot.\n'
        '• Enviar el <code>@usuario</code> o un enlace <code>t.me</code>.\n'
        '• <b>¿Canal privado?</b> Añade el bot como administrador desde los ajustes del canal; lo '
        'detecta solo.\n'
        '• ¿El canal ya tiene bot y eres coadmin? Envía su <b>@usuario</b> o <b>token</b>: '
        '[[admins_attach|Entrar en un canal que ya tiene bot]].\n\n'

        '## Paso 3 — la zona horaria es del canal\n'
        'Acepta una ciudad (<code>Madrid</code>), tu hora actual (<code>15:30</code>), una ubicación o '
        'la lista. Se guarda <b>solo para ese canal</b>. La zona por defecto de la cuenta se rellena '
        'únicamente si nunca la fijaste, así que los canales ya configurados conservan la suya.\n\n'

        '## El bot principal es opcional\n'
        'Puedes quitarlo del canal y todo sigue funcionando. Motivos para mantenerlo como admin:\n'
        '• <b>Sustituto en una avería:</b> si el token de tu bot se revoca o pierde derechos, el bot '
        'principal puede entregar el post una vez y ofrecer seguir publicando una ventana limitada '
        '(3 días por defecto). Ver [[main_bot_stand_in|Sustituto del bot principal]].\n'
        '• <b>Avisos de soporte y caducidad</b> llegan a su chat.\n'
        '• <b>Recuperación:</b> si pierdes el bot de envío, ahí reconectas otro.\n\n'

        '## Añadir más canales\n'
        '<b>➕ Añadir canal nuevo</b> ya no pide primero el enlace: lista tus bots de envío libres y al '
        'elegir uno se abre con el flujo de conexión ya iniciado.\n\n'

        '## Problemas frecuentes\n'
        '• <b>«@bot aún no es administrador»</b>: pulsa el botón verde y marca Publicar mensajes; '
        'luego Comprobar de nuevo.\n'
        '• <b>Comprobación automática en pausa</b>: usaste las cinco del día.\n'
        '• <b>Zona horaria equivocada</b>: cámbiala por canal en el bot de envío; no afecta a otros.\n'
        '• <b>Canal ya gestionado</b>: el bot indica el otro bot y la ruta @usuario/token.\n\n'

        '## Relacionado\n'
        '[[tutorial_walkthrough|El tutorial de primer arranque]], '
        '[[admins_attach|Entrar en un canal que ya tiene bot]], '
        '[[main_bot_stand_in|Sustituto del bot principal]], [[bot_add|Añadir un bot de envío]].'
    ),
    'children': None,
    'faq': [
        {
            'q': '¿Sigue haciendo falta añadir @FastSchedulerBot al canal?',
            'a': 'No. Publicar, programar, estadísticas y ajustes van por tu bot de envío. El principal '
                 'solo necesita Publicar mensajes si quieres el sustituto opcional.',
            'links': ['main_bot_stand_in'],
        },
        {
            'q': '¿Por qué espera diez segundos?',
            'a': 'Porque Telegram entrega el aviso de «bot ascendido» a su ritmo; un segundo no '
                 'siempre basta. Diez segundos equilibran una espera silenciosa y una pantalla que '
                 'miente.',
            'links': ['admins'],
        },
        {
            'q': '¿Qué pasa tras las cinco comprobaciones?',
            'a': 'El botón sigue abriendo el selector, pero el bot deja de vigilar. Termina de añadir '
                 'el bot y pulsa Comprobar de nuevo: esa vía no tiene límite.',
            'links': ['sender_bot_setup'],
        },
        {
            'q': '¿La zona horaria cambia mis otros canales?',
            'a': 'No. Se guarda solo para ese canal; la zona por defecto de la cuenta solo se escribe '
                 'si está vacía.',
            'links': ['timezone_set'],
        },
    ],
}

CONTENT_ES['main_bot_stand_in'] = {
    'title': 'Sustituto del bot principal',
    'description': (
        'Si tu bot de envío falla, el bot principal puede mantener viva la cola durante una ventana '
        'limitada y opcional: qué lo activa, qué publica, cuánto dura y qué protege contra abusos.'
    ),
    'content': (
        'Un bot de envío puede dejar de funcionar en el peor momento: token revocado en @BotFather, '
        'expulsado del canal o sin derechos. El sustituto es la red de seguridad, y es '
        'deliberadamente estrecho.\n\n'

        '## Qué lo activa\n'
        'Solo un <b>fallo de autenticación o permisos del bot de envío</b>: token revocado o inválido, '
        'bot fuera del canal, falta de <b>Publicar mensajes</b>. Los errores de contenido, tiempos de '
        'espera, límites de tasa y restricciones del canal no lo activan, porque el bot principal '
        'chocaría con el mismo muro.\n\n'

        '## Qué ves\n'
        '1. El post se entrega <b>una vez</b> por el bot principal, para no perder un mensaje '
        'programado.\n'
        '2. Justo después el bot pregunta una vez si quieres seguir publicando desde el principal '
        'hasta N días.\n'
        '3. <b>Sí</b> activa el sustituto para ese canal; <b>No</b> registra el rechazo y no vuelve a '
        'preguntar: los fallos se informan como errores.\n\n'

        '## La ventana\n'
        'Por defecto <b>3 días</b> por activación. El operador puede cambiar el valor global y fijar '
        'una excepción por bot; el rango va de 1 hora a 30 días. Al terminar, el sustituto se detiene '
        'solo y el siguiente fallo se informa con normalidad. No se renueva automáticamente.\n\n'

        '## Quién puede activarlo\n'
        'El dueño del canal o un admin con <code>settings_change_permissions</code>. Nadie más: es una '
        'decisión de canal que cambia quién publica.\n\n'

        '## Protecciones\n'
        '• <b>Opt-in, nunca automático</b> más allá del primer rescate.\n'
        '• <b>Apagar y encender no amplía el plazo</b>: reactivar dentro del enfriamiento conserva la '
        'caducidad original.\n'
        '• <b>Un aviso por canal y ventana</b>, sin spam mientras arreglas el bot.\n'
        '• <b>Ventana acotada</b> en el servidor, nunca «para siempre».\n'
        '• <b>Auditado</b>: activación, rechazo, reversión y caducidad quedan registrados.\n'
        '• <b>Interruptor global</b> para desactivar el sustituto en todos los canales a la vez.\n\n'

        '## Terminarlo antes\n'
        'El mensaje de confirmación trae <b>⛔ Detener el sustituto ahora</b>. También desde los '
        'ajustes del canal, donde se ve el tiempo restante. Detenerlo no borra nada: la cola vuelve a '
        'fallar con aviso si el bot sigue roto.\n\n'

        '## Lo que no es\n'
        'No es un segundo programador, no publica con el nombre de tu bot (los lectores lo notan), no '
        'arregla el token ni salta los permisos del canal. Compra tiempo para arreglar el problema '
        'real.\n\n'

        '## Relacionado\n'
        '[[sender_bot_setup|Primero el bot de envío]], [[bot_permissions|Permisos del bot]], '
        '[[admins|Administradores y acceso]].'
    ),
    'children': None,
    'faq': [
        {
            'q': '¿Se notará que publicó el bot principal?',
            'a': 'Sí: el autor del mensaje es el bot que lo envía. Es el intercambio honesto: un post '
                 'de un bot que tus lectores no siguen, en lugar de ningún post.',
            'links': ['bot_sender'],
        },
        {
            'q': '¿Empieza sin que yo diga que sí?',
            'a': 'Solo el primer rescate es automático, y es lo que salva el mensaje programado. Todo '
                 'lo demás espera un sí explícito.',
            'links': ['sender_bot_setup'],
        },
        {
            'q': 'Dije que no, ¿puedo cambiar de idea?',
            'a': 'Sí, activándolo desde los ajustes del canal. El rechazo solo evita que el bot '
                 'insista solo.',
            'links': ['admins'],
        },
        {
            'q': '¿Por qué se detuvo en mitad de la avería?',
            'a': 'Terminó la ventana: es una duración fija desde que lo activaste, no una cuenta atrás '
                 'que se pausa. Arregla el bot y la cola continúa.',
            'links': ['bot_permissions'],
        },
    ],
}

CONTENT_ES['channel_connect'] = {
    'title': 'Conectar el bot',
    'description': (
        'Qué bot necesita qué permiso y cómo concederlo en Telegram: solo el bot de envío del canal '
        'publica, y el bot principal ya no necesita derechos.'
    ),
    'content': (
        'Solo un bot hace el trabajo: <b>tu bot de envío</b>. El bot principal ya no necesita ser '
        'administrador del canal.\n\n'

        '## El bot de envío (obligatorio)\n'
        'Debe ser administrador con <b>Publicar mensajes</b> para publicar de verdad. La forma fácil: '
        'abre el bot de envío y pulsa el botón verde <b>➕ Añadir bot a un canal</b>; el selector de '
        'Telegram marca los derechos y el bot recomprueba solo a los 10 segundos (5 comprobaciones '
        'automáticas al día).\n\n'

        '## Derechos recomendados\n'
        '• <b>Editar mensajes</b> — corregir un post ya publicado.\n'
        '• <b>Eliminar mensajes</b> — retirar un post al borrarlo de la cola o al limpiar.\n\n'

        '## Verificar\n'
        'Tras conceder derechos, vuelve al bot y pulsa <b>🔄 Comprobar de nuevo</b> donde lo pida. La '
        'comprobación es en vivo, sin reinicios.\n\n'
        'Si el canal pierde los derechos después, la entrega falla y el bot lo informa. Restaura el '
        'permiso y la cola continúa.\n\n'

        '## Relacionado\n'
        '[[channel_permissions|Permisos del canal]], [[bot_permissions|Permisos del bot]], '
        '[[sender_bot_setup|Primero el bot de envío]].'
    ),
    'children': None,
}

CONTENT_ES['channel_add'] = {
    'title': 'Añadir un canal',
    'description': (
        'Los pasos exactos para conectar otro canal, incluido el atajo del selector dentro de la '
        'programación.'
    ),
    'content': (
        '## Antes de empezar\n'
        'Debes ser administrador del canal y el <b>bot de envío</b> que lo servirá debe ser '
        'administrador con <b>Publicar mensajes</b>. El bot principal no necesita ningún derecho.\n\n'

        '## Conectarlo\n'
        '1. Abre <b>📢 Canales</b> → <b>📢 Conectar canal</b>. El bot lista tus bots de envío libres: '
        'elige uno y se abre con el flujo ya iniciado. También desde <b>➕ Añadir canal nuevo</b> en el '
        'selector de programación.\n'
        '2. Envía el identificador: <code>@tucanal</code>, un enlace <code>https://t.me/…</code>, una '
        'invitación, un post reenviado o el id numérico <code>-100…</code>.\n'
        '3. El bot verifica los derechos y añade el canal a tu lista.\n\n'

        '## Después de conectar\n'
        'Si elegiste un bot de envío, el canal queda vinculado y la zona horaria es el último paso. Si '
        'conectaste el canal sin bot (la vía de escape), la programación sigue bloqueada hasta que '
        'añadas uno: cada canal necesita el suyo.\n\n'

        '## Límites\n'
        'Free: {channels_free} canal; Premium: hasta {channels_prem}. Al pasarte aparece la mejora.\n\n'

        '## Si falla\n'
        '• <b>El bot no es admin</b> — pulsa el botón verde del bot de envío y marca Publicar '
        'mensajes.\n'
        '• <b>El canal ya tiene bot</b> — el bot te dice cuál y te ofrece la ruta @usuario/token si '
        'eres administrador.\n\n'

        '## Relacionado\n'
        '[[sender_bot_setup|Primero el bot de envío]], [[channel_connect|Conectar el bot]], '
        '[[admins_attach|Entrar en un canal que ya tiene bot]].'
    ),
    'children': None,
}

CONTENT_ES['connect_bot'] = {
    'title': 'Conectar un bot',
    'description': (
        'Crea el bot de envío, conecta su token, añádelo al canal con el botón verde y entiende qué '
        'pasa después.'
    ),
    'content': (
        'Un bot de envío es un bot de Telegram tuyo. Fast Scheduler usa su token para publicar, así '
        'que el autor de cada post es tu bot y no el bot compartido.\n\n'

        '## Crear el token\n'
        '1. Abre <b>@BotFather</b>.\n'
        '2. Envía <code>/newbot</code>, elige nombre visible y un usuario que acabe en <code>bot</code>.\n'
        '3. Copia el token (<code>1234567890:ABCdef…</code>). Trátalo como una contraseña.\n\n'

        '## Conectarlo\n'
        '<b>🤖 Bots</b> → <b>🔑 Tengo un token</b> → envía el token. El bot lo verifica y muestra a qué '
        'bot pertenece.\n\n'

        '## Adjuntar el canal\n'
        'Un bot = un canal. Lo más fácil: abre el bot de envío y pulsa el botón verde <b>➕ Añadir bot '
        'a un canal</b>; el selector de Telegram marca los derechos de administrador y el bot '
        'recomprueba solo a los 10 segundos (5 comprobaciones automáticas al día).\n\n'

        '## Si aún no es administrador\n'
        'Canal → Administradores → Añadir administrador → tu bot → <b>Publicar mensajes</b>. Vuelve al '
        'bot y pulsa <b>🔄 Comprobar de nuevo</b>. El bot principal no hay que añadirlo.\n\n'

        '## Qué se mueve al bot de envío\n'
        'Programación, recurrentes, lista de mensajes, estadísticas, clasificación, copias de '
        'seguridad y gestión de admins. El bot principal queda como centro de soporte, avisos y '
        'recuperación.\n\n'

        '## Relacionado\n'
        '[[bot_add|Añadir un bot de envío]], [[bot_permissions|Permisos del bot]], '
        '[[sender_bot_setup|Primero el bot de envío]].'
    ),
    'children': None,
}

CONTENT_ES['channel_permissions'] = {
    'title': 'Permisos del canal',
    'description': (
        'Los derechos de administrador que usa el bot, qué desbloquea cada uno y el error exacto '
        'cuando falta uno.'
    ),
    'content': (
        'Solo tu <b>bot de envío</b> necesita derechos de administrador normales; el bot principal no '
        'necesita ninguno. Fast Scheduler nunca pide tu contraseña de Telegram ni un código de '
        'acceso.\n\n'

        '## Obligatorio\n'
        '<b>Publicar mensajes</b>: sin esto cada envío falla con un error de «el bot no es admin» y el '
        'bot se niega a desbloquear la programación del canal.\n\n'

        '## Recomendado\n'
        '• <b>Editar mensajes</b> — corregir un post ya publicado.\n'
        '• <b>Eliminar mensajes</b> — retirar un post al borrarlo de la cola.\n\n'

        '## Cómo concederlos\n'
        'Lo más rápido: el botón verde <b>➕ Añadir bot a un canal</b> dentro del bot de envío. A mano: '
        'Ajustes del canal → Administradores → Añadir → tu bot → marcar los derechos.\n\n'

        '## Comprobar\n'
        'Pulsa <b>🔄 Comprobar de nuevo</b> en el bot. La comprobación es en vivo y no requiere '
        'reiniciar nada.\n\n'

        '## Relacionado\n'
        '[[bot_permissions|Permisos del bot]], [[channel_connect|Conectar el bot]].'
    ),
    'children': None,
}

CONTENT_ES['onboarding_step1'] = {
    'title': 'Tutorial paso 1: conecta tu bot de envío',
    'description': (
        'La primera pantalla del tutorial pide solo una cosa: tu propio bot de envío. Qué hace cada '
        'botón, cómo es un token y cómo se ve el éxito.'
    ),
    'content': (
        'El tutorial empieza por el bot que va a publicar, no por un enlace de canal. No necesitas '
        'canal todavía ni hacer administrador a @FastSchedulerBot en ninguna parte.\n\n'

        '## La pantalla\n'
        '• <b>➕ Crear bot</b> — abre @BotFather con nombre y usuario preparados. Confirma, copia el '
        'token y vuelve.\n'
        '• <b>🔑 Tengo un token</b> — pega uno que ya tengas.\n'
        '• <b>⏭ Saltar tutorial</b> — pide confirmación y termina. Puedes conectar el bot luego desde '
        '<b>🤖 Bots</b>.\n\n'

        '## Cómo es un token\n'
        '<code>1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ</code>: una línea, número, dos puntos y letras. Si '
        'dice que no es válido, la copia se cortó: vuelve a copiar la línea entera.\n\n'

        '## Cómo se ve el éxito\n'
        'El bot verifica el token y responde <b>Token guardado para @tu_bot</b> con un botón verde '
        '<b>Abrir @tu_bot</b>. Púlsalo: el canal y la zona horaria se conectan ahí, dentro del bot de '
        'envío. El tutorial del bot principal termina en ese punto.\n\n'

        '## Si falla\n'
        '• <b>Token inválido</b> — copia cortada o token ya revocado.\n'
        '• <b>Ese es el token del bot principal</b> — crea tu propio bot.\n'
        '• <b>Límite alcanzado</b> — Free permite {bots_free} bot de envío; ver '
        '[[limit_bots|Límite de bots]].\n'
        '• <b>No pasa nada</b> — asegúrate de escribir en el chat privado del bot, no en un grupo.\n\n'

        '## Relacionado\n'
        '[[sender_bot_setup|Primero el bot de envío]], [[bot_add|Añadir un bot de envío]], '
        '[[onboarding_step2|Tutorial paso 2: canal y zona horaria]].'
    ),
    'children': None,
}

CONTENT_ES['onboarding_step2'] = {
    'title': 'Tutorial paso 2: canal y zona horaria (en el bot de envío)',
    'description': (
        'El resto ocurre dentro de tu bot de envío: añádelo al canal, deja que termine la comprobación '
        'de 10 segundos y fija la zona solo para ese canal.'
    ),
    'content': (
        'Con el bot de envío conectado, ábrelo con el botón verde. Muestra la pantalla «Estoy en '
        'marcha» porque aún no tiene canal.\n\n'

        '## Conectar el canal\n'
        '1. Pulsa la fila verde <b>➕ Añadir bot a un canal</b>.\n'
        '2. Telegram abre su selector con el bot marcado como administrador y <b>Publicar mensajes</b> '
        'activado. Elige el canal y confirma.\n'
        '3. El bot recomprueba solo a los <b>10 segundos</b> (5 comprobaciones automáticas al día) y '
        'continúa.\n'
        'Reenviar un post, enviar <code>@usuario</code> o añadirlo desde un canal privado también '
        'vale.\n\n'

        '## Fijar la zona\n'
        'La confirmación pide la zona: ciudad (<code>Madrid</code>), hora actual '
        '(<code>15:30</code>), ubicación o lista. Se guarda para <b>este canal</b>; los demás '
        'conservan la suya y la zona por defecto solo se rellena si estaba vacía.\n\n'

        '## Listo\n'
        'La última pantalla es <b>Todo listo — la zona de tu ciudad</b> con un botón al panel. Desde ahí viven '
        'programación, estadísticas, copias y admins.\n\n'

        '## Relacionado\n'
        '[[onboarding_step1|Tutorial paso 1]], [[sender_bot_setup|Primero el bot de envío]], '
        '[[timezone_set|Fijar la zona horaria]].'
    ),
    'children': None,
}

CONTENT_ES['onboarding_step3'] = {
    'title': 'Después del tutorial: tu panel del bot de envío',
    'description': (
        'El tutorial termina al conectar el bot de envío. Este es el panel al que llegas, qué hace '
        'cada fila y dónde fue el contenido del antiguo paso 3.'
    ),
    'content': (
        'El tutorial ahora son dos pasos: bot de envío y, dentro de él, canal y zona horaria. No hay '
        'un tercer paso que buscar.\n\n'

        '## A dónde llegas\n'
        'Tras guardar la zona, el bot de envío muestra el panel: <b>📅 Programar</b>, '
        '<b>🔁 Recurrentes</b>, <b>📋 Mensajes</b>, <b>📊 Estadísticas</b>, <b>⚙️ Ajustes</b> (admins, '
        'copias, ocultar canal) e <b>🌐 Idioma</b>. Las filas desaparecen si falta el permiso, así que '
        'un coadmin ve un menú más corto y honesto.\n\n'

        '## Dónde fue el antiguo paso 3\n'
        'Aquel paso pedía ascender el bot en el canal y pulsar Comprobar. Ahora forma parte del botón '
        '<b>Añadir bot a un canal</b>: el selector concede los derechos y la comprobación automática de '
        '10 segundos sustituye la verificación manual. Si lo añadiste a mano, sigue estando '
        '<b>🔄 Comprobar de nuevo</b>.\n\n'

        '## Añadir personas\n'
        'Ajustes → <b>👥 Admins</b>. Lee [[admins|Administradores y acceso]] antes de dar permisos de '
        'borrado o exportación: los valores por defecto son conservadores.\n\n'

        '## Relacionado\n'
        '[[sender_bot_setup|Primero el bot de envío]], [[admins|Administradores y acceso]], '
        '[[start_schedule|Programa tu primer post]].'
    ),
    'children': None,
}

CONTENT_ES['gs_step1'] = {
    'title': 'Paso 1: conecta tu bot de envío',
    'description': (
        'Empieza por el bot que publica. Créalo en @BotFather o pega un token existente y ábrelo con '
        'el botón verde que aparece.'
    ),
    'content': (
        'Cada canal lo sirve su propio bot de envío: un bot de Telegram tuyo que publica con su '
        'nombre. Por eso la configuración empieza por él.\n\n'

        '## Por qué tu propio bot\n'
        '• Los posts salen con el nombre y la foto de <b>tu bot</b>.\n'
        '• Sin cola compartida: no esperas detrás de otros canales.\n'
        '• Estadísticas, clasificación, copias y admins viven en ese bot.\n'
        '• Los botones inline funcionan a través de tu bot.\n\n'

        '## Hazlo\n'
        '1. <b>🤖 Bots</b> → <b>🔑 Tengo un token</b>, o <b>➕ Crear bot</b> para pasar por @BotFather.\n'
        '2. Envía el token en un mensaje. El bot llama a Telegram, lo verifica y muestra el usuario.\n'
        '3. Pulsa el botón verde <b>Abrir @tu_bot</b>: el canal y la zona se conectan dentro.\n\n'

        '## Siguiente\n'
        '[[gs_step2|Paso 2: conecta el canal y fija la zona horaria]].'
    ),
    'children': None,
}

CONTENT_ES['gs_step2'] = {
    'title': 'Paso 2: conecta el canal y fija la zona horaria',
    'description': (
        'Dentro del bot de envío: añádelo al canal con el botón verde, deja correr la comprobación '
        'automática y fija la zona de ese canal.'
    ),
    'content': (
        'Abre el bot de envío. Como aún no tiene canal, muestra la pantalla «Estoy en marcha» y no un '
        'panel.\n\n'

        '## Añadirlo al canal\n'
        '• Botón verde <b>➕ Añadir bot a un canal</b>: el selector de Telegram abre con el bot marcado '
        'como administrador y <b>Publicar mensajes</b> activado.\n'
        '• O reenvía un post del canal, o envía su <code>@usuario</code> / enlace <code>t.me</code>.\n'
        '• Canal privado: añade el bot desde los ajustes del propio canal; lo detecta solo.\n\n'

        '## La comprobación automática\n'
        'Tras el botón, el bot recomprueba una vez a los <b>10 segundos</b> y continúa solo. El límite '
        'es de <b>5 al día</b>; después usa <b>🔄 Comprobar de nuevo</b>, que no tiene límite.\n\n'

        '## La zona horaria\n'
        'Una ciudad, tu hora actual, una ubicación o la lista. Se guarda solo para este canal; los '
        'demás conservan la suya y la de la cuenta solo se escribe si está vacía.\n\n'

        '## Siguiente\n'
        '[[gs_step3|Paso 3: programa un mensaje]].'
    ),
    'children': None,
}

CONTENT_ES['tutorial_walkthrough'] = {
    'title': 'El tutorial de primer arranque',
    'description': (
        'Qué pide cada pantalla del tutorial, qué botón pulsar, cómo se ve el éxito y qué hacer cuando '
        'un paso se resiste.'
    ),
    'content': (
        'El tutorial es el camino más corto entre un chat vacío y un canal funcionando. Se ejecuta una '
        'vez tras <code>/start</code> y tiene dos pantallas: <b>conectar tu bot de envío</b> y '
        '<b>abrirlo</b>. El canal y la zona horaria se configuran dentro del bot de envío.\n\n'

        '## Antes de la primera pantalla\n'
        'Ten esto listo y todo tarda unos dos minutos:\n'
        '• Eres <b>administrador</b> del canal (Telegram debe listarte como admin, no basta con ser el '
        'dueño nominal). No hace falta añadir @FastSchedulerBot a ninguna parte.\n'
        '• Puedes abrir @BotFather en otro chat, porque ahí se crea el bot.\n\n'

        '## Pantalla 0 — Bienvenida\n'
        'El bot explica qué hace y ofrece <b>Empezar</b>, <b>Ayuda</b> y <b>Saltar tutorial</b> (con '
        'confirmación).\n\n'

        '## Pantalla 1 — Bot de envío\n'
        'Crea el bot o pega su token. Al verificarlo aparece <b>Abrir @tu_bot</b> en verde; el tutorial '
        'del bot principal termina ahí.\n\n'

        '## Dentro del bot de envío\n'
        '<b>➕ Añadir bot a un canal</b> → elegir canal (Publicar mensajes ya marcado) → esperar 10 '
        'segundos → zona horaria del canal → panel.\n\n'

        '## Si algo falla\n'
        '• Token inválido: copia la línea completa.\n'
        '• «Aún no es administrador»: usa el botón verde y marca Publicar mensajes.\n'
        '• Comprobación automática en pausa: pulsa Comprobar de nuevo.\n'
        '• El canal ya tiene bot: envía su @usuario o token si eres admin.\n\n'

        '## Relacionado\n'
        '[[sender_bot_setup|Primero el bot de envío]], [[admins_attach|Entrar en un canal que ya tiene '
        'bot]], [[main_bot_stand_in|Sustituto del bot principal]].'
    ),
    'children': None,
}
