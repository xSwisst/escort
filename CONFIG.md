# Configuration Guide

## 🎯 Философия конфигурации

Каждый сервис имеет **свой собственный `.env` файл** в своей директории. Нет общего корневого `.env` файла.

```
new_escort/
├── api/.env
├── main/.env
├── support/.env
├── admin/.env
├── photos/.env
├── logs/.env
├── web_app/.env
└── web/.env
```

## 📋 Шаблоны конфигов

В каждом сервисе есть `.env.example` - скопируй его в `.env` и заполни:

```bash
# Для каждого сервиса
cd api && cp .env.example .env
cd main && cp .env.example .env
cd support && cp .env.example .env
cd admin && cp .env.example .env
cd photos && cp .env.example .env
cd logs && cp .env.example .env
cd web_app && cp .env.example .env
cd web && cp .env.example .env
```

## 🔐 Общие секреты

Некоторые переменные должны быть **одинаковыми** во всех сервисах:

### API_SECRET_KEY
Используется для JWT токенов между сервисами. **Должен быть одинаковым везде!**

```bash
# Сгенерируй один раз
openssl rand -hex 32
# Результат: a1b2c3d4e5f6...

# Вставь во ВСЕ .env файлы:
# - api/.env
# - main/.env
# - support/.env
# - admin/.env
# - photos/.env
# - logs/.env
# - web_app/.env
```

### ADMIN_API_KEY
Используется для доступа к admin API. **Только в api/.env**

```bash
openssl rand -hex 32
# Вставь в api/.env
```

## 📦 Минимальная конфигурация для запуска

### 1. API Service (api/.env)

```env
API_SECRET_KEY=your_secret_key_here
ADMIN_API_KEY=your_admin_key_here
DB_URL=postgresql+asyncpg://escort:escort@postgres:5432/escort
PHOTOS_API_URL=http://photos:8005
LOGS_API_URL=http://logs:8006
```

### 2. Main Bot (main/.env)

```env
BOT_TOKEN=123456:ABC-DEF...
API_SECRET_KEY=your_secret_key_here
WEBHOOK_URL=https://webhook.domain.com/webhook/main
WEBHOOK_SECRET_TOKEN=change-me
API_BASE_URL=http://api:8000
WEB_APP_URL=https://app.domain.com
SUPPORT_BOT_URL=https://t.me/escort_support_bot
OWNER_ID=123456789
```

### 3. Support Bot (support/.env)

```env
BOT_TOKEN=789012:GHI-JKL...
API_SECRET_KEY=your_secret_key_here
WEBHOOK_URL=https://webhook.domain.com/webhook/support
WEBHOOK_SECRET_TOKEN=change-me
API_BASE_URL=http://api:8000
SUPPORT_FORUM_CHAT_ID=-1001234567890
```

### 4. Admin Bot (admin/.env)

```env
BOT_TOKEN=345678:MNO-PQR...
API_SECRET_KEY=your_secret_key_here
WEBHOOK_URL=https://webhook.domain.com/webhook/admin
WEBHOOK_SECRET_TOKEN=change-me
API_BASE_URL=http://api:8000
ADMIN_ALLOWED_IDS=123456789,987654321
```

### 5. Photos Service (photos/.env)

```env
API_SECRET_KEY=your_secret_key_here
PHOTOS_STORAGE_PATH=/data/photos
PHOTOS_SCHEME=https
PHOTOS_DOMAIN=photos.domain.com
PHOTOS_MAX_FILE_SIZE_MB=15
```

### 6. Logs Service (logs/.env)

```env
API_SECRET_KEY=your_secret_key_here
DB_HOST=postgres
DB_PORT=5432
DB_USER=escort
DB_PASSWORD=escort
DB_NAME=escort
LOGS_BOT_TOKEN=901234:STU-VWX...
LOGS_CHAT_ID=-1001234567890
LOGS_TOPIC_ID=123
```

### 7. Web App (web_app/.env)

```env
API_SECRET_KEY=your_secret_key_here
WEB_APP_SESSION_SECRET=your_session_secret_here
WEB_APP_BOT_TOKEN=567890:YZA-BCD...
API_BASE_URL=http://api:8000
WEB_APP_INFO_CHANNEL_URL=https://t.me/escort_info
WEB_APP_REVIEWS_CHANNEL_URL=https://t.me/escort_reviews
WEB_APP_SUPPORT_BOT_URL=https://t.me/escort_support_bot
```

### 8. Web Landing (web/.env)

```env
HOST=0.0.0.0
PORT=8007
API_PORT=8007

WEB_DOMAIN=elegant-agency.fun
WEB_URL=https://elegant-agency.fun

BOT_USERNAME=@ElegantAgencyApp
BOT_URL=https://t.me/ElegantAgencyApp
SUPPORT_BOT_URL=https://t.me/ElegantAgencySupportApp
WEB_APP_URL=https://app.elegant-agency.fun

APP_NAME=ELEGANT AGENCY
CONTACT_EMAIL=contact@elegant-agency.fun
```

## 🚀 Быстрый старт

### Скрипт для генерации всех секретов:

```bash
#!/bin/bash

# Генерация секретов
API_SECRET=$(openssl rand -hex 32)
ADMIN_API_KEY=$(openssl rand -hex 32)
WEB_APP_SECRET=$(openssl rand -hex 32)

echo "=== Сгенерированные секреты ==="
echo ""
echo "API_SECRET_KEY (используй во ВСЕХ сервисах):"
echo "$API_SECRET"
echo ""
echo "ADMIN_API_KEY (только для api/.env):"
echo "$ADMIN_API_KEY"
echo ""
echo "WEB_APP_SESSION_SECRET (только для web_app/.env):"
echo "$WEB_APP_SECRET"
echo ""
echo "=== Webhook секреты (по одному для каждого бота) ==="
echo "MAIN_WEBHOOK_SECRET: $(openssl rand -hex 16)"
echo "SUPPORT_WEBHOOK_SECRET: $(openssl rand -hex 16)"
echo "ADMIN_WEBHOOK_SECRET: $(openssl rand -hex 16)"
```

## 🔍 Проверка конфигурации

### Скрипт валидации:

```bash
#!/bin/bash

check_service() {
    local service=$1
    local env_file="$service/.env"
    
    if [ ! -f "$env_file" ]; then
        echo "❌ $service: .env не найден"
        return 1
    fi
    
    if ! grep -q "API_SECRET_KEY=" "$env_file"; then
        echo "❌ $service: отсутствует API_SECRET_KEY"
        return 1
    fi
    
    echo "✅ $service: конфиг в порядке"
    return 0
}

echo "Проверка конфигурации сервисов..."
echo ""

check_service "api"
check_service "main"
check_service "support"
check_service "admin"
check_service "photos"
check_service "logs"
check_service "web_app"

echo ""
echo "Проверка завершена"
```

## 📝 Что убрано из конфигов

**Удалены легаси параметры:**
- ❌ `LOGS_AUDIENCE` - не нужен, используем API_AUDIENCE
- ❌ `LOGS_ALLOWED_ISSUERS` - убрана валидация issuer
- ❌ `LOGS_TIMEOUT_SEC` - используем дефолтные таймауты
- ❌ `LOGS_TELEGRAM_API_BASE_URL` - используем стандартный
- ❌ `PHOTOS_ALLOWED_ISSUERS` - убрана валидация issuer
- ❌ `PHOTOS_API_AUDIENCE` - не нужен
- ❌ `ADMIN_RESULTS_PER_PAGE` - хардкодим в коде
- ❌ `MODELS_PER_PAGE` - хардкодим в коде
- ❌ `MEDIA_PATH` - хардкодим в коде

**Почему убрали?**
- Упрощение конфигурации
- Меньше мест для ошибок
- Разумные дефолты в коде
- Не было реальных кейсов когда это нужно менять

## 🏗️ Docker Compose

Docker compose читает `.env` файлы из каждого сервиса:

```yaml
services:
  api:
    env_file:
      - api/.env
    # переменные из api/.env автоматически доступны

  main:
    env_file:
      - main/.env

  photos:
    env_file:
      - photos/.env
```

## ⚠️ Важно

1. **Не коммить `.env` файлы в git** - они в `.gitignore`
2. **API_SECRET_KEY должен быть одинаковым** во всех сервисах
3. **Каждый бот имеет свой BOT_TOKEN** и свой WEBHOOK_SECRET_TOKEN
4. **ADMIN_API_KEY только в api/.env** - он для веб-панели

## 🔒 Production

Для production используй secrets manager (AWS Secrets, Vault, etc.) вместо `.env` файлов.

Пример с Docker Swarm secrets:

```yaml
services:
  api:
    secrets:
      - api_secret_key
      - admin_api_key
    environment:
      API_SECRET_KEY_FILE: /run/secrets/api_secret_key
      ADMIN_API_KEY_FILE: /run/secrets/admin_api_key
```
