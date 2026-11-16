# Web App Migration Analysis: Old vs New

## Executive Summary

**Completeness: ~15%**

Новое веб-приложение реализует только базовый скелет. **85% функциональности отсутствует**, включая критичную систему бронирования, без которой пользователи не могут совершить основное действие, ради которого существует приложение.

---

## 🔴 КРИТИЧНЫЕ ОТСУТСТВУЮЩИЕ ФУНКЦИИ

### 1. ❌ Система бронирования (ПОЛНОСТЬЮ ОТСУТСТВУЕТ)

Старое приложение: 7-шаговый процесс бронирования с 50+ компонентами
Новое приложение: **НИЧЕГО**

**Отсутствующие шаги:**
1. **Выбор даты/времени** - колёса выбора с раскрывающимися списками
2. **Выбор места** - у модели / у клиента
3. **Управление адресами** - список, создание, выбор адреса
4. **Выбор тарифа** - 1ч/2ч/3ч/ночь с отображением цен
5. **Дополнительные услуги** - чекбоксы с ценами и подсчётом
6. **Способ оплаты** - карта/наличные с валидацией (наличные >3 заказов)
7. **Подтверждение оплаты** - реквизиты карты, интеграция с поддержкой

**Бизнес-импакт:** Пользователи НЕ МОГУТ заказать модель. Это основная функция приложения.

### 2. ❌ City Gate & City Switcher (ПОЛНОСТЬЮ ОТСУТСТВУЕТ)

**Старое приложение:**
- City gate блокирует доступ к моделям до выбора города
- 2 слота для городов (можно сохранить и переключаться между двумя городами)
- Bottom sheet с переключателем городов
- Валидация города на бэкенде
- Анимированные переходы

**Новое приложение:** ❌ Нет ни city gate, ни переключателя

**Бизнес-импакт:** Нет географической фильтрации моделей

### 3. ❌ Hero Carousel (ПОЛНОСТЬЮ ОТСУТСТВУЕТ)

**Старое приложение:**
- Автоматическая карусель баннеров с 4+ изображениями
- Drag-to-navigate с momentum
- Бесконечный луп (3x повторение)
- Автопроигрывание каждые 3 секунды
- Плавные переходы 900ms

**Новое приложение:** ❌ Нет баннеров вообще

**Бизнес-импакт:** Нет промо-контента, нет визуального выделения акций

---

## 🟡 ВЫСОКОПРИОРИТЕТНЫЕ ОТСУТСТВУЮЩИЕ ФУНКЦИИ

### 4. ❌ Model Sheet (Bottom Sheet) - Заменён на статичную страницу

**Старое приложение:**
- Bottom sheet с drag-to-dismiss жестом
- Свайпаемая галерея фото с стрелками и точками
- Расширяемая высота (потянуть вверх → раскрыть полностью)
- Эластичное сопротивление при перетаскивании
- Плавный backdrop с blur 0→16px
- Бронирование встроено внутрь sheet

**Новое приложение:** Отдельная страница без жестов

**UX импакт:** Менее плавное взаимодействие, требует навигации назад

### 5. ❌ Поиск и сортировка

**Старое приложение:**
- Поиск в реальном времени по имени модели
- Bottom sheet с 5 опциями сортировки:
  - По новизне
  - Цена: низкая → высокая
  - Цена: высокая → низкая
  - Рейтинг: низкий → высокий  
  - Рейтинг: высокий → низкий

**Новое приложение:** ❌ Нет поиска, нет сортировки

### 6. ❌ Табы "Все" / "Избранное"

**Старое приложение:**
- 2 визуальных таба с активным состоянием
- Slide transitions (slide-left/slide-right)
- URL синхронизация с ?section=favorites

**Новое приложение:** Только чекбокс без визуального разделения

### 7. ❌ Все 26 иконок

**Старое приложение:** Кастомные SVG иконки для всего UI
**Новое приложение:** ❌ НЕТ папки assets вообще

Отсутствующие иконки:
- `eye-slash.svg` - пустое состояние моделей
- `heart-xmark.svg` - пустое состояние избранного
- `heart.svg`, `heart-crack.svg` - избранное активное/неактивное
- `shield-heart.svg` - health badge
- `true.svg` - verification badge
- `filter.svg`, `sort.svg`, `search.svg` - инструменты
- `telegram.svg` - ссылки на Telegram
- `clock.svg`, `geo.svg`, `message.svg` - профиль и поддержка
- И ещё 15 иконок

### 8. ❌ Бейджи верификации и медсправки

**Старое приложение:**
- Бейдж "Проверено" с галочкой
- Бейдж "Медсправка" с щитом
- Отображаются поверх фото модели

**Новое приложение:** ❌ Нет

---

## 🟢 СРЕДНЕПРИОРИТЕТНЫЕ ОТСУТСТВУЮЩИЕ ФУНКЦИИ

### 9. ❌ Анимации избранного

**Старое приложение:**
- Jello animation (560ms) при добавлении
- Shake animation (220ms) при удалении
- Exit ghost элементы при удалении из раздела "Избранное"
- FLIP animations для сдвига оставшихся карточек
- Optimistic updates с откатом при ошибке

**Новое приложение:** Простой toggle без анимаций

### 10. ❌ Onboarding система

**Старое приложение:**
- Модальное окно с TGS/Lottie анимациями
- TgsPlayer компонент
- Показывается при первом запуске

**Новое приложение:** ❌ Нет

### 11. ❌ FAQ система (AboutPage)

**Старое приложение:**
- Поиск по FAQ в реальном времени
- Accordion items с плавными раскрытиями
- Несколько секций
- Tab carousel с бесконечным листанием
- Пустое состояние при нулевых результатах поиска

**Новое приложение:** Только список простых ссылок

### 12. ❌ ElasticScrollArea

**Старое приложение:**
- Кастомный scroll компонент
- Предотвращает overscroll bounce
- Touch event handling для iOS-стайл эластичности
- Scroll direction detection
- Интеграция с кнопкой scroll-to-top

**Новое приложение:** ❌ Нет

### 13. ❌ Scroll-to-top кнопка

**Старое приложение:**
- Появляется при скролле вниз
- Скрывает bottom nav при скролле
- Плавная анимация скролла
- Glassmorphism стилизация

**Новое приложение:** ❌ Нет

---

## 📊 ДЕТАЛЬНОЕ СРАВНЕНИЕ ПО СТРАНИЦАМ

### ModelsPage

| Функция | Старое | Новое | Статус |
|---------|--------|-------|--------|
| Строк кода | 3,134 | 108 | ❌ 97% отсутствует |
| Hero carousel | ✅ | ❌ | **ОТСУТСТВУЕТ** |
| City gate | ✅ | ❌ | **ОТСУТСТВУЕТ** |
| City switcher | ✅ | ❌ | **ОТСУТСТВУЕТ** |
| Поиск | ✅ | ❌ | **ОТСУТСТВУЕТ** |
| Табы All/Favorites | ✅ | ❌ Чекбокс | **ОТСУТСТВУЕТ** |
| Сортировка | ✅ | ❌ | **ОТСУТСТВУЕТ** |
| Фильтр | ✅ | ❌ | **ОТСУТСТВУЕТ** |
| Карточки моделей | ✅ Сложные | ✅ Базовые | **ЧАСТИЧНО** |
| Бейджи | ✅ | ❌ | **ОТСУТСТВУЕТ** |
| Анимации избранного | ✅ | ❌ | **ОТСУТСТВУЕТ** |
| Exit ghosts | ✅ FLIP | ❌ | **ОТСУТСТВУЕТ** |
| Model sheet | ✅ Bottom sheet | ❌ | **ОТСУТСТВУЕТ** |
| Галерея фото | ✅ Swipeable | ❌ | **ОТСУТСТВУЕТ** |
| Бронирование | ✅ 7 шагов | ❌ | **ОТСУТСТВУЕТ** |

### ProfilePage

| Функция | Старое | Новое | Статус |
|---------|--------|-------|--------|
| Layout | Grid с sheets | Простые карточки | **УПРОЩЁН** |
| Метрики | ✅ Glass cards | ✅ Stats | **ЧАСТИЧНО** |
| City slots | ✅ 2 города | ✅ Базово | **ОТСУТСТВУЕТ ФИЧА** |
| History sheet | ✅ Bottom sheet | ❌ Inline | **ОТСУТСТВУЕТ** |
| Promo sheet | ✅ Bottom sheet | ✅ Inline | **ОТСУТСТВУЕТ** |
| Addresses sheet | ✅ Bottom sheet | ✅ Inline | **ОТСУТСТВУЕТ** |
| Анимации sheet | ✅ Drag/transition | ❌ | **ОТСУТСТВУЕТ** |
| Order status labels | ✅ Переведены | ❌ Raw | **ОТСУТСТВУЕТ** |

### SupportPage

| Функция | Старое | Новое | Статус |
|---------|--------|-------|--------|
| Контакты | ✅ С иконками | ✅ Базово | **ЧАСТИЧНО** |
| FAQ | ✅ Accordion | ❌ | **ОТСУТСТВУЕТ** |
| Адрес агентства | ✅ | ❌ | **ОТСУТСТВУЕТ** |
| Часы работы | ✅ | ❌ | **ОТСУТСТВУЕТ** |
| Иконки | ✅ MaskedIcon | ❌ | **ОТСУТСТВУЕТ** |

### AboutPage

| Функция | Старое | Новое | Статус |
|---------|--------|-------|--------|
| Структура | FAQ система | Простые ссылки | **ПОЛНОСТЬЮ ДРУГОЕ** |
| Поиск | ✅ | ❌ | **ОТСУТСТВУЕТ** |
| Tab carousel | ✅ | ❌ | **ОТСУТСТВУЕТ** |
| FAQ sections | ✅ | ❌ | **ОТСУТСТВУЕТ** |
| Accordion | ✅ | ❌ | **ОТСУТСТВУЕТ** |

---

## 🎨 СТИЛИ И АНИМАЦИИ

### Отсутствующие анимации:

1. **Favorite Icon Animations:**
   - Jello при добавлении: 560ms spring
   - Shake при удалении: 220ms shake
   - Переходы состояний иконок

2. **Favorite Exit Ghost:**
   - Ghost элемент с точным позиционированием
   - 420ms fade-out и scale
   - FLIP layout animations для оставшихся элементов

3. **Section Slide Transitions:**
   - Slide-left при переходе к избранному
   - Slide-right при возврате ко всем моделям

4. **Sheet Transitions:**
   - 420ms cubic-bezier(0.16, 1, 0.3, 1)
   - Backdrop blur 0 → 16px
   - Backdrop opacity 0.1 → 0.26
   - Sheet translateY animations

5. **Hero Carousel:**
   - 900ms slide transitions
   - 3000ms авто-проигрывание
   - Drag жесты с momentum

6. **Nav Icon Jello:**
   - 560ms jello при нажатии таба
   - Применяется к bottom nav и profile кнопке

### Отсутствующие glassmorphism классы:

- `glass-block-soft` - основные блоки
- `glass-accent-blue` - акцентные элементы
- `glass-block-muted` - приглушённые блоки
- `glass-chip` - чипсы
- `glass-chip-success` - успешные чипсы

---

## 📦 КОМПОНЕНТЫ

### Полностью отсутствующие сложные компоненты:

1. **Bottom Sheets** (draggable)
   - Drag handle
   - Pointer capture
   - Elastic resistance
   - Progressive backdrop blur
   - Height calculation и expansion

2. **ElasticScrollArea**
   - Предотвращение overscroll
   - Touch event handling
   - Scroll direction detection

3. **PromoCardsCarousel** (370 строк)
   - Infinite loop
   - Auto-play с паузой
   - Drag gestures
   - Visibility state management

4. **FaqAccordionItem**
   - Collapsible items
   - Smooth animations
   - Search integration

5. **TgsPlayer**
   - Lottie/TGS анимации
   - Size control
   - Loop management

6. **MaskedIcon**
   - SVG иконки с mask-image CSS
   - Используется по всему приложению

---

## 📝 КОНТЕНТ (YAML)

### Старое приложение: 6 YAML файлов

1. `appShellContent.yaml`
2. `modelsPageContent.yaml` - **93 лейбла**
3. `profilePageContent.yaml` - **47 лейблов**
4. `supportPageContent.yaml`
5. `aboutPageContent.yaml`
6. `systemPageContent.yaml`

### Новое приложение: 1 YAML файл

- `app.yaml` - всё в одном файле, **минимальное количество лейблов**

### Отсутствующие лейблы из modelsPageContent.yaml (93 шт):

**City gate (7):** title, description, placeholder, submit, loading, error, notFound
**City switcher (11):** menu title, selected prefix, add labels, back, close, etc.
**Booking (50+):** все 7 шагов со всеми лейблами
**Sort (7):** latest, priceAsc, priceDesc, ratingAsc, ratingDesc, close, done
**Badges (2):** verification, health
**Empty states (2):** emptyModels, emptyFavorites

---

## 🗂️ ASSETS

### Отсутствующие иконки (26 шт):

```
/assets/icons/
├── about.svg
├── at.svg
├── butterfly.svg
├── clock.svg
├── disount.svg
├── doc.svg
├── eye-slash.svg ⭐ (empty models state)
├── filter.svg ⭐
├── geo.svg
├── geo-home.svg
├── heart.svg ⭐
├── heart-crack.svg ⭐
├── heart-xmark.svg ⭐ (empty favorites state)
├── history.svg
├── message.svg
├── question.svg
├── saved.svg
├── search.svg ⭐
├── shield-heart.svg ⭐ (health badge)
├── sort.svg ⭐
├── telegram.svg ⭐
└── true.svg ⭐ (verification badge)
```

⭐ = критично важные для UI

### Отсутствующие баннеры:

```
/assets/banners/
├── banner-1.{avif,webp,jpg}
├── banner-2.{avif,webp,jpg}
├── banner-3.{avif,webp,jpg}
└── banner-4.{avif,webp,jpg}
```

Новое приложение: **НЕТ папки /assets вообще**

---

## 🔧 API ИНТЕГРАЦИЯ

### Отсутствующие API функции:

1. `markModelOpened(token, code)` - трекинг просмотра модели
2. `prepareModelBooking(token, code, body)` - подготовка бронирования
3. `resolveModelBookingPayment(token, orderNumber, method)` - резолв оплаты

### Отсутствующие query паттерны:

- Prefetch при hover/scroll (до 6 моделей)
- Stale times: PROFILE (5min), MODELS (2min), MODEL_DETAILS (10min), SUPPORT (30min)
- Query invalidation chains при смене города

---

## ⚙️ STATE MANAGEMENT

### Отсутствующая логика состояния:

1. **Optimistic Updates** - избранное с откатом при ошибке
2. **Query Invalidation** - сложные цепочки инвалидации
3. **Booking State Machine** - многошаговый flow с сохранением состояния
4. **Sheet State** - open/close/dragging/height
5. **Carousel State** - activeIndex, dragOffset, transitionVersion, visibility
6. **Scroll State** - direction detection, scroll-to-top visibility
7. **City State** - activeSlot, pendingCity, validation
8. **Favorite Animation State** - jello/shake timings, exit ghosts, layout ready

---

## 🚀 BOOTSTRAP

### Старое приложение:
- `useBootstrap.ts` - отдельный hook
- `useTelegramWebAppRuntime.ts` - инициализация Telegram runtime
- Error boundary integration

### Новое приложение:
- Простой inline bootstrap в App.tsx
- Нет отдельных hooks
- Нет Telegram runtime обработки

---

## 📋 ПРИОРИТЕТЫ МИГРАЦИИ

### 🔴 Критично (без этого приложение НЕ ФУНКЦИОНАЛЬНО):

1. **Booking система** - вся целиком (7 шагов, 50+ компонентов, 1500+ строк)
2. **City gate & switcher** - блокирует доступ без выбора города
3. **Hero carousel** - промо-контент
4. **Все иконки** - 26 SVG файлов
5. **Бейджи** - verification, health

### 🟡 Высокий приоритет (UX страдает):

6. **Model bottom sheet** - вместо отдельной страницы
7. **Поиск** - поиск по моделям
8. **Сортировка** - 5 опций сортировки
9. **Табы All/Favorites** - визуальные табы вместо чекбокса
10. **Галерея фото** - swipeable вместо одного фото

### 🟢 Средний приоритет (полировка):

11. **Анимации избранного** - jello/shake/exit ghosts
12. **FAQ система** - AboutPage с поиском и accordion
13. **Onboarding** - модальное окно для новых пользователей
14. **ElasticScrollArea** - плавный скролл
15. **Scroll-to-top** - кнопка прокрутки наверх

---

## 💰 ОЦЕНКА РАБОТЫ

### Объём кода для портирования:

- **ModelsPage:** 3,134 строки → 108 строк = **3,026 строк отсутствует**
- **Booking flow:** ~1,500 строк
- **Bottom sheets:** ~800 строк
- **Animations & transitions:** ~400 строк
- **Carousels:** ~500 строк
- **FAQ система:** ~300 строк
- **Компоненты:** ~600 строк

**Итого: ~7,000+ строк кода нужно портировать**

### Время разработки (примерная оценка):

- Booking система: **2-3 недели** (сложная логика, много состояний)
- City management: **3-5 дней**
- Hero carousel: **2-3 дня**
- Bottom sheets: **1 неделя** (сложные жесты и анимации)
- Поиск/сортировка: **2-3 дня**
- Иконки и assets: **1-2 дня** (копирование + интеграция)
- Анимации избранного: **3-5 дней**
- FAQ система: **1 неделя**
- Onboarding: **3-5 дней**
- Остальные компоненты: **1 неделя**

**Итого: 6-8 недель разработки** для достижения полного паритета функций

---

## ⚠️ ВЫВОД

Новое приложение реализует только **~15% функциональности** старого приложения.

**Критичная проблема:** Отсутствует система бронирования - пользователи **НЕ МОГУТ заказать модель**. Это основная функция приложения.

**Рекомендация:** Необходима полная миграция всех компонентов, логики и стилей из старого приложения в новое, с приоритетом на booking систему.
