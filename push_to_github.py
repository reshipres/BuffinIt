"""
Скрипт для пуша проекта в GitHub.
Выполняет все необходимые git команды.
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Выполняет команду и выводит результат."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print('='*60)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=False,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  PUSH ПРОЕКТА В GITHUB")
    print("="*60)
    
    # Проверяем наличие git
    if not run_command("git --version", "Проверка Git"):
        print("\n❌ Git не установлен или недоступен!")
        print("Установите Git: https://git-scm.com/download/win")
        input("\nНажмите Enter для выхода...")
        return
    
    # Инициализация git (если нужно)
    if not os.path.exists(".git"):
        run_command("git init", "Инициализация Git репозитория")
    
    # Удаляем старый remote (если есть)
    run_command("git remote remove origin", "Удаление старого remote (если есть)")
    
    # Добавляем remote
    if not run_command(
        "git remote add origin https://github.com/reshipres/BuffinIt.git",
        "Добавление remote origin"
    ):
        print("\n⚠️ Remote уже существует или ошибка добавления")
    
    # Добавляем все файлы
    run_command("git add .", "Добавление всех файлов")
    
    # Создаем коммит
    commit_message = "BUFF Pay Bot - Telegram бот для покупки скинов с обязательной подпиской"
    run_command(f'git commit -m "{commit_message}"', "Создание коммита")
    
    # Устанавливаем ветку main
    run_command("git branch -M main", "Установка ветки main")
    
    # Push в GitHub
    print("\n" + "="*60)
    print("  PUSH В GITHUB")
    print("="*60)
    print("\n⚠️  Возможно потребуется авторизация в GitHub!")
    print("Введите свой логин и токен (или пароль) если попросит.\n")
    
    success = run_command("git push -u origin main", "Загрузка в GitHub")
    
    print("\n" + "="*60)
    if success:
        print("  ✅ УСПЕШНО!")
        print("="*60)
        print("\n🎉 Проект загружен на GitHub:")
        print("   https://github.com/reshipres/BuffinIt")
    else:
        print("  ⚠️  ВОЗМОЖНЫ ОШИБКИ")
        print("="*60)
        print("\nВозможные причины:")
        print("1. Нужна авторизация в GitHub")
        print("2. Репозиторий не пустой (используйте force push)")
        print("3. Нет прав доступа к репозиторию")
        print("\nРучной push:")
        print("git push -u origin main --force")
    
    print("\n")
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        input("\nНажмите Enter для выхода...")

