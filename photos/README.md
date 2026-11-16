# photos

Single-project media service.

Не переносим:

- tenant-aware contract
- legacy issuer maps
- video support

Оставляем:

- internal upload
- internal delete
- public serve by content hash

## Контракт

- `POST /internal/v1/files`
- `DELETE /internal/v1/files/{file_name}`
- `GET /c/{file_name}`
- `GET /v1/health`

## Правила

- только изображения;
- публичная раздача идет через `/c/{content_hash}.{ext}`;
- загрузка и удаление доступны только сервисам по bearer token;
- имя файла генерируется по sha256 content hash;
- сервис не знает ничего про tenant, worker, panel legacy.
