"""
Основной файл бота BUFF Pay.

Инициализирует бота, регистрирует обработчики и запускает polling.
"""

import asyncio
import logging
from aiogram import Dispatcher, Router, F, Bot, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

from config import BOT_TOKEN
from handlers import start, requests, admin, subscription

# Настройка логирования для отладки
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Проверяем что токен установлен
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN не установлен!")
    raise ValueError("BOT_TOKEN не найден в переменных окружения")


async def main():
    """
    Основная функция запуска бота.
    
    Инициализирует диспетчер, регистрирует все обработчики
    и запускает долгий поллинг для получения обновлений.
    """
    
    logger.info("=" * 60)
    logger.info("🚀 Инициализирую бота...")
    logger.info("=" * 60)
    
    # Создаём экземпляр бота с параметрами
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Получаем информацию о боте
    bot_info = await bot.get_me()
    logger.info(f"✅ Бот подключен: @{bot_info.username} (ID: {bot_info.id})")
    
    # Используем MemoryStorage для хранения состояния пользователей
    storage = MemoryStorage()
    
    # Создаём диспетчер (он управляет обработчиками)
    dp = Dispatcher(storage=storage)
    
    # Создаём Router для обработчиков
    router = Router()
    
    logger.info("📝 Регистрирую обработчики...")
    
    # === СООБЩЕНИЯ (MESSAGE HANDLERS) ===
    
    # Команда /start
    router.message.register(
        start.start_command,
        Command("start")
    )
    logger.info("✅ Обработчик /start зарегистрирован")
    
    # Команда /admin (админ-панель)
    router.message.register(
        admin.admin_command,
        Command("admin")
    )
    logger.info("✅ Обработчик /admin зарегистрирован")
    
    # Сбор данных заявки
    router.message.register(requests.collect_request_data)
    logger.info("✅ Обработчик сбора данных зарегистрирован")
    
    # === CALLBACK (КНОПКИ) ===
    
    # Проверка подписки на канал
    router.callback_query.register(
        subscription.button_check_subscription,
        F.data == "check_subscription"
    )
    logger.info("✅ Обработчик 'Проверка подписки' зарегистрирован")
    
    # Регистрация через Steam
    router.callback_query.register(
        start.button_register,
        F.data == "register"
    )
    logger.info("✅ Обработчик 'Регистрация' зарегистрирован")
    
    # Гайд по ссылке
    router.callback_query.register(
        start.button_send_link,
        F.data == "send_link"
    )
    logger.info("✅ Обработчик 'Как скинуть ссылку' зарегистрирован")
    
    # Как это работает
    router.callback_query.register(
        start.button_how_it_works,
        F.data == "how_it_works"
    )
    logger.info("✅ Обработчик 'Как это работает' зарегистрирован")
    
    # Поддержка
    router.callback_query.register(
        start.button_support,
        F.data == "support"
    )
    logger.info("✅ Обработчик 'Поддержка' зарегистрирован")
    
    # Оформить заявку
    router.callback_query.register(
        requests.button_request,
        F.data == "request"
    )
    logger.info("✅ Обработчик 'Оформить заявку' зарегистрирован")
    
    # Назад в меню
    router.callback_query.register(
        start.button_back_to_start,
        F.data == "back_to_start"
    )
    logger.info("✅ Обработчик 'Назад в меню' зарегистрирован")
    
    # === АДМИН-ПАНЕЛЬ ===
    
    # Статистика
    router.callback_query.register(
        admin.button_admin_stats,
        F.data == "admin_stats"
    )
    logger.info("✅ Обработчик 'Статистика' зарегистрирован")
    
    # Список заявок
    router.callback_query.register(
        admin.button_admin_requests,
        F.data == "admin_requests"
    )
    logger.info("✅ Обработчик 'Список заявок' зарегистрирован")
    
    # Список админов
    router.callback_query.register(
        admin.button_admin_list,
        F.data == "admin_list"
    )
    logger.info("✅ Обработчик 'Список админов' зарегистрирован")
    
    # Информация о боте
    router.callback_query.register(
        admin.button_admin_info,
        F.data == "admin_info"
    )
    logger.info("✅ Обработчик 'Информация о боте' зарегистрирован")
    
    # Возврат в админку
    router.callback_query.register(
        admin.button_admin_back,
        F.data == "admin_back"
    )
    logger.info("✅ Обработчик 'Назад в админку' зарегистрирован")
    
    # Включаем router в диспетчер
    dp.include_router(router)
    logger.info("✅ Все обработчики зарегистрированы успешно!\n")
    
    print("\n" + "="*60)
    print("💎 BUFF Pay Bot АКТИВЕН И ГОТОВ!")
    print("="*60)
    print("\n📱 Отправь /start боту в Telegram\n")
    
    try:
        # Запускаем поллинг
        logger.info("🔄 Начинаю polling...")
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )
    except Exception as e:
        logger.error(f"❌ Ошибка при polling: {e}", exc_info=True)
    finally:
        logger.info("❌ Бот остановлен")
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Бот остановлен (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
