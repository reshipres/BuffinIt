@echo off
chcp 65001 > nul
echo ========================================
echo   PUSH В GITHUB
echo ========================================
echo.

REM Инициализация git (если еще не инициализирован)
if not exist .git (
    echo Инициализирую git...
    git init
    echo.
)

REM Добавляем remote (если еще не добавлен)
git remote remove origin 2>nul
echo Добавляю remote origin...
git remote add origin https://github.com/reshipres/BuffinIt.git
echo.

REM Добавляем все файлы
echo Добавляю файлы...
git add .
echo.

REM Коммит
echo Создаю коммит...
git commit -m "BUFF Pay Bot - Telegram бот для покупки скинов с обязательной подпиской на канал"
echo.

REM Устанавливаем ветку main
git branch -M main
echo.

REM Push в GitHub
echo Пушу в GitHub...
git push -u origin main
echo.

echo ========================================
echo   ГОТОВО!
echo ========================================
echo.
echo Проект загружен на GitHub:
echo https://github.com/reshipres/BuffinIt
echo.

pause

