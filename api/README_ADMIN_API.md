# Admin API Authentication

## Обзор
Все endpoints в `/admin/v1/*` защищены API ключом для доступа из внешней веб-панели.

## Настройка

### 1. Добавить ADMIN_API_KEY в .env
```bash
# Сгенерировать случайный ключ:
openssl rand -hex 32

# Добавить в .env:
ADMIN_API_KEY=your_generated_key_here
```

### 2. Использование в запросах

Все запросы к admin endpoints должны включать header:
```
X-API-Key: your_generated_key_here
```

## Примеры запросов

### Получить список клиентов
```bash
curl -X GET "http://localhost:8000/admin/v1/clients?page=1&per_page=10" \
  -H "X-API-Key: your_api_key_here"
```

### Получить детали клиента
```bash
curl -X GET "http://localhost:8000/admin/v1/clients/123456" \
  -H "X-API-Key: your_api_key_here"
```

### Забанить клиента
```bash
curl -X PATCH "http://localhost:8000/admin/v1/clients/123456/ban" \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"is_banned": true}'
```

### Установить соглашение клиенту
```bash
curl -X PATCH "http://localhost:8000/admin/v1/clients/123456/agreement" \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"agreement_id": 1}'
```

### Получить список соглашений
```bash
curl -X GET "http://localhost:8000/admin/v1/agreements" \
  -H "X-API-Key: your_api_key_here"
```

## Ошибки аутентификации

### 401 Unauthorized - Missing X-API-Key header
```json
{
  "detail": "Missing X-API-Key header"
}
```

### 401 Unauthorized - Invalid API key
```json
{
  "detail": "Invalid API key"
}
```

### 500 Internal Server Error - ADMIN_API_KEY not configured
```json
{
  "detail": "ADMIN_API_KEY not configured"
}
```

## Защищенные endpoints

Все endpoints в следующих роутерах требуют API ключ:
- `GET /admin/v1/clients` - список клиентов
- `GET /admin/v1/clients/{user_id}` - детали клиента
- `PATCH /admin/v1/clients/{user_id}/ban` - бан/разбан
- `PATCH /admin/v1/clients/{user_id}/agreement` - установить соглашение
- `GET /admin/v1/agreements` - список соглашений

## Интеграция с веб-панелью

### JavaScript/TypeScript пример
```javascript
const API_KEY = 'your_api_key_here';
const API_BASE_URL = 'http://localhost:8000';

async function getClients(page = 1, perPage = 10) {
  const response = await fetch(
    `${API_BASE_URL}/admin/v1/clients?page=${page}&per_page=${perPage}`,
    {
      headers: {
        'X-API-Key': API_KEY,
      },
    }
  );
  return response.json();
}

async function banClient(userId, isBanned) {
  const response = await fetch(
    `${API_BASE_URL}/admin/v1/clients/${userId}/ban`,
    {
      method: 'PATCH',
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ is_banned: isBanned }),
    }
  );
  return response.json();
}
```

### Python пример
```python
import requests

API_KEY = 'your_api_key_here'
API_BASE_URL = 'http://localhost:8000'

def get_clients(page=1, per_page=10):
    response = requests.get(
        f'{API_BASE_URL}/admin/v1/clients',
        headers={'X-API-Key': API_KEY},
        params={'page': page, 'per_page': per_page}
    )
    return response.json()

def ban_client(user_id, is_banned):
    response = requests.patch(
        f'{API_BASE_URL}/admin/v1/clients/{user_id}/ban',
        headers={
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json'
        },
        json={'is_banned': is_banned}
    )
    return response.json()
```

## Безопасность

1. **Никогда не коммитьте ADMIN_API_KEY в git**
2. **Используйте HTTPS в продакшене**
3. **Ротируйте ключ периодически**
4. **Храните ключ в переменных окружения**
5. **Не передавайте ключ через URL параметры**

## Отличие от service_session

- `service_session` - JWT токены для внутренней service-to-service коммуникации (main/support/admin боты → API)
- `admin_session` - API ключ для внешней веб-панели → API
