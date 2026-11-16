# web_app

Mini App разделен на:

- `frontend/` — UI на React/TypeScript
- `backend/` — тонкий BFF для Telegram session и вызовов `api/client/v1`

Основной контракт — `api/client/v1`.

Сейчас реализовано:

- Telegram session bootstrap через `initData`;
- backend BFF:
  - `/web-app/api/v1/auth/session`
  - `/web-app/api/v1/about`
  - `/web-app/api/v1/support`
  - `/web-app/api/v1/models`
  - `/web-app/api/v1/profile`
- frontend на React/Vite:
  - `about`
  - `models`
  - `model details`
  - `support`
  - `profile`

Что не делаем здесь:

- прямой доступ к БД;
- бизнес-логику;
- nginx;
- legacy tenant/worker/LTP ветки.
