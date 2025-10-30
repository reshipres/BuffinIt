"""
Простой скрипт для запуска бота с установленным токеном.
Запускайте этот файл вместо bot.py

ВАЖНО: Замените 'YOUR_BOT_TOKEN_HERE' на ваш токен бота
"""

import os
import sys

# Устанавливаем токен нового бота
# Получить токен можно у @BotFather в Telegram
os.environ["BOT_TOKEN"] = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Запускаем основной файл бота
if __name__ == "__main__":
    if os.environ["BOT_TOKEN"] == "YOUR_BOT_TOKEN_HERE":
        print("=" * 60)
        print("  ⚠️  ОШИБКА: Токен не установлен!")
        print("=" * 60)
        print()
        print("Откройте файл start_bot.py и замените")
        print("'YOUR_BOT_TOKEN_HERE' на ваш токен бота")
        print()
        print("Или установите переменную окружения BOT_TOKEN:")
        print("set BOT_TOKEN=ваш_токен")
        print()
        input("Нажмите Enter для выхода...")
        sys.exit(1)
    
    print("=" * 60)
    print("  ЗАПУСК BUFF PAY BOT")
    print("=" * 60)
    print(f"Токен установлен: {os.environ['BOT_TOKEN'][:20]}...")
    print()
    
    # Импортируем и запускаем бота
    import bot

