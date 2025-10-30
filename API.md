# 🔌 API и структура BUFF Pay Bot

Документация для разработчиков — как работает бот изнутри и как его расширять.

---

## 📊 Архитектура

```
┌─────────────────────────────────────────────┐
│          Telegram Bot API                   │
│       (Сервера Telegram)                    │
└──────────────┬──────────────────────────────┘
               │
               ▼
        ┌─────────────┐
        │   bot.py    │  ◄─── Основной файл (polling)
        └──────┬──────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
   handlers/      config.py
  (команды)   (настройки)
   │
   ├── start.py       (команда /start)
   ├── requests.py    (сбор заявок)
   └── support.py     (поддержка)

Данные потока: User → Bot → Manager
```

---

## 🔄 Поток выполнения

### 1️⃣ Инициализация (bot.py)

```python
# 1. Загружаем конфиг
from config import BOT_TOKEN

# 2. Создаём бота
bot = Bot(token=BOT_TOKEN)

# 3. Создаём хранилище состояния (FSM)
storage = MemoryStorage()

# 4. Создаём диспетчер
dp = Dispatcher(storage=storage)

# 5. Регистрируем обработчики
dp.message.register(start.start_command, F.command("start"))

# 6. Запускаем поллинг
await dp.start_polling(bot)
```

### 2️⃣ Получение сообщения

```
User пишет сообщение
         ↓
Telegram API отправляет в бота
         ↓
Диспетчер (Dispatcher) получает обновление
         ↓
Ищет подходящий обработчик
         ↓
Вызывает обработчик с контекстом
         ↓
Обработчик отправляет ответ
```

### 3️⃣ Сбор заявки (FSM)

```
/start
  ↓
Пользователь нажимает "Оформить заявку"
  ↓
Бот переводит в состояние: waiting_for_link
  ↓
Пользователь отправляет ссылку
  ↓
Бот сохраняет ссылку, переводит в: waiting_for_amount
  ↓
Пользователь отправляет сумму
  ↓
Бот отправляет уведомление менеджеру
  ↓
Бот очищает состояние
```

---

## 🔌 Основные компоненты

### `bot.py` — Главный файл

```python
# Инициализирует и запускает бота

async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация обработчиков
    dp.message.register(start.start_command, F.command("start"))
    
    # Запуск
    await dp.start_polling(bot)
```

**Ключевые классы:**
- `Bot` — клиент для общения с Telegram API
- `Dispatcher` — маршрутизирует обновления к обработчикам
- `MemoryStorage` — хранит состояние пользователей в памяти

---

### `config.py` — Конфигурация

```python
# Загружает переменные окружения из .env

from dotenv import load_dotenv

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_ID = os.getenv("MANAGER_ID")
MANAGER_USERNAME = os.getenv("MANAGER_USERNAME")
```

**Используется:**
- В `bot.py` для инициализации бота
- В `handlers/requests.py` для отправки уведомлений

---

### `handlers/start.py` — Навигация

**Функции:**

| Функция | Описание |
|---------|---------|
| `start_command()` | Команда `/start`, показывает главное меню |
| `button_how_it_works()` | Нажатие кнопки "Как это работает" |
| `button_support()` | Нажатие кнопки "Поддержка" |
| `button_back_to_start()` | Возврат в главное меню |

**Пример:**

```python
async def start_command(message: types.Message):
    """Обработчик команды /start"""
    
    # Текст сообщения
    text = "💎 BUFF Pay — покупай скины дешевле"
    
    # Создаём клавиатуру
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🧾 Оформить заявку", callback_data="request")
    keyboard.button(text="❓ Как это работает", callback_data="how_it_works")
    keyboard.adjust(1)  # Одна кнопка в ряд
    
    # Отправляем сообщение
    await message.answer(text, reply_markup=keyboard.as_markup())
```

---

### `handlers/requests.py` — Сбор заявок

**Состояния (FSM):**

```python
class RequestStates(StatesGroup):
    waiting_for_link = State()      # Ждём ссылку
    waiting_for_amount = State()    # Ждём сумму
```

**Функции:**

| Функция | Описание |
|---------|---------|
| `button_request()` | Инициирует процесс заявки |
| `collect_request_data()` | Собирает ссылку и сумму (2 этапа) |
| `send_notification_to_manager()` | Отправляет уведомление менеджеру |

**Пример FSM:**

```python
async def button_request(callback, state):
    # Переводим в состояние ожидания ссылки
    await state.set_state(RequestStates.waiting_for_link)
    await callback.message.edit_text("Отправь ссылку на товар:")

async def collect_request_data(message, state):
    current_state = await state.get_state()
    
    if current_state == RequestStates.waiting_for_link:
        # Сохраняем ссылку
        await state.update_data(link=message.text)
        
        # Переходим на следующий этап
        await state.set_state(RequestStates.waiting_for_amount)
        await message.answer("Теперь пришли сумму:")
    
    elif current_state == RequestStates.waiting_for_amount:
        # Получаем сохранённую ссылку
        data = await state.get_data()
        link = data.get("link")
        amount = message.text
        
        # Очищаем состояние
        await state.clear()
        
        # Отправляем уведомление менеджеру
        await send_notification_to_manager(message.from_user.id, link, amount)
```

---

## 📝 Типы обработчиков

### Message Handler (сообщения)

```python
# Обработчик команды
dp.message.register(handler, F.command("start"))

# Обработчик текста
dp.message.register(handler, F.text)

# Обработчик с фильтром
dp.message.register(handler, F.text.contains("hello"))
```

### CallbackQuery Handler (нажатия кнопок)

```python
# Обработчик кнопки
dp.callback_query.register(handler, F.data == "request")

# Обработчик с фильтром
dp.callback_query.register(handler, F.data.startswith("item_"))
```

---

## 🔐 Безопасность

### Текущая реализация

✅ **Что сделано:**
- Конфиг в `.env` (не в коде)
- FSM состояния хранятся в памяти (не в БД)
- Нет валидации (как просили)
- Логирование событий

❌ **Что отсутствует:**
- Валидация ссылок
- Сохранение в БД
- Ограничение по rate limit
- Двухфакторная верификация

### Рекомендации

Если планируете использовать в production:

```python
# 1. Добавить валидацию ссылок
import re
def validate_buff_url(url):
    if not re.match(r"^https://buff\.163\.com/.*", url):
        raise ValueError("Invalid BUFF URL")

# 2. Добавить БД
from sqlalchemy import create_engine
engine = create_engine("sqlite:///buff_bot.db")

# 3. Добавить rate limiting
from slowapi import Limiter

# 4. Логировать в файл
logging.FileHandler("bot.log")
```

---

## 🛠️ Как расширять бота

### Добавить новую команду

```python
# 1. Создать обработчик в handlers/my_handler.py
async def my_command(message: types.Message):
    await message.answer("Hello!")

# 2. Зарегистрировать в bot.py
from handlers import my_handler
dp.message.register(my_handler.my_command, F.command("mycommand"))
```

### Добавить новую кнопку

```python
# 1. Добавить кнопку в handlers/start.py
keyboard.button(text="📊 Статистика", callback_data="stats")

# 2. Создать обработчик
async def button_stats(callback: types.CallbackQuery):
    await callback.message.edit_text("Статистика заявок: 42")

# 3. Зарегистрировать в bot.py
dp.callback_query.register(start.button_stats, F.data == "stats")
```

### Добавить сохранение в БД

```python
import aiosqlite

# 1. Создать таблицу
async def init_db():
    async with aiosqlite.connect("buff_bot.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                link TEXT,
                amount REAL,
                created_at TIMESTAMP
            )
        """)
        await db.commit()

# 2. Сохранять данные
async def save_request(user_id, link, amount):
    async with aiosqlite.connect("buff_bot.db") as db:
        await db.execute(
            "INSERT INTO requests (user_id, link, amount) VALUES (?, ?, ?)",
            (user_id, link, amount)
        )
        await db.commit()
```

---

## 📚 Ссылки

- **aiogram документация**: https://docs.aiogram.dev/
- **Telegram Bot API**: https://core.telegram.org/bots/api
- **Python asyncio**: https://docs.python.org/3/library/asyncio.html

---

## 💡 Советы

1. **Используйте логирование** для отладки
   ```python
   logger.info("✅ Заявка создана")
   logger.error("❌ Ошибка:", exc_info=True)
   ```

2. **Проверяйте состояния** перед обработкой
   ```python
   if await state.get_state() is None:
       return
   ```

3. **Ловите исключения** при работе с API
   ```python
   try:
       await bot.send_message(...)
   except Exception as e:
       logger.error(f"Ошибка отправки: {e}")
   ```

4. **Используйте type hints** для чистоты кода
   ```python
   async def handler(message: types.Message) -> None:
       pass
   ```

---

**Удачи в разработке! 🚀**


