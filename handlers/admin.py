"""
Обработчики админ-панели.

Доступ только для пользователей из списка ADMINS.
Функционал:
- Статистика пользователей
- Просмотр заявок
- Управление ботом
"""

import logging
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from admins import is_admin, ADMINS

logger = logging.getLogger(__name__)


# ============================================================================
# ГЛАВНОЕ МЕНЮ АДМИН-ПАНЕЛИ
# ============================================================================

async def admin_command(message: types.Message):
    """
    Команда /admin - открывает админ-панель.
    Доступна только администраторам.
    """
    
    user_id = message.from_user.id
    username = message.from_user.username or "без username"
    
    logger.info(f"📨 /admin от {user_id} (@{username})")
    
    # Проверка прав доступа
    if not is_admin(user_id):
        logger.warning(f"⚠️ Попытка доступа к админке от {user_id} (@{username})")
        await message.answer("❌ У вас нет доступа к админ-панели")
        return
    
    # Формируем текст приветствия
    text = f"""🔐 <b>АДМИН-ПАНЕЛЬ</b>

👤 Вы вошли как: @{username} (ID: {user_id})

📊 <b>Выберите действие:</b>"""
    
    # Создаем клавиатуру
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📊 Статистика", callback_data="admin_stats")
    keyboard.button(text="📋 Все заявки", callback_data="admin_requests")
    keyboard.button(text="👥 Список админов", callback_data="admin_list")
    keyboard.button(text="ℹ️ О боте", callback_data="admin_info")
    keyboard.adjust(1)
    
    try:
        await message.answer(text, reply_markup=keyboard.as_markup())
        logger.info(f"✅ Админ-панель открыта для {user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка в admin_command: {e}", exc_info=True)


# ============================================================================
# СТАТИСТИКА
# ============================================================================

async def button_admin_stats(callback: types.CallbackQuery):
    """Показывает статистику бота."""
    
    user_id = callback.from_user.id
    
    # Проверка прав
    if not is_admin(user_id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    logger.info(f"📨 Кнопка 'admin_stats' от {user_id}")
    
    try:
        # Получаем статистику из модуля database
        from database import get_statistics
        
        stats = get_statistics()
        total_requests = stats["total_requests"]
        unique_users = stats["unique_users"]
        
        # Формируем текст
        text = f"""📊 <b>СТАТИСТИКА БОТА</b>

📝 <b>Заявки:</b>
   • Всего заявок: {total_requests}

👥 <b>Пользователи:</b>
   • Уникальных пользователей: {unique_users}

🔄 <b>Обновлено:</b> только что"""
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения статистики: {e}", exc_info=True)
        text = f"❌ <b>Ошибка получения статистики</b>\n\n{str(e)}"
    
    # Кнопка назад
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="⬅️ Назад в админку", callback_data="admin_back")
    
    try:
        await callback.message.answer(text, reply_markup=keyboard.as_markup())
        logger.info(f"✅ Статистика отправлена админу {user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки статистики: {e}", exc_info=True)
    
    await callback.answer()


# ============================================================================
# ПРОСМОТР ЗАЯВОК
# ============================================================================

async def button_admin_requests(callback: types.CallbackQuery):
    """Показывает последние заявки."""
    
    user_id = callback.from_user.id
    
    # Проверка прав
    if not is_admin(user_id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    logger.info(f"📨 Кнопка 'admin_requests' от {user_id}")
    
    try:
        # Получаем заявки из модуля database
        from database import get_all_requests
        
        requests = get_all_requests(limit=10)
        
        if not requests:
            text = "📋 <b>ЗАЯВКИ</b>\n\nПока нет ни одной заявки"
        else:
            text = f"📋 <b>ПОСЛЕДНИЕ 10 ЗАЯВОК</b>\n\n"
            
            for req in requests:
                req_id, req_user_id, req_username, amount, link, created_at = req
                
                # Форматируем заявку
                text += f"<b>Заявка #{req_id}</b>\n"
                text += f"👤 @{req_username or 'нет username'} (ID: {req_user_id})\n"
                text += f"💰 Сумма: {amount} ¥\n"
                text += f"🔗 Ссылка: {link}\n"
                text += f"📅 Дата: {created_at}\n"
                text += "─" * 30 + "\n\n"
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения заявок: {e}", exc_info=True)
        text = f"❌ <b>Ошибка получения заявок</b>\n\n{str(e)}"
    
    # Кнопка назад
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="⬅️ Назад в админку", callback_data="admin_back")
    
    try:
        await callback.message.answer(text, reply_markup=keyboard.as_markup())
        logger.info(f"✅ Список заявок отправлен админу {user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки заявок: {e}", exc_info=True)
    
    await callback.answer()


# ============================================================================
# СПИСОК АДМИНОВ
# ============================================================================

async def button_admin_list(callback: types.CallbackQuery):
    """Показывает список всех админов."""
    
    user_id = callback.from_user.id
    
    # Проверка прав
    if not is_admin(user_id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    logger.info(f"📨 Кнопка 'admin_list' от {user_id}")
    
    text = "👥 <b>СПИСОК АДМИНИСТРАТОРОВ</b>\n\n"
    
    if not ADMINS:
        text += "Список администраторов пуст.\n\n"
        text += "Добавьте админов в файл <code>admins.py</code>"
    else:
        for idx, (admin_id, admin_username) in enumerate(ADMINS, 1):
            text += f"{idx}. @{admin_username} (ID: <code>{admin_id}</code>)\n"
        
        text += f"\n<b>Всего админов:</b> {len(ADMINS)}"
    
    # Кнопка назад
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="⬅️ Назад в админку", callback_data="admin_back")
    
    try:
        await callback.message.answer(text, reply_markup=keyboard.as_markup())
        logger.info(f"✅ Список админов отправлен админу {user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки списка админов: {e}", exc_info=True)
    
    await callback.answer()


# ============================================================================
# ИНФОРМАЦИЯ О БОТЕ
# ============================================================================

async def button_admin_info(callback: types.CallbackQuery):
    """Показывает информацию о боте."""
    
    user_id = callback.from_user.id
    
    # Проверка прав
    if not is_admin(user_id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    logger.info(f"📨 Кнопка 'admin_info' от {user_id}")
    
    text = """ℹ️ <b>ИНФОРМАЦИЯ О БОТЕ</b>

<b>Название:</b> BUFF Pay Bot
<b>Версия:</b> 1.0

<b>Функционал:</b>
• Прием заявок от пользователей
• Система навигации с гайдами
• Отправка уведомлений менеджеру
• Админ-панель для управления

<b>База данных:</b> SQLite (buff_requests.db)
<b>Библиотека:</b> aiogram 3.x

<b>Файлы:</b>
• bot.py - основной файл
• config.py - конфигурация
• admins.py - список админов
• handlers/ - обработчики команд"""
    
    # Кнопка назад
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="⬅️ Назад в админку", callback_data="admin_back")
    
    try:
        await callback.message.answer(text, reply_markup=keyboard.as_markup())
        logger.info(f"✅ Информация отправлена админу {user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки информации: {e}", exc_info=True)
    
    await callback.answer()


# ============================================================================
# ВОЗВРАТ В АДМИН-ПАНЕЛЬ
# ============================================================================

async def button_admin_back(callback: types.CallbackQuery):
    """Возврат в главное меню админ-панели."""
    
    user_id = callback.from_user.id
    username = callback.from_user.username or "без username"
    
    # Проверка прав
    if not is_admin(user_id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    logger.info(f"📨 Кнопка 'admin_back' от {user_id}")
    
    # Формируем меню админки
    text = f"""🔐 <b>АДМИН-ПАНЕЛЬ</b>

👤 Вы вошли как: @{username} (ID: {user_id})

📊 <b>Выберите действие:</b>"""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📊 Статистика", callback_data="admin_stats")
    keyboard.button(text="📋 Все заявки", callback_data="admin_requests")
    keyboard.button(text="👥 Список админов", callback_data="admin_list")
    keyboard.button(text="ℹ️ О боте", callback_data="admin_info")
    keyboard.adjust(1)
    
    try:
        await callback.message.answer(text, reply_markup=keyboard.as_markup())
        logger.info(f"✅ Возврат в админку для {user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка возврата в админку: {e}", exc_info=True)
    
    await callback.answer()

