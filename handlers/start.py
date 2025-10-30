"""
Обработчик команды /start и главного меню.

Система навигации с отправкой новых сообщений (не редактированием).
Добавлены гайды по регистрации и получению ссылок.
"""

import logging
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.subscription import check_subscription, send_subscription_required

logger = logging.getLogger(__name__)


# ============================================================================
# ГЛАВНОЕ МЕНЮ
# ============================================================================

async def start_command(message: types.Message):
    """Команда /start - главное меню."""
    
    logger.info(f"📨 /start от {message.from_user.id}")
    
    # Проверяем подписку на канал
    is_subscribed = await check_subscription(message.from_user.id, message.bot)
    
    if not is_subscribed:
        # Если не подписан - показываем сообщение о необходимости подписки
        logger.info(f"🔒 Пользователь {message.from_user.id} не подписан на канал")
        await send_subscription_required(message)
        return
    
    # Если подписан - показываем главное меню
    logger.info(f"✅ Пользователь {message.from_user.id} подписан, показываем меню")
    
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
        await message.answer(text, reply_markup=keyboard.as_markup())
        logger.info(f"✅ Главное меню отправлено")
    except Exception as e:
        logger.error(f"❌ Ошибка в start_command: {e}", exc_info=True)


# ============================================================================
# РЕГИСТРАЦИЯ ЧЕРЕЗ STEAM
# ============================================================================

async def button_register(callback: types.CallbackQuery):
    """Гайд по регистрации на BUFF через Steam."""
    
    logger.info(f"📨 Кнопка 'register' от {callback.from_user.id}")
    
    # Проверяем подписку
    is_subscribed = await check_subscription(callback.from_user.id, callback.bot)
    if not is_subscribed:
        await send_subscription_required(callback)
        return
    
    text = """🪪 <b>Как зарегистрироваться на BUFF (buff.163.com)</b>

1️⃣ Зайди на сайт <code>https://buff.163.com</code>

2️⃣ Нажми «Login via Steam» (кнопка с логотипом Steam)

3️⃣ Авторизуйся через свой Steam-аккаунт

4️⃣ После входа BUFF попросит подтвердить номер телефона:
   • Выбери страну 🇰🇿 Казахстан
   • Введи свой номер
   • Убедись что VPN выключен
   • Подтверди SMS-код

5️⃣ После этого аккаунт BUFF будет создан!

✅ <b>Теперь ты можешь спокойно:</b>
   • Смотреть и покупать скины
   • На сайте есть русская версия интерфейса
   • Цены отображаются в юанях
   • Можно добавить в «Избранное» интересующие товары

<b>Следующий шаг:</b> Нажми «Как скинуть ссылку», чтобы узнать как найти и отправить скин"""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🔗 Как скинуть ссылку", callback_data="send_link")
    keyboard.button(text="⬅️ Назад в меню", callback_data="back_to_start")
    keyboard.adjust(1)
    
    try:
        await callback.message.answer(text, reply_markup=keyboard.as_markup())
        logger.info(f"✅ Гайд регистрации отправлен")
    except Exception as e:
        logger.error(f"❌ Ошибка в button_register: {e}", exc_info=True)
    
    await callback.answer()


# ============================================================================
# ГАЙД ПО ССЫЛКЕ НА ТОВАР
# ============================================================================

async def button_send_link(callback: types.CallbackQuery):
    """Гайд по отправке ссылки на товар."""
    
    logger.info(f"📨 Кнопка 'send_link' от {callback.from_user.id}")
    
    # Проверяем подписку
    is_subscribed = await check_subscription(callback.from_user.id, callback.bot)
    if not is_subscribed:
        await send_subscription_required(callback)
        return
    
    text = """🔗 <b>Как скинуть ссылку на товар с BUFF</b>

1️⃣ Зайди на <code>https://buff.163.com</code> и выбери нужный скин

2️⃣ Нажми на товар, чтобы открыть его страницу

3️⃣ Скопируй ссылку из адресной строки

Пример:
<code>https://buff.163.com/goods/42542</code>

4️⃣ Отправь эту ссылку и сумму в юанях в этого бота

5️⃣ Менеджер @BuffinItMNG напишет тебе и попросит QR-код для оплаты

<b>Готов отправить заявку?</b> Нажми кнопку ниже 👇"""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🧾 Оформить заявку", callback_data="request")
    keyboard.button(text="⬅️ Назад в меню", callback_data="back_to_start")
    keyboard.adjust(1)
    
    try:
        await callback.message.answer(text, reply_markup=keyboard.as_markup())
        logger.info(f"✅ Гайд по ссылке отправлен")
    except Exception as e:
        logger.error(f"❌ Ошибка в button_send_link: {e}", exc_info=True)
    
    await callback.answer()


# ============================================================================
# КАК ЭТО РАБОТАЕТ
# ============================================================================

async def button_how_it_works(callback: types.CallbackQuery):
    """Объяснение как всё работает."""
    
    logger.info(f"📨 Кнопка 'how_it_works' от {callback.from_user.id}")
    
    # Проверяем подписку
    is_subscribed = await check_subscription(callback.from_user.id, callback.bot)
    if not is_subscribed:
        await send_subscription_required(callback)
        return
    
    text = """⚙️ <b>Как это работает</b>

1️⃣ Ты сам заходишь на сайт <code>buff.163.com</code>

2️⃣ Выбираешь скин, доходишь до оплаты — BUFF покажет QR-код

3️⃣ Возвращаешься сюда и жмёшь «Оформить заявку»

4️⃣ Вводишь сумму и ссылку на товар

5️⃣ Мы переадресуем тебя менеджеру @BuffinItMNG

6️⃣ Менеджер попросит QR-код и оплатит покупку через китайскую платёжную систему

7️⃣ Скин падает прямо в твой инвентарь

💰 <b>Средняя экономия — 30–40% по сравнению со Steam</b>"""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="⬅️ Назад в меню", callback_data="back_to_start")
    keyboard.adjust(1)
    
    try:
        await callback.message.answer(text, reply_markup=keyboard.as_markup())
        logger.info(f"✅ Гайд 'как это работает' отправлен")
    except Exception as e:
        logger.error(f"❌ Ошибка в button_how_it_works: {e}", exc_info=True)
    
    await callback.answer()


# ============================================================================
# ПОДДЕРЖКА
# ============================================================================

async def button_support(callback: types.CallbackQuery):
    """Контакт поддержки."""
    
    logger.info(f"📨 Кнопка 'support' от {callback.from_user.id}")
    
    # Проверяем подписку
    is_subscribed = await check_subscription(callback.from_user.id, callback.bot)
    if not is_subscribed:
        await send_subscription_required(callback)
        return
    
    text = """📞 <b>Поддержка</b>

Если что-то непонятно или нужна срочная помощь — пиши менеджеру:

<code>@BuffinItMNG</code>

Он ответит на все вопросы и поможет с заявкой."""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="⬅️ Назад в меню", callback_data="back_to_start")
    keyboard.adjust(1)
    
    try:
        await callback.message.answer(text, reply_markup=keyboard.as_markup())
        logger.info(f"✅ Поддержка отправлена")
    except Exception as e:
        logger.error(f"❌ Ошибка в button_support: {e}", exc_info=True)
    
    await callback.answer()


# ============================================================================
# ВОЗВРАТ В МЕНЮ
# ============================================================================

async def button_back_to_start(callback: types.CallbackQuery):
    """Возврат в главное меню."""
    
    logger.info(f"📨 Кнопка 'back_to_start' от {callback.from_user.id}")
    
    # Проверяем подписку
    is_subscribed = await check_subscription(callback.from_user.id, callback.bot)
    if not is_subscribed:
        await send_subscription_required(callback)
        return
    
    text = """💎 <b>BUFF Pay</b> — главное меню

Выбери что тебе нужно:"""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🪪 Как зарегистрироваться", callback_data="register")
    keyboard.button(text="🔗 Как скинуть ссылку", callback_data="send_link")
    keyboard.button(text="🧾 Оформить заявку", callback_data="request")
    keyboard.button(text="❓ Как это работает", callback_data="how_it_works")
    keyboard.button(text="💬 Поддержка", callback_data="support")
    keyboard.adjust(1)
    
    try:
        await callback.message.answer(text, reply_markup=keyboard.as_markup())
        logger.info(f"✅ Вернулись в меню")
    except Exception as e:
        logger.error(f"❌ Ошибка в button_back_to_start: {e}", exc_info=True)
    
    await callback.answer()
