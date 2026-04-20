"""Мультиязычность — русский, узбекский, английский
Использование: from bot.i18n import t
  t("start.welcome", lang="en", name="John")
"""

from bot.emojis import E

TRANSLATIONS = {
    # === /start ===
    "start.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет, {{name}}!</b>\n\n"
            f"{E['video']} Я помогу тебе обрезать видео быстро и просто.\n\n"
            f"{E['pin']} <b>Как пользоваться:</b>\n"
            "Отправь мне видеофайл — я помогу выбрать начало и конец обрезки. "
            f"{E['plane']}\n\n"
            "Выбери действие ниже:"
        ),
        "uz": (
            f"{E['bot']} <b>Salom, {{name}}!</b>\n\n"
            f"{E['video']} Video fayllarni tez va oson qisqartirishda yordam beraman.\n\n"
            f"{E['pin']} <b>Qanday foydalanish:</b>\n"
            "Menga video fayl yuboring — men boshlanish va tugash vaqtini tanlashga yordam beraman. "
            f"{E['plane']}\n\n"
            "Quyidagi tugmalardan birini tanlang:"
        ),
        "en": (
            f"{E['bot']} <b>Hello, {{name}}!</b>\n\n"
            f"{E['video']} I'll help you trim video files quickly and easily.\n\n"
            f"{E['pin']} <b>How to use:</b>\n"
            "Send me a video file — I'll help you select the start and end of the trim. "
            f"{E['plane']}\n\n"
            "Choose an action below:"
        ),
    },

    # === Кнопки главного меню ===
    "btn.trim": {
        "ru": "Обрезать видео",
        "uz": "Videoni qisqartirish",
        "en": "Trim video",
    },
    "btn.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "btn.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "btn.back": {
        "ru": "Назад",
        "uz": "Orqaga",
        "en": "Back",
    },
    "btn.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },

    # === Обрезка видео (FSM-флоу) ===
    "trim.send_video": {
        "ru": (
            f"{E['video']} <b>Пришли видео для обрезки.</b>\n\n"
            f"{E['info']} Поддерживаются файлы до 2 ГБ.\n"
            f"{E['pin']} Формат тайм-кодов: <code>1:23:45</code>, <code>5:30</code>, <code>90</code>.\n\n"
            f"Для отмены — /cancel"
        ),
        "uz": (
            f"{E['video']} <b>Qisqartirish uchun video yuboring.</b>\n\n"
            f"{E['info']} 2 GB gacha fayllar qo'llab-quvvatlanadi.\n"
            f"{E['pin']} Vaqt format: <code>1:23:45</code>, <code>5:30</code>, <code>90</code>.\n\n"
            f"Bekor qilish uchun — /cancel"
        ),
        "en": (
            f"{E['video']} <b>Send a video to trim.</b>\n\n"
            f"{E['info']} Files up to 2 GB are supported.\n"
            f"{E['pin']} Timecode format: <code>1:23:45</code>, <code>5:30</code>, <code>90</code>.\n\n"
            f"To cancel — /cancel"
        ),
    },
    "trim.video_received": {
        "ru": (
            f"{E['check']} <b>Видео получено.</b>\n\n"
            f"{E['clock']} Длительность: <b>{{duration}}</b>\n"
            f"{E['package']} Размер: <b>{{size}}</b>\n\n"
            f"{E['edit']} Укажи <b>тайм-код начала</b> (например <code>0:30</code>):"
        ),
        "uz": (
            f"{E['check']} <b>Video qabul qilindi.</b>\n\n"
            f"{E['clock']} Davomiyligi: <b>{{duration}}</b>\n"
            f"{E['package']} Hajmi: <b>{{size}}</b>\n\n"
            f"{E['edit']} <b>Boshlanish vaqtini</b> kiriting (masalan <code>0:30</code>):"
        ),
        "en": (
            f"{E['check']} <b>Video received.</b>\n\n"
            f"{E['clock']} Duration: <b>{{duration}}</b>\n"
            f"{E['package']} Size: <b>{{size}}</b>\n\n"
            f"{E['edit']} Send the <b>start timecode</b> (e.g. <code>0:30</code>):"
        ),
    },
    "trim.send_end": {
        "ru": (
            f"{E['check']} Начало: <code>{{start}}</code>\n\n"
            f"{E['edit']} Теперь укажи <b>тайм-код конца</b>:"
        ),
        "uz": (
            f"{E['check']} Boshlanish: <code>{{start}}</code>\n\n"
            f"{E['edit']} Endi <b>tugash vaqtini</b> kiriting:"
        ),
        "en": (
            f"{E['check']} Start: <code>{{start}}</code>\n\n"
            f"{E['edit']} Now send the <b>end timecode</b>:"
        ),
    },
    "trim.choose_mode": {
        "ru": (
            f"{E['check']} Обрезка с <code>{{start}}</code> до <code>{{end}}</code>\n\n"
            f"{E['gear']} Выбери режим:\n"
            f"{E['lightning']} <b>Быстрый</b> — без перекодирования, границы по ключевым кадрам\n"
            f"{E['star']} <b>Точный</b> — с перекодированием, точно до секунды (медленнее)"
        ),
        "uz": (
            f"{E['check']} Qisqartirish <code>{{start}}</code> — <code>{{end}}</code>\n\n"
            f"{E['gear']} Rejimni tanlang:\n"
            f"{E['lightning']} <b>Tez</b> — qayta kodlashsiz, kalit kadrlar bo'yicha\n"
            f"{E['star']} <b>Aniq</b> — qayta kodlash bilan, soniyagacha aniq (sekinroq)"
        ),
        "en": (
            f"{E['check']} Trim <code>{{start}}</code> — <code>{{end}}</code>\n\n"
            f"{E['gear']} Choose mode:\n"
            f"{E['lightning']} <b>Fast</b> — no re-encoding, by keyframes\n"
            f"{E['star']} <b>Precise</b> — re-encode, accurate to the second (slower)"
        ),
    },
    "trim.mode_fast": {
        "ru": "Быстрый",
        "uz": "Tez",
        "en": "Fast",
    },
    "trim.mode_precise": {
        "ru": "Точный",
        "uz": "Aniq",
        "en": "Precise",
    },
    "trim.processing": {
        "ru": f"{E['clock']} <b>Обрабатываю...</b>\n\nМожет занять до пары минут.",
        "uz": f"{E['clock']} <b>Qayta ishlamoqda...</b>\n\nBir necha daqiqa davom etishi mumkin.",
        "en": f"{E['clock']} <b>Processing...</b>\n\nThis may take a couple of minutes.",
    },
    "trim.done": {
        "ru": f"{E['check']} <b>Готово!</b> Держи обрезанный фрагмент.",
        "uz": f"{E['check']} <b>Tayyor!</b> Mana qisqartirilgan parcha.",
        "en": f"{E['check']} <b>Done!</b> Here is the trimmed fragment.",
    },
    "trim.error_timecode": {
        "ru": (
            f"{E['cross']} <b>Неверный формат тайм-кода.</b>\n\n"
            f"{E['pin']} Примеры: <code>1:23:45</code>, <code>5:30</code>, <code>90</code>\n\n"
            "Попробуй ещё раз:"
        ),
        "uz": (
            f"{E['cross']} <b>Vaqt formati noto'g'ri.</b>\n\n"
            f"{E['pin']} Masalan: <code>1:23:45</code>, <code>5:30</code>, <code>90</code>\n\n"
            "Qayta urinib ko'ring:"
        ),
        "en": (
            f"{E['cross']} <b>Invalid timecode format.</b>\n\n"
            f"{E['pin']} Examples: <code>1:23:45</code>, <code>5:30</code>, <code>90</code>\n\n"
            "Try again:"
        ),
    },
    "trim.error_end_before_start": {
        "ru": f"{E['cross']} Конец должен быть <b>позже начала</b>. Попробуй ещё раз:",
        "uz": f"{E['cross']} Tugash vaqti <b>boshlanishdan keyin</b> bo'lishi kerak. Qayta urinib ko'ring:",
        "en": f"{E['cross']} End must be <b>after start</b>. Try again:",
    },
    "trim.error_out_of_bounds": {
        "ru": (
            f"{E['cross']} Значение выходит за пределы видео "
            f"(длительность <b>{{duration}}</b>). Попробуй ещё раз:"
        ),
        "uz": (
            f"{E['cross']} Qiymat video davomiyligidan oshib ketdi "
            f"(davomiyligi <b>{{duration}}</b>). Qayta urinib ko'ring:"
        ),
        "en": (
            f"{E['cross']} Value exceeds the video duration "
            f"(<b>{{duration}}</b>). Try again:"
        ),
    },
    "trim.error_too_big": {
        "ru": (
            f"{E['package']} <b>Фрагмент слишком большой</b> (> 1.9 ГБ).\n\n"
            "Сократи интервал обрезки."
        ),
        "uz": (
            f"{E['package']} <b>Parcha juda katta</b> (> 1.9 GB).\n\n"
            "Qisqartirish oralig'ini kamaytiring."
        ),
        "en": (
            f"{E['package']} <b>Fragment too big</b> (> 1.9 GB).\n\n"
            "Shorten the trim interval."
        ),
    },
    "trim.error_ffmpeg": {
        "ru": f"{E['cross']} <b>Не удалось обработать видео.</b>\n\nПопробуй другой файл или режим.",
        "uz": f"{E['cross']} <b>Videoni qayta ishlashning imkoni bo'lmadi.</b>\n\nBoshqa fayl yoki rejimni sinab ko'ring.",
        "en": f"{E['cross']} <b>Failed to process the video.</b>\n\nTry another file or mode.",
    },
    "trim.error_not_video": {
        "ru": f"{E['cross']} Пришли <b>видео</b> или видео-файл.",
        "uz": f"{E['cross']} <b>Video</b> yoki video faylni yuboring.",
        "en": f"{E['cross']} Please send a <b>video</b> or a video file.",
    },
    "trim.error_download": {
        "ru": f"{E['cross']} <b>Не удалось скачать файл.</b>\n\nПопробуй ещё раз.",
        "uz": f"{E['cross']} <b>Faylni yuklab olishning imkoni bo'lmadi.</b>\n\nQayta urinib ko'ring.",
        "en": f"{E['cross']} <b>Failed to download the file.</b>\n\nTry again.",
    },
    "trim.busy": {
        "ru": f"{E['clock']} Дождись окончания текущей обработки.",
        "uz": f"{E['clock']} Joriy qayta ishlash tugashini kuting.",
        "en": f"{E['clock']} Please wait until the current processing finishes.",
    },
    "trim.cancelled": {
        "ru": f"{E['check']} Отменено. Пришли новое видео когда будет удобно.",
        "uz": f"{E['check']} Bekor qilindi. Qulay bo'lganda yangi video yuboring.",
        "en": f"{E['check']} Cancelled. Send a new video whenever ready.",
    },
    "trim.cancel": {
        "ru": "Отмена",
        "uz": "Bekor qilish",
        "en": "Cancel",
    },

    # === Профиль ===
    "profile.title": {
        "ru": (
            f"{E['profile']} <b>Твой профиль</b>\n\n"
            f"{E['edit']} Имя: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['video']} Обрезок сделано: {{downloads}}\n"
        ),
        "uz": (
            f"{E['profile']} <b>Profiling</b>\n\n"
            f"{E['edit']} Ism: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['video']} Qisqartirishlar soni: {{downloads}}\n"
        ),
        "en": (
            f"{E['profile']} <b>Your profile</b>\n\n"
            f"{E['edit']} Name: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['video']} Trims done: {{downloads}}\n"
        ),
    },

    # === Помощь ===
    "help.text": {
        "ru": (
            f"{E['book']} <b>Помощь</b>\n\n"
            f"{E['star']} Отправь видеофайл — бот предложит обрезать его\n"
            f"{E['star']} Укажи начало и конец в формате MM:SS или HH:MM:SS\n"
            f"{E['star']} Поддерживаются файлы до 2 ГБ\n"
            f"{E['lock']} Файл обрабатывается на сервере через ffmpeg\n\n"
            f"{E['plane']} По вопросам: @{{admin_username}}"
        ),
        "uz": (
            f"{E['book']} <b>Yordam</b>\n\n"
            f"{E['star']} Video fayl yuboring — bot uni qisqartirishni taklif qiladi\n"
            f"{E['star']} Boshlanish va tugashni MM:SS yoki HH:MM:SS formatida kiriting\n"
            f"{E['star']} 2 GB gacha fayllar qo'llab-quvvatlanadi\n"
            f"{E['lock']} Fayl serverda ffmpeg orqali qayta ishlanadi\n\n"
            f"{E['plane']} Savollar uchun: @{{admin_username}}"
        ),
        "en": (
            f"{E['book']} <b>Help</b>\n\n"
            f"{E['star']} Send a video file — the bot will offer to trim it\n"
            f"{E['star']} Specify start and end in MM:SS or HH:MM:SS format\n"
            f"{E['star']} Files up to 2 GB are supported\n"
            f"{E['lock']} File is processed on the server via ffmpeg\n\n"
            f"{E['plane']} Contact: @{{admin_username}}"
        ),
    },

    # === Подписка ===
    "sub.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет!</b>\n\n"
            f"{E['video']} Этот бот обрезает видеофайлы — быстро и бесплатно!\n\n"
            f"{E['lock']} <b>Для начала подпишись на каналы ниже:</b>\n\n"
            f"После подписки нажми «{E['check']} Проверить подписку»"
        ),
        "uz": (
            f"{E['bot']} <b>Salom!</b>\n\n"
            f"{E['video']} Bu bot video fayllarni qisqartiradi — tez va bepul!\n\n"
            f"{E['lock']} <b>Boshlash uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
            f"Obuna bo'lgandan keyin «{E['check']} Obunani tekshirish» tugmasini bosing"
        ),
        "en": (
            f"{E['bot']} <b>Hello!</b>\n\n"
            f"{E['video']} This bot trims video files — fast and free!\n\n"
            f"{E['lock']} <b>To start, subscribe to the channels below:</b>\n\n"
            f"After subscribing, tap «{E['check']} Check subscription»"
        ),
    },
    "sub.not_subscribed": {
        "ru": (
            f"{E['cross']} <b>Ты ещё не подписался на все каналы:</b>\n\n"
            f"Подпишись и нажми «{E['check']} Проверить подписку» ещё раз."
        ),
        "uz": (
            f"{E['cross']} <b>Hali barcha kanallarga obuna bo'lmading:</b>\n\n"
            f"Obuna bo'l va «{E['check']} Obunani tekshirish» tugmasini qayta bos."
        ),
        "en": (
            f"{E['cross']} <b>You haven't subscribed to all channels yet:</b>\n\n"
            f"Subscribe and tap «{E['check']} Check subscription» again."
        ),
    },
    "sub.success": {
        "ru": (
            f"{E['check']} <b>Отлично, {{name}}!</b>\n\n"
            f"Теперь ты можешь пользоваться ботом! {E['plane']}\n\n"
            "Отправь видеофайл для обрезки."
        ),
        "uz": (
            f"{E['check']} <b>Zo'r, {{name}}!</b>\n\n"
            f"Endi botdan foydalanishingiz mumkin! {E['plane']}\n\n"
            "Qisqartirish uchun video fayl yuboring."
        ),
        "en": (
            f"{E['check']} <b>Great, {{name}}!</b>\n\n"
            f"You can now use the bot! {E['plane']}\n\n"
            "Send a video file to trim."
        ),
    },
    "btn.check_sub": {
        "ru": "Проверить подписку",
        "uz": "Obunani tekshirish",
        "en": "Check subscription",
    },
    "sub.check_alert_fail": {
        "ru": f"{E['cross']} Подпишись на все каналы!",
        "uz": f"{E['cross']} Barcha kanallarga obuna bo'ling!",
        "en": f"{E['cross']} Subscribe to all channels!",
    },
    "sub.check_alert_ok": {
        "ru": f"{E['check']} Подписка подтверждена!",
        "uz": f"{E['check']} Obuna tasdiqlandi!",
        "en": f"{E['check']} Subscription confirmed!",
    },
    "sub.not_required": {
        "ru": f"{E['check']} Подписка не требуется!",
        "uz": f"{E['check']} Obuna talab qilinmaydi!",
        "en": f"{E['check']} No subscription required!",
    },

    # === Ошибки ===
    "error.too_large": {
        "ru": f"{E['package']} <b>Файл слишком большой</b>\n\nTelegram ограничивает размер файла до 2 ГБ.",
        "uz": f"{E['package']} <b>Fayl juda katta</b>\n\nTelegram fayl hajmini 2 GB bilan cheklaydi.",
        "en": f"{E['package']} <b>File too large</b>\n\nTelegram limits file size to 2 GB.",
    },
    "error.timeout": {
        "ru": f"{E['clock']} <b>Превышено время ожидания</b>\n\nПопробуй ещё раз через пару минут.",
        "uz": f"{E['clock']} <b>Kutish vaqti tugadi</b>\n\nBir necha daqiqadan keyin qayta urinib ko'ring.",
        "en": f"{E['clock']} <b>Request timed out</b>\n\nPlease try again in a few minutes.",
    },
    "error.generic": {
        "ru": f"{E['cross']} <b>Что-то пошло не так</b>\n\nПопробуй позже.",
        "uz": f"{E['cross']} <b>Nimadir noto'g'ri ketdi</b>\n\nKeyinroq urinib ko'ring.",
        "en": f"{E['cross']} <b>Something went wrong</b>\n\nTry again later.",
    },
    "error.rate_limit": {
        "ru": f"{E['clock']} <b>Слишком много запросов!</b>\n\nПодожди {{seconds}} секунд и попробуй снова.",
        "uz": f"{E['clock']} <b>Juda ko'p so'rovlar!</b>\n\n{{seconds}} soniya kuting va qayta urinib ko'ring.",
        "en": f"{E['clock']} <b>Too many requests!</b>\n\nWait {{seconds}} seconds and try again.",
    },

    # === Выбор языка ===
    "lang.choose": {
        "ru": f"{E['gear']} <b>Выберите язык:</b>",
        "uz": f"{E['gear']} <b>Tilni tanlang:</b>",
        "en": f"{E['gear']} <b>Choose language:</b>",
    },
    "lang.changed": {
        "ru": f"{E['check']} Язык изменён на русский",
        "uz": f"{E['check']} Til o'zbek tiliga o'zgartirildi",
        "en": f"{E['check']} Language changed to English",
    },

    # === Админ-панель ===
    "admin.title": {
        "ru": f"{E['gear']} <b>Админ-панель</b>\n\nВыбери действие:",
        "uz": f"{E['gear']} <b>Admin panel</b>\n\nAmalni tanlang:",
        "en": f"{E['gear']} <b>Admin panel</b>\n\nChoose an action:",
    },
    "admin.no_access": {
        "ru": f"{E['ban']} Нет доступа",
        "uz": f"{E['ban']} Ruxsat yo'q",
        "en": f"{E['ban']} No access",
    },
    "admin.channel_deleted": {
        "ru": f"{E['check']} Канал удалён!",
        "uz": f"{E['check']} Kanal o'chirildi!",
        "en": f"{E['check']} Channel deleted!",
    },
    "admin.channel_not_found": {
        "ru": f"{E['cross']} Канал не найден",
        "uz": f"{E['cross']} Kanal topilmadi",
        "en": f"{E['cross']} Channel not found",
    },
    "admin.stats": {
        "ru": (
            f"{E['chart']} <b>Статистика бота</b>\n\n"
            f"{E['users']} Всего юзеров: <b>{{total_users}}</b>\n"
            f"{E['star']} Новых юзеров сегодня: <b>{{today_users}}</b>\n"
            f"{E['video']} Всего обрезок: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Каналов: <b>{{total_channels}}</b>"
        ),
        "uz": (
            f"{E['chart']} <b>Bot statistikasi</b>\n\n"
            f"{E['users']} Jami foydalanuvchilar: <b>{{total_users}}</b>\n"
            f"{E['star']} Bugungi yangi foydalanuvchilar: <b>{{today_users}}</b>\n"
            f"{E['video']} Jami qisqartirishlar: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Kanallar: <b>{{total_channels}}</b>"
        ),
        "en": (
            f"{E['chart']} <b>Bot statistics</b>\n\n"
            f"{E['users']} Total users: <b>{{total_users}}</b>\n"
            f"{E['star']} New users today: <b>{{today_users}}</b>\n"
            f"{E['video']} Total trims: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Channels: <b>{{total_channels}}</b>"
        ),
    },
    "admin.channels_empty": {
        "ru": f"{E['megaphone']} <b>Каналы</b>\n\nСписок пуст. Добавь канал кнопкой ниже.",
        "uz": f"{E['megaphone']} <b>Kanallar</b>\n\nRo'yxat bo'sh. Quyidagi tugma orqali kanal qo'shing.",
        "en": f"{E['megaphone']} <b>Channels</b>\n\nList is empty. Add a channel using the button below.",
    },
    "admin.channels_title": {
        "ru": f"{E['megaphone']} <b>Каналы для подписки:</b>\n",
        "uz": f"{E['megaphone']} <b>Obuna kanallari:</b>\n",
        "en": f"{E['megaphone']} <b>Subscription channels:</b>\n",
    },
    "admin.add_channel_id": {
        "ru": (
            f"{E['megaphone']} <b>Добавление канала</b>\n\n"
            "Отправь <b>ID канала</b> (например <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Узнать ID: добавь бота @getmyid_bot в канал"
        ),
        "uz": (
            f"{E['megaphone']} <b>Kanal qo'shish</b>\n\n"
            "<b>Kanal ID</b> raqamini yuboring (masalan <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} ID bilish: @getmyid_bot ni kanalga qo'shing"
        ),
        "en": (
            f"{E['megaphone']} <b>Add channel</b>\n\n"
            "Send the <b>channel ID</b> (e.g. <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Get ID: add @getmyid_bot to the channel"
        ),
    },
    "admin.add_channel_title": {
        "ru": f"{E['edit']} Теперь отправь <b>название канала</b>:",
        "uz": f"{E['edit']} Endi <b>kanal nomini</b> yuboring:",
        "en": f"{E['edit']} Now send the <b>channel name</b>:",
    },
    "admin.add_channel_link": {
        "ru": (
            f"{E['link']} Теперь отправь <b>ссылку или юзернейм канала</b>\n\n"
            "Принимаю любой формат:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "uz": (
            f"{E['link']} Endi <b>kanal havolasi yoki username</b> yuboring\n\n"
            "Istalgan formatda:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "en": (
            f"{E['link']} Now send the <b>channel link or username</b>\n\n"
            "Any format accepted:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
    },
    "admin.channel_added": {
        "ru": f"{E['check']} <b>Канал добавлен!</b>",
        "uz": f"{E['check']} <b>Kanal qo'shildi!</b>",
        "en": f"{E['check']} <b>Channel added!</b>",
    },
    "admin.confirm_delete": {
        "ru": f"{E['warning']} <b>Удалить канал?</b>\n\nID: <code>{{channel_id}}</code>\n\nЭто действие нельзя отменить.",
        "uz": f"{E['warning']} <b>Kanalni o'chirishni xohlaysizmi?</b>\n\nID: <code>{{channel_id}}</code>\n\nBu amalni qaytarib bo'lmaydi.",
        "en": f"{E['warning']} <b>Delete channel?</b>\n\nID: <code>{{channel_id}}</code>\n\nThis action cannot be undone.",
    },
    "admin.id_not_number": {
        "ru": f"{E['cross']} ID должен быть числом. Попробуй ещё раз:",
        "uz": f"{E['cross']} ID raqam bo'lishi kerak. Qayta urinib ko'ring:",
        "en": f"{E['cross']} ID must be a number. Try again:",
    },
    "admin.title_too_long": {
        "ru": f"{E['cross']} Название слишком длинное (макс 200 символов)",
        "uz": f"{E['cross']} Nom juda uzun (maks 200 belgi)",
        "en": f"{E['cross']} Name is too long (max 200 characters)",
    },
    "admin.link_invalid": {
        "ru": f"{E['cross']} Не удалось распознать ссылку.\nПопробуй ещё:",
        "uz": f"{E['cross']} Havolani aniqlab bo'lmadi.\nQayta urinib ko'ring:",
        "en": f"{E['cross']} Could not parse the link.\nTry again:",
    },

    # === Кнопки админки ===
    "btn.admin_stats": {"ru": "Статистика", "uz": "Statistika", "en": "Statistics"},
    "btn.admin_channels": {"ru": "Каналы", "uz": "Kanallar", "en": "Channels"},
    "btn.admin_home": {"ru": "Главное меню", "uz": "Bosh menyu", "en": "Main menu"},
    "btn.admin_add": {"ru": "Добавить канал", "uz": "Kanal qo'shish", "en": "Add channel"},
    "btn.admin_back": {"ru": "Назад", "uz": "Orqaga", "en": "Back"},
    "btn.admin_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_confirm_del": {"ru": "Да, удалить", "uz": "Ha, o'chirish", "en": "Yes, delete"},
    "btn.admin_cancel_del": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_panel": {"ru": "Админ-панель", "uz": "Admin panel", "en": "Admin panel"},
    "btn.admin_broadcast": {"ru": "Рассылка", "uz": "Xabar yuborish", "en": "Broadcast"},

    # === Рассылка ===
    "admin.broadcast_prompt": {
        "ru": f"{E['plane']} <b>Массовая рассылка</b>\n\nОтправь текст/фото/видео для рассылки.\nПоддерживается HTML.",
        "uz": f"{E['plane']} <b>Ommaviy xabar</b>\n\nYuborish uchun matn/rasm/video yuboring.\nHTML qo'llab-quvvatlanadi.",
        "en": f"{E['plane']} <b>Mass broadcast</b>\n\nSend text/photo/video to broadcast.\nHTML supported.",
    },
    "admin.broadcast_preview": {
        "ru": f"{E['eye']} <b>Предпросмотр</b>\n\nОтправить это сообщение всем юзерам?",
        "uz": f"{E['eye']} <b>Oldindan ko'rish</b>\n\nBu xabarni barcha foydalanuvchilarga yuborishni xohlaysizmi?",
        "en": f"{E['eye']} <b>Preview</b>\n\nSend this message to all users?",
    },
    "admin.broadcast_confirm": {"ru": "Да, отправить", "uz": "Ha, yuborish", "en": "Yes, send"},
    "admin.broadcast_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "admin.broadcast_started": {
        "ru": f"{E['plane']} Рассылка запущена... Ожидай отчёт.",
        "uz": f"{E['plane']} Xabar yuborilmoqda... Hisobotni kuting.",
        "en": f"{E['plane']} Broadcast started... Wait for report.",
    },
    "admin.broadcast_done": {
        "ru": f"{E['chart']} <b>Рассылка завершена!</b>\n\n{E['check']} Доставлено: <b>{{success}}</b>\n{E['cross']} Ошибок: <b>{{failed}}</b>\n{E['users']} Всего: <b>{{total}}</b>",
        "uz": f"{E['chart']} <b>Xabar yuborish tugadi!</b>\n\n{E['check']} Yetkazildi: <b>{{success}}</b>\n{E['cross']} Xatolar: <b>{{failed}}</b>\n{E['users']} Jami: <b>{{total}}</b>",
        "en": f"{E['chart']} <b>Broadcast complete!</b>\n\n{E['check']} Delivered: <b>{{success}}</b>\n{E['cross']} Failed: <b>{{failed}}</b>\n{E['users']} Total: <b>{{total}}</b>",
    },

    # === Описания команд бота (для меню Telegram) ===
    "cmd.start": {
        "ru": "Запустить бота",
        "uz": "Botni boshlash",
        "en": "Start the bot",
    },
    "cmd.menu": {
        "ru": "Главное меню",
        "uz": "Bosh menyu",
        "en": "Main menu",
    },
    "cmd.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "cmd.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "cmd.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },
}


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """Получить перевод по ключу и языку"""
    translations = TRANSLATIONS.get(key, {})
    text = translations.get(lang, translations.get("ru", f"[{key}]"))
    if kwargs:
        text = text.format(**kwargs)
    return text


def detect_language(language_code: str | None) -> str:
    """Определяет язык по Telegram: ru → русский, uz → узбекский, остальное → английский"""
    if not language_code:
        return "en"
    if language_code.startswith("ru"):
        return "ru"
    if language_code.startswith("uz"):
        return "uz"
    return "en"
