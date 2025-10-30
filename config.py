"""
Конфигурация бота BUFF Pay.

Загружает токен бота из переменных окружения.
MANAGER_ID - опциональный параметр для отправки уведомлений.
"""

import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла (если он есть)
load_dotenv()

# Токен Telegram-бота (получить у BotFather)
# Установлен через переменную окружения перед импортом
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ID менеджера для получения уведомлений (опционально)
MANAGER_ID = os.getenv("MANAGER_ID")

# Username менеджера для отправки пользователю (опционально)
MANAGER_USERNAME = os.getenv("MANAGER_USERNAME", "BuffinItMNG")

# Канал для обязательной подписки
# Формат: @BuffinIt (без https://t.me/)
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", "@BuffinIt")
# ID канала (можно получить через бота или API)
# Для публичных каналов формат: @username
REQUIRED_CHANNEL_ID = os.getenv("REQUIRED_CHANNEL_ID", "@BuffinIt")

# Если MANAGER_ID не установлен, работаем без отправки менеджеру
if not MANAGER_ID:
    print("⚠️  MANAGER_ID не установлен. Уведомления менеджеру не будут отправляться.")
