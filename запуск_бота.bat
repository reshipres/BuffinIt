@echo off
chcp 65001 > nul
echo ========================================
echo   ЗАПУСК BUFF PAY BOT
echo ========================================
echo.

REM ВАЖНО: Замените YOUR_BOT_TOKEN_HERE на ваш токен бота
REM Получить токен можно у @BotFather в Telegram
set BOT_TOKEN=YOUR_BOT_TOKEN_HERE

REM Запускаем бота
echo Запускаю бота...
python bot.py

pause

