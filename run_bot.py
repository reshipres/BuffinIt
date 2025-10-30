#!/usr/bin/env python3
"""
Быстрый запуск бота BUFF Pay

Этот скрипт запускает бота с BOT_TOKEN из переменной окружения или из параметра.
Токен ДОЛЖЕН быть установлен ДО импорта модулей!
"""

import os
import sys

# === ЭТАП 1: Устанавливаем BOT_TOKEN в переменную окружения ===
# Это ДОЛЖНО быть ДО импорта bot.py и config.py!

BOT_TOKEN = None

# Проверяем аргументы командной строки
if len(sys.argv) > 1:
    BOT_TOKEN = sys.argv[1]
    print(f"✅ BOT_TOKEN получен из аргумента")
else:
    # Проверяем переменную окружения
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if BOT_TOKEN:
        print(f"✅ BOT_TOKEN получен из переменной окружения")

# Если токен есть - устанавливаем его в окружение
if BOT_TOKEN:
    os.environ["BOT_TOKEN"] = BOT_TOKEN
else:
    print("❌ BOT_TOKEN не найден!")
    print("\nИспользование:")
    print("  python run_bot.py <BOT_TOKEN>")
    print("\nПример:")
    print("  python run_bot.py 7528975289:AAE9yRfmq2pYiJjI3WVkE-eMj9_vl1u8_cM")
    sys.exit(1)

# === ЭТАП 2: ТЕПЕРЬ импортируем bot (токен уже установлен!) ===
print("\n🚀 Запускаю бота...")
print("-" * 60)
print()

try:
    import asyncio
    from bot import main
    
    # Запускаем основную функцию
    asyncio.run(main())
    
except KeyboardInterrupt:
    print("\n\n⚠️  Бот остановлен (Ctrl+C)")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ ОШИБКА при запуске бота:")
    print(f"   {type(e).__name__}: {e}")
    import traceback
    print("\nПолный стек ошибки:")
    traceback.print_exc()
    sys.exit(1)
