# Photo Upload & City Validation - Updated Documentation

## 🔄 Что изменено:

### 1. ✅ Загрузка фотографий переделана на прямую загрузку файлов

**Раньше (неправильно):**
```json
POST /admin/v1/forms/{code}/photos
{
  "urls": ["photo1.jpg", "photo2.jpg"]  // ← Нужно было заранее загружать
}
```

**Теперь (правильно):**
```bash
# Загружаем файлы напрямую через multipart/form-data
curl -X POST "http://localhost:8000/admin/v1/forms/abc123/photos" \
  -H "X-API-Key: your_api_key" \
  -F "files=@photo1.jpg" \
  -F "files=@photo2.jpg" \
  -F "files=@photo3.jpg"
```

**JavaScript пример:**
```javascript
const API_KEY = 'your_api_key';
const formCode = 'abc123';

// Загрузка фото из input[type=file]
const fileInput = document.getElementById('photoInput');
const formData = new FormData();

for (const file of fileInput.files) {
  formData.append('files', file);
}

const response = await fetch(`http://localhost:8000/admin/v1/forms/${formCode}/photos`, {
  method: 'POST',
  headers: {
    'X-API-Key': API_KEY,
  },
  body: formData  // multipart/form-data автоматически
});

const result = await response.json();
console.log('Photos uploaded:', result);
```

**Что происходит внутри:**
1. Admin API получает файлы через multipart/form-data
2. Генерирует JWT токен для photos service
3. Каждый файл загружается в photos service через `POST /internal/v1/files`
4. Photos service возвращает `file_name` (content hash: `abc123def456.jpg`)
5. Admin API сохраняет `storage_key` в базу `forms_photos`
6. Публичный URL: `https://photos.domain.com/c/abc123def456.jpg`

**Ограничения:**
- Максимум 20 фото за один запрос
- Разрешенные форматы: JPEG, PNG, WebP, GIF
- Размер файла: до 15MB (настройка в photos service)

---

### 2. ✅ Валидация городов перенесена в API

**Раньше (legacy):**
```python
# main/services/city.py
# Каждый бот валидирует сам через Open-Meteo API
await validate_city("Moscow")
```

**Теперь (централизованно):**
```bash
# Все боты обращаются к единому API endpoint
curl -X POST "http://localhost:8000/client/v1/cities/validate" \
  -H "Authorization: Bearer <service_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "city_name": "Москва"
  }'
```

**Response:**
```json
{
  "city_name": "Moscow",
  "is_valid": true
}
```

**Если город не найден:**
```json
{
  "city_name": null,
  "is_valid": false
}
```

**Python пример (для ботов):**
```python
import httpx
from shared.auth import create_service_token

async def validate_city_via_api(city_name: str) -> str | None:
    token = create_service_token(
        secret_key=settings.API_SECRET_KEY,
        issuer="main",
        audience=settings.API_AUDIENCE,
        ttl_hours=1,
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.API_BASE_URL}/client/v1/cities/validate",
            json={"city_name": city_name},
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        data = response.json()

        if data["is_valid"]:
            return data["city_name"]
        return None
```

**Преимущества:**
- ✅ Единая точка валидации
- ✅ Можно добавить кеширование в API
- ✅ Централизованное логирование
- ✅ Легче мониторить и обновлять
- ✅ Боты остаются thin clients

---

## 📁 Структура изменений

### Новые файлы:

```
api/
├── domain/
│   └── cities/
│       ├── __init__.py
│       └── service.py              # Валидация городов через Open-Meteo
├── clients/
│   ├── __init__.py
│   └── photos.py                   # HTTP client для photos service
├── schemas/
│   └── client/
│       └── cities.py               # ValidateCityRequest/Response
└── api/routes/
    └── client/v1/
        └── cities.py               # POST /client/v1/cities/validate
```

### Обновленные файлы:

```
api/api/routes/admin/v1/forms.py    # add_photos() теперь принимает файлы
api/schemas/admin/forms.py          # Удален AddPhotosRequest
main/services/city.py               # Теперь вызывает API (legacy compatible)
```

---

## 🔐 Audience для токенов

### Photos Service:
```python
token = create_service_token(
    secret_key=settings.API_SECRET_KEY,
    issuer="api",
    audience="escort_photos",  # ← специфичный для photos
    ttl_hours=1,
)
```

### API (боты → API):
```python
token = create_service_token(
    secret_key=settings.API_SECRET_KEY,
    issuer="main",  # или "support", "admin"
    audience=settings.API_AUDIENCE,  # "escort_api"
    ttl_hours=24,
)
```

---

## 🧪 Тестирование

### 1. Загрузка фото через curl:
```bash
curl -X POST "http://localhost:8000/admin/v1/forms/testcode/photos" \
  -H "X-API-Key: your_api_key" \
  -F "files=@/path/to/photo1.jpg" \
  -F "files=@/path/to/photo2.png"
```

### 2. Валидация города:
```bash
# Через service token
TOKEN=$(python3 -c "from shared.auth import create_service_token; print(create_service_token('secret', issuer='test', audience='escort_api'))")

curl -X POST "http://localhost:8000/client/v1/cities/validate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"city_name": "Москва"}'
```

---

## 📊 Миграция legacy кода

### Main bot (уже обновлен):
```python
# main/services/city.py теперь вызывает API
# Старый код работает, но с deprecation notice
from services import validate_city

city = await validate_city("Moscow")  # Работает через API
```

### Support/Admin боты:
Обновить аналогично, или напрямую вызывать API endpoint.

---

## ⚠️ Breaking Changes:

### 1. Admin API - загрузка фото:
- **Удалено**: `AddPhotosRequest` schema с полем `urls: list[str]`
- **Добавлено**: Прямая загрузка через `files: list[UploadFile]`
- **Формат**: multipart/form-data вместо JSON

### 2. Photos service audience:
- **Было**: могли использовать любой audience
- **Стало**: требуется `audience="escort_photos"`

---

## ✅ Готово к деплою

Все изменения обратно совместимы:
- ✅ Main bot продолжает работать (вызывает API через обновленный service)
- ✅ Admin API принимает файлы напрямую
- ✅ Новый endpoint `/client/v1/cities/validate` доступен всем сервисам
- ✅ Синтаксис Python валиден
