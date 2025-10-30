"""
Модуль проверки обязательной подписки на канал.

Проверяет, подписан ли пользователь на канал BUFF.
Если не подписан - показывает красивое сообщение про безопасность.
"""

import logging
from aiogram import types, Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import REQUIRED_CHANNEL, REQUIRED_CHANNEL_ID

logger = logging.getLogger(__name__)


async def send_main_menu(message: types.Message):
    """
    Отправляет главное меню бота.
    
    Args:
        message: Объект сообщения для отправки меню
    """
    
    text = """💎 <b>BUFF Pay</b> — покупай скины в 2 раза дешевле, чем в Steam

Если ты покупаешь через Steam — ты переплачиваешь до 40%.
В Китае есть официальный маркетплейс BUFF (buff.163.com), где те же скины стоят на треть дешевле.

Мы помогаем тебе купить там, где ты не можешь сам.

📍 <b>Выбери что тебе нужно:</b>"""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🪪 Как зарегистрироваться", callback_data="register")
    keyboard.button(text="🔗 Как скинуть ссылку", callback_data="send_link")
    keyboard.button(text="🧾 Оформить заявку", callback_data="request")
    keyboard.button(text="❓ Как это работает", callback_data="how_it_works")
    keyboard.button(text="💬 Поддержка", callback_data="support")
    keyboard.adjust(1)
    
    try:
        # Используем bot.send_message для надёжности
        bot = message.bot
        await bot.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=keyboard.as_markup(),
            parse_mode="HTML"
        )
        logger.info(f"✅ Главное меню отправлено")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки главного меню: {e}", exc_info=True)


async def check_subscription(user_id: int, bot: Bot) -> bool:
    """
    Проверяет подписан ли пользователь на обязательный канал.
    
    Args:
        user_id: ID пользователя Telegram
        bot: Экземпляр бота
        
    Returns:
        True если подписан, False если нет
    """
    try:
        # Получаем информацию о пользователе в канале
        member = await bot.get_chat_member(
            chat_id=REQUIRED_CHANNEL_ID,
            user_id=user_id
        )
        
        # Проверяем статус: member, administrator, creator
        # restricted и kicked - не подписан
        if member.status in ["member", "administrator", "creator"]:
            logger.info(f"✅ Пользователь {user_id} подписан на канал")
            return True
        else:
            logger.info(f"❌ Пользователь {user_id} НЕ подписан (статус: {member.status})")
            return False
            
    except Exception as e:
        # Если ошибка (например пользователь не в канале) - считаем что не подписан
        logger.warning(f"⚠️ Ошибка проверки подписки для {user_id}: {e}")
        return False


async def send_subscription_required(message_or_callback):
    """
    Отправляет красивое сообщение о необходимости подписаться на канал.
    
    Args:
        message_or_callback: Message или CallbackQuery объект
    """
    
    # Определяем откуда пришел запрос (сообщение или кнопка)
    if isinstance(message_or_callback, types.CallbackQuery):
        message = message_or_callback.message
        user_id = message_or_callback.from_user.id
        bot = message_or_callback.bot
        chat_id = message.chat.id
    else:
        message = message_or_callback
        user_id = message.from_user.id
        bot = message.bot
        chat_id = message.chat.id
    
    logger.info(f"🔒 Показываем требование подписки для {user_id}")
    
    # Строгое сообщение про безопасность
    text = """<b>Обязательная подписка</b>

Для защиты от фейковых ботов и мошенников необходимо подписаться на официальный канал {channel}

В канале публикуются официальные новости, информация о безопасности и предупреждения о мошенниках.

После подписки нажмите кнопку "Проверить подписку".""".format(channel=REQUIRED_CHANNEL)
    
    # Создаем кнопки
    keyboard = InlineKeyboardBuilder()
    
    # Кнопка подписки на канал
    keyboard.button(
        text="Подписаться на канал",
        url=f"https://t.me/{REQUIRED_CHANNEL.replace('@', '')}"
    )
    
    # Кнопка проверки подписки
    keyboard.button(
        text="Проверить подписку",
        callback_data="check_subscription"
    )
    
    keyboard.adjust(1)  # По одной кнопке в строке
    
    try:
        # Используем bot.send_message вместо message.answer для надёжности
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard.as_markup(),
            disable_web_page_preview=True,
            parse_mode="HTML"
        )
        logger.info(f"✅ Сообщение о подписке отправлено пользователю {user_id}")
        
        # Если это callback - отвечаем на него
        if isinstance(message_or_callback, types.CallbackQuery):
            await message_or_callback.answer(
                "Требуется подписка на канал",
                show_alert=True
            )
            
    except Exception as e:
        logger.error(f"❌ Ошибка отправки сообщения о подписке: {e}", exc_info=True)


async def button_check_subscription(callback: types.CallbackQuery):
    """
    Обработчик кнопки "Я подписался".
    Проверяет подписку и либо пропускает дальше, либо просит подписаться снова.
    """
    
    user_id = callback.from_user.id
    logger.info(f"🔍 Проверка подписки для пользователя {user_id}")
    
    # Проверяем подписку
    is_subscribed = await check_subscription(user_id, callback.bot)
    
    if is_subscribed:
        # Пользователь подписан - показываем главное меню
        logger.info(f"✅ Пользователь {user_id} подписан, показываем меню")
        
        await callback.answer("Подписка подтверждена", show_alert=False)
        
        # Отправляем главное меню напрямую
        await send_main_menu(callback.message)
        
    else:
        # Пользователь еще не подписан
        logger.warning(f"❌ Пользователь {user_id} все еще не подписан")
        
        await callback.answer(
            "Подписка не обнаружена. Подпишитесь на канал и повторите попытку.",
            show_alert=True
        )
        
        # Отправляем сообщение о подписке снова
        await send_subscription_required(callback)

