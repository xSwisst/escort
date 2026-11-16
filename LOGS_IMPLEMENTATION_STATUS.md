# Logs System Implementation Status

## Overview
Logs service реализует отправку логов событий в Telegram форум с автоматическим управлением тредами.

## Architecture

### Key Components

1. **LogThread Model** (`api/models/log_threads.py`)
   - Хранит маппинг типов логов на ID тредов Telegram форума
   - 14 типов тредов (LogThreadType enum)
   - Автоматическое управление created_at/updated_at

2. **ThreadManager** (`logs/services/thread_manager.py`)
   - 3-уровневое кеширование: память → БД → создание
   - Автоматическое создание отсутствующих тредов
   - Поддержка холодного старта через `recreate_all_threads()`

3. **Event Mapping** (`logs/services/event_mapping.py`)
   - Маппинг имени события на тип треда
   - 18 событий → 14 тредов
   - Фоллбек на CLIENT_SUPPORT_MESSAGES для неизвестных событий

4. **TelegramLogSender** (`logs/services/telegram/sender.py`)
   - Отправка сообщений в правильный тред
   - Автоматическое создание тредов при необходимости

5. **API Endpoints** (`logs/api/routes/v1/threads.py`)
   - `POST /v1/threads/recreate` - Пересоздать все треды (холодный старт)
   - `GET /v1/threads` - Список всех тредов из БД

## Thread Types (14 total)

| Thread Type | Emoji | Display Name | Events |
|-------------|-------|--------------|--------|
| `client_registration` | 👤 | Регистрации клиентов | new_user |
| `client_cities` | 🏙️ | Города клиентов | add_city, change_of_city |
| `client_addresses` | 📍 | Адреса клиентов | add_address, remove_address |
| `client_support_section` | 💬 | Раздел поддержки | open_support_section |
| `client_support_messages` | ✉️ | Сообщения в поддержку | message_to_support |
| `payment_requests` | 📋 | Заявки на пополнение | payment_request |
| `payment_checks` | 💳 | Чеки | get_check_of_top_up, get_check_of_payment_private_channel, get_check_of_payment_model |
| `orders` | 🛎️ | Оформления | new_order |
| `forms_views` | 👁️ | Открытие анкет | open_model_form |
| `forms_management` | 📝 | Анкеты | new_form |
| `promocode_created` | 🎁 | Создание промокодов | promocode_created |
| `promocode_activated` | ✅ | Активация промокодов | promocode_activated |
| `reviews` | ⭐ | Отзывы | new_review |
| `mailing` | 📢 | Рассылка | mailing |

## Flow

### Normal Flow (Thread Exists)
```
Event → get_thread_type_for_event() → ThreadManager.get_thread_id()
  ↓
Check cache → Found → Return thread_id
  ↓
Format message → Send to thread
```

### Thread Creation Flow (First Time)
```
Event → get_thread_type_for_event() → ThreadManager.get_thread_id()
  ↓
Check cache → Not found
  ↓
Check DB → Not found
  ↓
Create via Telegram API
  ↓
Save to DB → Cache → Return thread_id
  ↓
Format message → Send to thread
```

### Cold Start Flow
```
POST /v1/threads/recreate
  ↓
Clear cache and DB
  ↓
For each thread type:
  - Create via Telegram API
  - Save to DB
  - Cache
  ↓
Return all thread_id mappings
```

## Database Schema

### log_threads table
```sql
CREATE TABLE log_threads (
    id SERIAL PRIMARY KEY,
    thread_type VARCHAR(50) UNIQUE NOT NULL,
    thread_id INTEGER NOT NULL,
    thread_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE UNIQUE INDEX ix_log_threads_thread_type ON log_threads(thread_type);
```

## Message Templates

All message templates are in `logs/assets/texts/messages.yaml`:
- Используют HTML formatting (Telegram parse_mode)
- Структура: blockquote для заголовков, bold/code для данных
- Плейсхолдеры в формате `{field_name}`

## API Integration

### Logs Service
- Base URL: из `settings.LOGS_TELEGRAM_API_BASE_URL`
- Bot token: из `settings.LOGS_BOT_TOKEN`
- Chat ID: из `settings.LOGS_CHAT_ID`
- Parse mode: из `settings.LOGS_PARSE_MODE`

### Endpoints Used
- `POST /bot{token}/createForumTopic` - создание треда
- `POST /bot{token}/sendMessage` - отправка сообщения в тред

## Dependencies

### Database
- AsyncSession injection через `get_database()` dependency
- Connection pool management через `async_session_maker`

### HTTP Client
- `httpx.AsyncClient` для Telegram API
- Timeout из `settings.LOGS_TIMEOUT_SEC`

## Security

### Service Authentication
- Все thread endpoints защищены `service_auth` dependency
- Только сервисы могут пересоздавать треды

## Migration

### Status
✅ Migration created: `002_add_log_threads_table.py`
- Revision: `002_add_log_threads`
- Depends on: `001_decompose_forms`

### To Apply
```bash
cd /home/name/Desktop/escort/new_escort/api
alembic upgrade head
```

## Implementation Status

### ✅ Completed
1. LogThread model with 14 thread types
2. ThreadManager with 3-level caching
3. Event mapping for 18 events
4. TelegramLogSender integration
5. API endpoints for thread management
6. Message templates for all events (promocode_created, promocode_activated included)
7. Database session injection
8. Alembic migration

### ⏳ Pending (Next Prompt)
**User explicitly requested to postpone:**
> "Пока что логи, именно функциональность этих логов не подключай, подключим их следующим промтом"

Connection of log emission from services:
- **Main service**: new_user, add_city, change_of_city, add_address, remove_address, open_model_form, new_order, payment_request, get_check_of_top_up, get_check_of_payment_model, get_check_of_payment_private_channel, new_review
- **Support service**: message_to_support, open_support_section  
- **Admin service**: new_form, promocode_created, promocode_activated, mailing

## Design Principles

1. **Fault Tolerance**: Логи никогда не теряются - если тред не существует, он создается автоматически
2. **Performance**: 3-уровневое кеширование минимизирует обращения к БД и API
3. **Idempotency**: Можно безопасно вызывать `recreate_all_threads()` несколько раз
4. **Type Safety**: Enum для типов тредов предотвращает опечатки
5. **Separation of Concerns**: Разделение маппинга, форматирования и отправки

## Error Handling

- `httpx` exceptions пробрасываются наверх
- Telegram API errors возвращают RuntimeError с деталями
- DB errors обрабатываются на уровне SQLAlchemy

## Notes

- Треды создаются в Telegram форуме автоматически при первом использовании
- При очистке форума необходимо вызвать `POST /v1/threads/recreate`
- Cache очищается только при `recreate_all_threads()` - живет на протяжении жизни процесса
- Fallback для неизвестных событий: `CLIENT_SUPPORT_MESSAGES`
