# new_escort

Новый каркас проекта escort, собранный по утвержденному плану миграции.

## Состав репозитория

- `api/` — единая точка бизнес-логики и схемы данных
- `main/` — основной Telegram-бот, тонкий клиент к `api`
- `support/` — бот поддержки с единым форумом поддержки
- `admin/` — админский бот для управления и поиска клиентов
- `web_app/` — Mini App: frontend + backend/BFF-обвязка
- `photos/` — отдельный media-сервис
- `logs/` — прием событий и отправка в Telegram thread
- `shared/` — общая библиотека
- `docs/` — документация по миграции и архитектуре

## Важные принципы

- `worker`-домен, LTP и реферальная механика не переносятся
- `nginx` в новую репу не закладывается
- тексты остаются в `.yaml`
- клавиатуры живут в `keyboards` своего сервиса
- логовые тексты живут только в `logs/`

## Локальный запуск

1. Создать `.env` на основе `.env.example`.
   Для точечной настройки по сервисам можно брать шаблоны из:
   - `api/.env.example`
   - `main/.env.example`
   - `support/.env.example`
   - `admin/.env.example`
   - `logs/.env.example`
   - `photos/.env.example`
   - `web_app/.env.example`
2. Заполнить обязательные секреты и публичные URL:
   - `API_SECRET_KEY`
   - `DB_URL`
   - `MAIN_WEBHOOK_URL`, `SUPPORT_WEBHOOK_URL`, `ADMIN_WEBHOOK_URL`
   - `MAIN_BOT_TOKEN`, `SUPPORT_BOT_TOKEN`, `ADMIN_BOT_TOKEN`
   - `LOGS_BOT_TOKEN`, `LOGS_CHAT_ID`, `LOGS_TOPIC_ID`
   - `WEB_APP_URL`, `WEB_APP_SESSION_SECRET`, `WEB_APP_BOT_TOKEN`
3. Поднять стек:

```bash
docker compose up --build
```

`api` сам применяет Alembic migration при старте контейнера. `web_app` собирает frontend внутри Docker-образа и раздает его через backend без `nginx`.
