# bot_5_trimmer

Telegram-бот для обрезки видеофайлов через ffmpeg.

## Возможности

- Принимает видеофайлы до 2 ГБ (через Local Bot API)
- Обрезка по тайм-кодам начала и конца
- Быстрый режим (stream copy) и точный режим (re-encode)
- Три языка: русский, узбекский, английский
- Обязательная подписка на каналы
- Админ-панель: статистика, каналы, рассылка

## Стек

- Python 3.12 + aiogram 3.26
- PostgreSQL 16 (SQLAlchemy 2.x async)
- ffmpeg
- Local Bot API (aiogram/telegram-bot-api)
- Docker Compose

## Деплой

```bash
cp .env.example .env
# заполнить BOT_TOKEN, API_ID, API_HASH, DB_PASSWORD, ADMIN_IDS

docker compose up -d --build
docker compose logs -f bot
```

## Структура

```
bot/
  main.py, config.py, i18n.py, emojis.py
  database/   — models, crud
  handlers/   — start, admin, trim (TODO)
  middlewares/ — subscription, rate_limit
  keyboards/  — inline, admin
  services/   — trimmer (TODO)
  utils/      — commands, timecode (TODO)
```
