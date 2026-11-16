# api

Единая точка бизнес-логики, схемы БД, миграций и внутренних контрактов.

Сюда уходит:

- доменная логика из `escort_v1_main`
- support-домен без LTP
- логика анкет, клиентов, заказов, настроек
- интеграции с `photos` и `logs`

## Что живет в api

- `core/` — настройки сервиса
- `db/` — engine, session factory, transaction manager
- `models/` — split SQLAlchemy-модели по доменам
- `repositories/` — доступ к данным
- `domain/` — сервисный слой поверх репозиториев
- `api/routes/` — FastAPI роуты по аудиториям
- `migrations/` — alembic scaffold

`main/`, `support/`, `admin/`, `web_app/` не должны держать собственный ORM/db-слой.
