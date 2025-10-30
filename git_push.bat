@echo off
chcp 65001 >nul
echo ============================================
echo     PUSH TO GITHUB
echo ============================================
echo.

REM Инициализация git если нужно
if not exist ".git" (
    echo Инициализация Git репозитория...
    git init
    echo.
)

REM Добавляем remote origin
echo Добавление remote origin...
git remote remove origin 2>nul
git remote add origin https://github.com/reshipres/BuffinIt.git
echo.

REM Добавляем все файлы
echo Добавление файлов...
git add .
echo.

REM Делаем commit
echo Создание commit...
git commit -m "Initial commit: BUFF Pay Bot with Admin Panel"
echo.

REM Устанавливаем main как основную ветку
echo Переименование ветки в main...
git branch -M main
echo.

REM Push в GitHub
echo Отправка в GitHub...
git push -u origin main
echo.

echo ============================================
echo     ГОТОВО!
echo ============================================
pause

