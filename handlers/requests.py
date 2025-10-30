"""
Обработчик для сбора и обработки заявок на покупку.

Собирает ссылку на товар и сумму, затем отправляет уведомление менеджеру (если ID указан).
Сохраняет заявки в базу данных и уведомляет админов.
"""

import logging
from aiogram import types, Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import MANAGER_ID, MANAGER_USERNAME
from database import save_request
from admins import ADMINS
from handlers.subscription import check_subscription, send_subscription_required

logger = logging.getLogger(__name__)

# Определяем состояния для сбора данных заявки
# FSM = Finite State Machine (конечный автомат)
class RequestStates(StatesGroup):
    """Состояния при сборе информации о заявке."""
    
    # Ждём ссылку на товар
    waiting_for_link = State()
    
    # Ждём сумму в юанях
    waiting_for_amount = State()


async def button_request(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки 'Оформить заявку'.
    
    Запускает процесс сбора информации и переводит пользователя
    в состояние ожидания ссылки на товар.
    """
    
    logger.info(f"📨 Кнопка 'request' от {callback.from_user.id}")
    
    # Проверяем подписку
    is_subscribed = await check_subscription(callback.from_user.id, callback.bot)
    if not is_subscribed:
        await send_subscription_required(callback)
        return
    
    request_text = """🧾 <b>Оформление заявки</b>

Отправь, пожалуйста:
1️⃣ Ссылку на товар на BUFF
2️⃣ Сумму в юанях (¥)

Пример:
<code>https://buff.163.com/goods/42542</code>
<code>150</code>

После этого я передам данные менеджеру @BuffinItMNG.
Он попросит QR-код и оплатит покупку от китайского аккаунта."""
    
    # Отправляем сообщение (новое)
    await callback.message.answer(request_text)
    
    # Переводим пользователя в состояние ожидания ссылки
    await state.set_state(RequestStates.waiting_for_link)
    
    logger.info(f"✅ Процесс оформления заявки начат")
    
    # Подтверждаем нажатие кнопки
    await callback.answer()


async def collect_request_data(message: types.Message, state: FSMContext):
    """
    Обработчик для сбора данных заявки.
    
    Этот обработчик работает в зависимости от текущего состояния:
    - Если пользователь в состоянии waiting_for_link — сохраняем ссылку
    - Если пользователь в состоянии waiting_for_amount — сохраняем сумму и отправляем заявку
    """
    
    # Получаем текущее состояние пользователя
    current_state = await state.get_state()
    
    # Если пользователь не находится в процессе заявки — игнорируем
    if current_state is None:
        return
    
    # === ЭТАП 1: Сбор ссылки ===
    if current_state == RequestStates.waiting_for_link:
        # Сохраняем ссылку в контексте FSM
        await state.update_data(link=message.text)
        
        # Переводим на следующий этап — сбор суммы
        await state.set_state(RequestStates.waiting_for_amount)
        
        logger.info(f"📎 Ссылка получена от {message.from_user.id}")
        
        # Просим ввести сумму
        await message.answer(
            "✅ Ссылка получена!\n\n"
            "Теперь отправь сумму в юанях (¥)\n\n"
            "Пример: <code>150</code>"
        )
    
    # === ЭТАП 2: Сбор суммы ===
    elif current_state == RequestStates.waiting_for_amount:
        # Получаем сохранённую ссылку из контекста
        user_data = await state.get_data()
        link = user_data.get("link")
        amount = message.text
        
        # Сохраняем данные пользователя
        user_id = message.from_user.id
        username = message.from_user.username or "не указано"
        
        # Очищаем состояние (заявка завершена)
        await state.clear()
        
        logger.info(f"💳 Заявка готова от {user_id}: {amount} ¥")
        
        # Сохраняем заявку в базу данных
        save_request(user_id, username, amount, link)
        
        # Отправляем подтверждение пользователю
        await message.answer(
            "✅ <b>Заявка создана!</b>\n\n"
            f"💳 <b>Сумма:</b> {amount} ¥\n"
            f"🔗 <b>Ссылка:</b> {link}\n\n"
            f"Менеджер <code>@{MANAGER_USERNAME}</code> свяжется с тобой в ближайшее время.\n"
            "Будь онлайн — QR-код действует ограниченное время."
        )
        
        # Отправляем уведомление менеджеру (если ID указан)
        if MANAGER_ID:
            await send_notification_to_manager(
                user_id=user_id,
                username=username,
                amount=amount,
                link=link
            )
        else:
            logger.warning("⚠️  MANAGER_ID не установлен. Уведомление менеджеру не отправлено.")
        
        # Отправляем уведомление всем админам
        await send_notifications_to_admins(user_id, username, amount, link)


async def send_notification_to_manager(user_id: int, username: str, amount: str, link: str):
    """
    Отправляет уведомление менеджеру о новой заявке.
    
    Args:
        user_id: ID пользователя в Telegram
        username: Username пользователя в Telegram
        amount: Сумма в юанях
        link: Ссылка на товар
    """
    
    try:
        # Создаём экземпляр бота для отправки уведомления
        from config import BOT_TOKEN
        bot = Bot(token=BOT_TOKEN)
        
        # Формируем текст уведомления для менеджера
        notification_text = f"""📥 <b>Новая заявка с BUFF Pay</b>

👤 <b>Пользователь:</b> @{username}
🆔 <b>ID:</b> <code>{user_id}</code>
💳 <b>Сумма:</b> <code>{amount}</code> ¥
🔗 <b>Ссылка:</b>
<code>{link}</code>

⏰ <b>Действие:</b> Свяжись через @BuffinItMNG для запроса QR-кода."""
        
        # Отправляем уведомление менеджеру
        await bot.send_message(
            chat_id=int(MANAGER_ID),
            text=notification_text,
            parse_mode="HTML"
        )
        
        logger.info(f"🔔 Менеджер оповещён о заявке от @{username}")
        
        # Закрываем сессию бота
        await bot.session.close()
        
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке уведомления менеджеру: {e}", exc_info=True)


async def send_notifications_to_admins(user_id: int, username: str, amount: str, link: str):
    """
    Отправляет уведомления всем админам о новой заявке.
    
    Args:
        user_id: ID пользователя в Telegram
        username: Username пользователя в Telegram
        amount: Сумма в юанях
        link: Ссылка на товар
    """
    
    # Если нет админов - выходим
    if not ADMINS:
        logger.warning("⚠️  Список админов пуст. Уведомления не отправлены.")
        return
    
    try:
        # Создаём экземпляр бота для отправки уведомлений
        from config import BOT_TOKEN
        bot = Bot(token=BOT_TOKEN)
        
        # Формируем текст уведомления для админов
        notification_text = f"""🔔 <b>НОВАЯ ЗАЯВКА</b>

👤 <b>Пользователь:</b> @{username}
🆔 <b>ID:</b> <code>{user_id}</code>
💰 <b>Сумма:</b> {amount} ¥
🔗 <b>Ссылка:</b>
{link}

📊 Проверьте админ-панель: /admin"""
        
        # Отправляем уведомление каждому админу
        for admin_id, admin_username in ADMINS:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=notification_text,
                    parse_mode="HTML"
                )
                logger.info(f"🔔 Админ @{admin_username} (ID: {admin_id}) оповещён о заявке")
            except Exception as e:
                logger.error(f"❌ Не удалось отправить уведомление админу @{admin_username}: {e}")
        
        # Закрываем сессию бота
        await bot.session.close()
        
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке уведомлений админам: {e}", exc_info=True)
