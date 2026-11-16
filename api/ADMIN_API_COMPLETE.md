# Admin API - Complete Endpoints Documentation

Все endpoints защищены API ключом через header `X-API-Key`.

## Базовый URL
```
http://localhost:8000/admin/v1
```

---

## 1. Clients (Клиенты)

### GET /admin/v1/clients
Список клиентов с поиском и пагинацией
```bash
curl -X GET "http://localhost:8000/admin/v1/clients?q=username&page=1&per_page=10" \
  -H "X-API-Key: your_api_key"
```

### GET /admin/v1/clients/{user_id}
Детали клиента
```bash
curl -X GET "http://localhost:8000/admin/v1/clients/123456" \
  -H "X-API-Key: your_api_key"
```

### PATCH /admin/v1/clients/{user_id}/ban
Бан/разбан клиента
```bash
curl -X PATCH "http://localhost:8000/admin/v1/clients/123456/ban" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"is_banned": true}'
```

### PATCH /admin/v1/clients/{user_id}/agreement
Установить соглашение клиенту
```bash
curl -X PATCH "http://localhost:8000/admin/v1/clients/123456/agreement" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"agreement_id": 1}'
```

---

## 2. Agreements (Соглашения)

### GET /admin/v1/agreements
Список всех соглашений
```bash
curl -X GET "http://localhost:8000/admin/v1/agreements" \
  -H "X-API-Key: your_api_key"
```

---

## 3. Forms (Анкеты/Models)

### GET /admin/v1/forms
Список всех анкет
```bash
# Все анкеты
curl -X GET "http://localhost:8000/admin/v1/forms" \
  -H "X-API-Key: your_api_key"

# Фильтр по городу (city_slot: 1 или 2)
curl -X GET "http://localhost:8000/admin/v1/forms?city_slot=1" \
  -H "X-API-Key: your_api_key"
```

**Response:**
```json
{
  "items": [
    {
      "code": "abc123de",
      "name": "Анна",
      "age": 25,
      "height": 170,
      "bust_size": 3,
      "one_hour_price": 5000,
      "two_hour_price": 9000,
      "three_hour_price": 12000,
      "overnight_price": 20000,
      "city_slot": 1,
      "sort_order": 0,
      "is_visible": true,
      "is_verified": true,
      "has_medical_certificate": false,
      "photo_count": 5,
      "created_at": "2024-01-15T12:00:00Z"
    }
  ]
}
```

### GET /admin/v1/forms/{code}
Детали анкеты
```bash
curl -X GET "http://localhost:8000/admin/v1/forms/abc123de" \
  -H "X-API-Key: your_api_key"
```

**Response:**
```json
{
  "code": "abc123de",
  "name": "Анна",
  "age": 25,
  "height": 170,
  "bust_size": 3,
  "caption": "Описание анкеты",
  "one_hour_price": 5000,
  "two_hour_price": 9000,
  "three_hour_price": 12000,
  "overnight_price": 20000,
  "city_slot": 1,
  "sort_order": 0,
  "is_visible": true,
  "is_verified": true,
  "has_medical_certificate": false,
  "photos": ["photo1.jpg", "photo2.jpg"],
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-16T12:00:00Z"
}
```

### POST /admin/v1/forms
Создать новую анкету
```bash
curl -X POST "http://localhost:8000/admin/v1/forms" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Мария",
    "age": 23,
    "height": 165,
    "bust_size": 2,
    "caption": "Молодая и красивая",
    "one_hour_price": 4000,
    "two_hour_price": 7000,
    "city_slot": 1,
    "sort_order": 0,
    "is_visible": false,
    "is_verified": false
  }'
```

### PUT /admin/v1/forms/{code}
Обновить анкету
```bash
curl -X PUT "http://localhost:8000/admin/v1/forms/abc123de" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Анна (обновлено)",
    "age": 26,
    "one_hour_price": 5500,
    "is_visible": true
  }'
```

### DELETE /admin/v1/forms/{code}
Удалить анкету (cascade удаление всех связанных данных)
```bash
curl -X DELETE "http://localhost:8000/admin/v1/forms/abc123de" \
  -H "X-API-Key: your_api_key"
```

### POST /admin/v1/forms/{code}/toggle
Toggle булевого поля (is_visible, is_verified, has_medical_certificate)
```bash
curl -X POST "http://localhost:8000/admin/v1/forms/abc123de/toggle" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"field": "is_visible"}'
```

### POST /admin/v1/forms/swap-positions
Поменять позиции двух анкет
```bash
curl -X POST "http://localhost:8000/admin/v1/forms/swap-positions" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "code_a": "abc123de",
    "code_b": "xyz789gh"
  }'
```

---

## 4. Form Photos (Фотографии анкет)

### POST /admin/v1/forms/{code}/photos
Добавить фотографии к анкете
```bash
curl -X POST "http://localhost:8000/admin/v1/forms/abc123de/photos" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "photo1.jpg",
      "photo2.jpg",
      "photo3.jpg"
    ]
  }'
```

### DELETE /admin/v1/forms/{code}/photos/{index}
Удалить фотографию по индексу (0-based)
```bash
# Удалить первую фотографию (index=0)
curl -X DELETE "http://localhost:8000/admin/v1/forms/abc123de/photos/0" \
  -H "X-API-Key: your_api_key"
```

---

## 5. Reviews (Отзывы)

### GET /admin/v1/reviews/forms/{code}
Список отзывов для анкеты
```bash
curl -X GET "http://localhost:8000/admin/v1/reviews/forms/abc123de" \
  -H "X-API-Key: your_api_key"
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "form_code": "abc123de",
      "author": "Иван",
      "review_date": "15.01.2024",
      "body": "Отличная девушка, все понравилось",
      "score": 5,
      "created_at": "2024-01-15T12:00:00Z"
    }
  ]
}
```

### POST /admin/v1/reviews/forms/{code}
Создать отзыв для анкеты
```bash
curl -X POST "http://localhost:8000/admin/v1/reviews/forms/abc123de" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "author": "Михаил",
    "review_date": "20.01.2024",
    "body": "Супер, рекомендую!",
    "score": 5
  }'
```

### PUT /admin/v1/reviews/{review_id}
Обновить отзыв
```bash
curl -X PUT "http://localhost:8000/admin/v1/reviews/1" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "body": "Обновленный текст отзыва",
    "score": 4
  }'
```

### DELETE /admin/v1/reviews/{review_id}
Удалить отзыв
```bash
curl -X DELETE "http://localhost:8000/admin/v1/reviews/1" \
  -H "X-API-Key: your_api_key"
```

---

## 6. Services (Услуги)

### GET /admin/v1/services/forms/{code}
Список услуг для анкеты
```bash
curl -X GET "http://localhost:8000/admin/v1/services/forms/abc123de" \
  -H "X-API-Key: your_api_key"
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "form_code": "abc123de",
      "name": "Классический секс",
      "created_at": "2024-01-15T12:00:00Z"
    }
  ]
}
```

### POST /admin/v1/services/forms/{code}
Создать услугу для анкеты
```bash
curl -X POST "http://localhost:8000/admin/v1/services/forms/abc123de" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Минет в презервативе"
  }'
```

### PUT /admin/v1/services/{service_id}
Обновить услугу
```bash
curl -X PUT "http://localhost:8000/admin/v1/services/1" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Обновленное название услуги"
  }'
```

### DELETE /admin/v1/services/{service_id}
Удалить услугу
```bash
curl -X DELETE "http://localhost:8000/admin/v1/services/1" \
  -H "X-API-Key: your_api_key"
```

---

## 7. Additionals (Дополнительные услуги)

### GET /admin/v1/additionals/forms/{code}
Список доп. услуг для анкеты
```bash
curl -X GET "http://localhost:8000/admin/v1/additionals/forms/abc123de" \
  -H "X-API-Key: your_api_key"
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "form_code": "abc123de",
      "name": "Игрушки",
      "price": 1000,
      "created_at": "2024-01-15T12:00:00Z"
    }
  ]
}
```

### POST /admin/v1/additionals/forms/{code}
Создать доп. услугу для анкеты
```bash
curl -X POST "http://localhost:8000/admin/v1/additionals/forms/abc123de" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Стриптиз",
    "price": 2000
  }'
```

### PUT /admin/v1/additionals/{additional_id}
Обновить доп. услугу
```bash
curl -X PUT "http://localhost:8000/admin/v1/additionals/1" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Стриптиз + танец",
    "price": 2500
  }'
```

### DELETE /admin/v1/additionals/{additional_id}
Удалить доп. услугу
```bash
curl -X DELETE "http://localhost:8000/admin/v1/additionals/1" \
  -H "X-API-Key: your_api_key"
```

---

## 8. Promos (Промокоды)

### GET /admin/v1/promos
Список всех промокодов
```bash
curl -X GET "http://localhost:8000/admin/v1/promos" \
  -H "X-API-Key: your_api_key"
```

**Response:**
```json
{
  "items": [
    {
      "name": "SUMMER2024",
      "discount": 10,
      "created_at": "2024-01-15T12:00:00Z"
    }
  ]
}
```

### POST /admin/v1/promos
Создать промокод
```bash
curl -X POST "http://localhost:8000/admin/v1/promos" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "WINTER2024",
    "discount": 15
  }'
```

### DELETE /admin/v1/promos/{name}
Удалить промокод
```bash
curl -X DELETE "http://localhost:8000/admin/v1/promos/SUMMER2024" \
  -H "X-API-Key: your_api_key"
```

---

## Общие ответы

### Успешная операция (без тела)
```json
{
  "ok": true
}
```

### Ошибка 401 - Missing API Key
```json
{
  "detail": "Missing X-API-Key header"
}
```

### Ошибка 401 - Invalid API Key
```json
{
  "detail": "Invalid API key"
}
```

### Ошибка 404 - Not Found
```json
{
  "detail": "Form not found"
}
```

### Ошибка 409 - Conflict
```json
{
  "detail": "Promo with this name already exists"
}
```

---

## Настройка API ключа

1. Сгенерировать ключ:
```bash
openssl rand -hex 32
```

2. Добавить в `.env`:
```env
ADMIN_API_KEY=your_generated_key_here
```

3. Использовать в запросах:
```bash
-H "X-API-Key: your_generated_key_here"
```

---

## JavaScript пример

```javascript
const API_KEY = 'your_api_key_here';
const API_BASE = 'http://localhost:8000/admin/v1';

async function getForms() {
  const response = await fetch(`${API_BASE}/forms`, {
    headers: { 'X-API-Key': API_KEY }
  });
  return response.json();
}

async function createForm(data) {
  const response = await fetch(`${API_BASE}/forms`, {
    method: 'POST',
    headers: {
      'X-API-Key': API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  return response.json();
}

async function updateForm(code, data) {
  const response = await fetch(`${API_BASE}/forms/${code}`, {
    method: 'PUT',
    headers: {
      'X-API-Key': API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  return response.json();
}

async function deleteForm(code) {
  const response = await fetch(`${API_BASE}/forms/${code}`, {
    method: 'DELETE',
    headers: { 'X-API-Key': API_KEY }
  });
  return response.json();
}
```

---

## Сводка endpoints

**Всего: 32 endpoints**

- **Clients**: 4 endpoints
- **Agreements**: 1 endpoint
- **Forms**: 9 endpoints
- **Photos**: 2 endpoints
- **Reviews**: 4 endpoints
- **Services**: 4 endpoints
- **Additionals**: 4 endpoints
- **Promos**: 3 endpoints

Все endpoints защищены API ключом через `X-API-Key` header.
