# Admin API - Photo Upload Complete Guide

## 🎯 Архитектура загрузки фотографий

### Правильный flow:

```
┌─────────────┐         ┌──────────┐         ┌────────────┐         ┌──────────┐
│  Web Panel  │────────▶│ Admin API│────────▶│   Photos   │────────▶│ Storage  │
│             │  upload │          │  upload │  Service   │  save   │  /data   │
└─────────────┘  files  └──────────┘  bytes  └────────────┘  hash   └──────────┘
                  │                      │            │
                  │                      │            │ returns file_name
                  │                      │            │ (abc123def.jpg)
                  │                      │            ▼
                  │                      │      ┌────────────┐
                  │                      └─────▶│     DB     │
                  │                       save  │forms_photos│
                  │                       keys  └────────────┘
                  │
                  ▼
          Success response
```

### Что обрабатывает Photos Service:
- ✅ Валидация типа файла (JPEG, PNG, WebP, GIF)
- ✅ Проверка размера (до 15MB)
- ✅ Генерация SHA256 hash от контента
- ✅ Сохранение в файловую систему
- ✅ Возврат `file_name` для публичного доступа

### Что делает Admin API:
- ✅ Получает файлы от клиента
- ✅ Генерирует JWT токен для photos service
- ✅ Загружает каждый файл в photos service
- ✅ Сохраняет `storage_key` (file_name) в базу
- ✅ Управляет транзакциями и rollback

---

## 📝 API Endpoints

### 1. Создание анкеты с фотографиями

**POST /admin/v1/forms**

Принимает `multipart/form-data` с полями формы + файлы.

**Параметры:**

Form Fields (все обязательные кроме optional):
- `name` (string, 1-50 chars)
- `age` (int, 18-99)
- `height` (int, 140-220 cm)
- `bust_size` (int, 0-10)
- `caption` (string, optional, max 256 chars)
- `one_hour_price` (int, optional, >= 0)
- `two_hour_price` (int, optional, >= 0)
- `three_hour_price` (int, optional, >= 0)
- `overnight_price` (int, optional, >= 0)
- `city_slot` (int, default 1, 1-2)
- `sort_order` (int, default 0, >= 0)
- `is_visible` (bool, default false)
- `is_verified` (bool, default false)
- `has_medical_certificate` (bool, default false)
- `files` (file[], optional, max 20)

**cURL пример:**

```bash
curl -X POST "http://localhost:8000/admin/v1/forms" \
  -H "X-API-Key: your_api_key" \
  -F "name=Анна" \
  -F "age=25" \
  -F "height=170" \
  -F "bust_size=3" \
  -F "caption=Молодая и красивая" \
  -F "one_hour_price=5000" \
  -F "two_hour_price=9000" \
  -F "city_slot=1" \
  -F "is_visible=false" \
  -F "files=@photo1.jpg" \
  -F "files=@photo2.jpg" \
  -F "files=@photo3.jpg"
```

**JavaScript пример:**

```javascript
const formData = new FormData();

// Form fields
formData.append('name', 'Мария');
formData.append('age', '23');
formData.append('height', '165');
formData.append('bust_size', '2');
formData.append('caption', 'Красивая девушка');
formData.append('one_hour_price', '4000');
formData.append('two_hour_price', '7000');
formData.append('city_slot', '1');
formData.append('is_visible', 'false');

// Photos from file input
const fileInput = document.getElementById('photoInput');
for (const file of fileInput.files) {
  formData.append('files', file);
}

const response = await fetch('http://localhost:8000/admin/v1/forms', {
  method: 'POST',
  headers: {
    'X-API-Key': 'your_api_key',
  },
  body: formData
});

const result = await response.json();
console.log('Form created:', result.code);
console.log('Photos uploaded:', result.photos);
```

**Response:**

```json
{
  "code": "abc123de",
  "name": "Анна",
  "age": 25,
  "height": 170,
  "bust_size": 3,
  "caption": "Молодая и красивая",
  "one_hour_price": 5000,
  "two_hour_price": 9000,
  "three_hour_price": null,
  "overnight_price": null,
  "city_slot": 1,
  "sort_order": 0,
  "is_visible": false,
  "is_verified": false,
  "has_medical_certificate": false,
  "photos": [
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.jpg",
    "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9.jpg",
    "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b.jpg"
  ],
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

**Публичные URL фото:**
```
https://photos.domain.com/c/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.jpg
https://photos.domain.com/c/5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9.jpg
https://photos.domain.com/c/6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b.jpg
```

---

### 2. Добавление фото к существующей анкете

**POST /admin/v1/forms/{code}/photos**

Принимает `multipart/form-data` с файлами.

**cURL пример:**

```bash
curl -X POST "http://localhost:8000/admin/v1/forms/abc123de/photos" \
  -H "X-API-Key: your_api_key" \
  -F "files=@photo4.jpg" \
  -F "files=@photo5.jpg"
```

**JavaScript пример:**

```javascript
const formData = new FormData();

const fileInput = document.getElementById('additionalPhotos');
for (const file of fileInput.files) {
  formData.append('files', file);
}

const response = await fetch(`http://localhost:8000/admin/v1/forms/${formCode}/photos`, {
  method: 'POST',
  headers: {
    'X-API-Key': 'your_api_key',
  },
  body: formData
});

const result = await response.json();
console.log('Photos added:', result.ok);
```

**Response:**

```json
{
  "ok": true
}
```

---

## 🔧 Внутренняя реализация

### Admin API (`api/api/routes/admin/v1/forms.py`)

```python
async def _upload_photos_to_service(files: list[UploadFile]) -> list[str]:
    """
    Upload photos to photos service and return storage keys.
    
    Flow:
    1. Validate content type
    2. Read file bytes
    3. Upload to photos service via HTTP
    4. Get file_name (hash) back
    5. Return list of storage_keys
    """
    token = _generate_photos_token()  # JWT для photos service
    storage_keys = []
    
    for file in files:
        content = await file.read()
        result = await photos_client.upload_file(content, file.content_type, token)
        storage_keys.append(result["file_name"])
    
    return storage_keys
```

### Photos Client (`api/clients/photos.py`)

```python
class PhotosClient:
    async def upload_file(self, file_content: bytes, content_type: str, token: str) -> dict:
        """
        Upload file to photos service.
        
        Returns:
            {
                "file_name": "abc123def.jpg",
                "content_hash": "abc123def...",
                "path": "/c/abc123def.jpg",
                "public_url": "https://photos.domain.com/c/abc123def.jpg"
            }
        """
        async with httpx.AsyncClient() as client:
            files = {"file": ("photo", file_content, content_type)}
            response = await client.post(
                f"{self.base_url}/internal/v1/files",
                files=files,
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            return response.json()
```

### Photos Service (`photos/api/routes/v1/files.py`)

```python
@router.post("/internal/v1/files")
async def upload_file(file: UploadFile = File(...)):
    """
    1. Validate content type (image/jpeg, image/png, image/webp, image/gif)
    2. Check file size (max 15MB)
    3. Calculate SHA256 hash
    4. Save to /data/photos/{hash}.{ext}
    5. Return file_name for public access
    """
    extension = _ALLOWED_TYPES.get(file.content_type)
    file_name, content_hash = await save_upload_stream(file, extension)
    
    return {
        "file_name": file_name,
        "content_hash": content_hash,
        "path": f"/c/{file_name}",
        "public_url": f"https://photos.domain.com/c/{file_name}"
    }
```

---

## 🔐 Безопасность

### JWT Token для Photos Service

```python
token = create_service_token(
    secret_key=settings.API_SECRET_KEY,
    issuer="api",                    # кто создал токен
    audience="escort_photos",        # для какого сервиса
    ttl_hours=1,                     # время жизни
)
```

**Payload:**
```json
{
  "iss": "api",
  "aud": "escort_photos",
  "exp": 1704807600,
  "iat": 1704804000
}
```

Photos service проверяет:
- ✅ Подпись токена (secret key)
- ✅ Audience = "escort_photos"
- ✅ Issuer в списке allowed ("api", "admin", "main", ...)
- ✅ Токен не истек

---

## 📊 База данных

### Таблица `forms_photos`

```sql
CREATE TABLE forms_photos (
    id SERIAL PRIMARY KEY,
    form_code VARCHAR(64) NOT NULL REFERENCES forms(code) ON DELETE CASCADE,
    storage_key VARCHAR(512) NOT NULL,  -- file_name from photos service
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(form_code, storage_key)
);
```

**Пример данных:**

| id | form_code | storage_key | sort_order |
|----|-----------|-------------|------------|
| 1  | abc123de  | e3b0c442...855.jpg | 0 |
| 2  | abc123de  | 5feceb66...7e9.jpg | 1 |
| 3  | abc123de  | 6b86b273...b4b.jpg | 2 |

---

## ⚠️ Обработка ошибок

### 400 Bad Request - Invalid file type
```json
{
  "detail": "Invalid file type: image/bmp. Allowed: jpeg, png, webp, gif"
}
```

### 400 Bad Request - Too many files
```json
{
  "detail": "Maximum 20 photos per request"
}
```

### 413 Request Entity Too Large
```json
{
  "detail": "File too large"
}
```
*Если файл > 15MB (настройка photos service)*

### 500 Internal Server Error - Upload failed
```json
{
  "detail": "Failed to upload photo: Connection timeout"
}
```

### Rollback при ошибке

Если загрузка одного из файлов в photos service падает:
1. ❌ Photos service вернул ошибку
2. 🔄 Admin API НЕ создает форму (rollback)
3. 🗑️ Уже загруженные фото остаются в photos service (orphaned)
4. ⚠️ Клиент получает 500 ошибку

**TODO:** Добавить cleanup orphaned photos (фоновая задача).

---

## 🧪 Тестирование

### 1. Создание формы с фото
```bash
curl -X POST "http://localhost:8000/admin/v1/forms" \
  -H "X-API-Key: test_key" \
  -F "name=Test" \
  -F "age=25" \
  -F "height=170" \
  -F "bust_size=3" \
  -F "one_hour_price=5000" \
  -F "files=@test1.jpg" \
  -F "files=@test2.jpg"
```

### 2. Добавление фото
```bash
curl -X POST "http://localhost:8000/admin/v1/forms/abc123/photos" \
  -H "X-API-Key: test_key" \
  -F "files=@test3.jpg"
```

### 3. Удаление фото по индексу
```bash
curl -X DELETE "http://localhost:8000/admin/v1/forms/abc123/photos/0" \
  -H "X-API-Key: test_key"
```

### 4. Проверка публичного доступа
```bash
curl -I "https://photos.domain.com/c/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.jpg"
```

---

## 🚀 Production настройки

### `.env` для API:
```env
API_SECRET_KEY=your_secret_key_here
PHOTOS_API_URL=http://photos:8005
ADMIN_API_KEY=your_admin_api_key
```

### `.env` для Photos:
```env
API_SECRET_KEY=your_secret_key_here  # тот же что в API
PHOTOS_STORAGE_PATH=/data/photos
PHOTOS_SCHEME=https
PHOTOS_DOMAIN=photos.domain.com
PHOTOS_MAX_FILE_SIZE_MB=15
PHOTOS_ALLOWED_ISSUERS=api,admin,main,support,web_app
```

### Nginx для photos:
```nginx
location /c/ {
    alias /data/photos/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## ✅ Checklist

- ✅ Photos service обрабатывает типы, размеры, hash
- ✅ Admin API загружает файлы → photos service → сохраняет keys
- ✅ Создание формы с фото в одном запросе
- ✅ Добавление фото к существующей форме
- ✅ JWT аутентификация между сервисами
- ✅ Публичный доступ через `/c/{hash}`
- ✅ Обработка ошибок
- ✅ Документация с примерами
