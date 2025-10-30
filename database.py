"""
Модуль для работы с базой данных заявок.

Создает таблицу если её нет, сохраняет и получает заявки.
"""

import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Имя файла базы данных
DB_NAME = "buff_requests.db"


def init_database():
    """
    Инициализирует базу данных.
    Создает таблицу requests если её нет.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Создаем таблицу если её нет
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                amount TEXT NOT NULL,
                link TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("✅ База данных инициализирована")
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}", exc_info=True)


def save_request(user_id: int, username: str, amount: str, link: str) -> bool:
    """
    Сохраняет заявку в базу данных.
    
    Args:
        user_id: ID пользователя Telegram
        username: Username пользователя
        amount: Сумма в юанях
        link: Ссылка на товар
        
    Returns:
        True если успешно сохранено, False если ошибка
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Получаем текущее время
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Вставляем заявку
        cursor.execute("""
            INSERT INTO requests (user_id, username, amount, link, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, amount, link, created_at))
        
        conn.commit()
        request_id = cursor.lastrowid
        conn.close()
        
        logger.info(f"✅ Заявка #{request_id} сохранена от @{username}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения заявки: {e}", exc_info=True)
        return False


def get_all_requests(limit: int = 10):
    """
    Получает последние заявки из базы данных.
    
    Args:
        limit: Количество заявок для получения
        
    Returns:
        Список кортежей с данными заявок
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, username, amount, link, created_at 
            FROM requests 
            ORDER BY id DESC 
            LIMIT ?
        """, (limit,))
        
        requests = cursor.fetchall()
        conn.close()
        
        return requests
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения заявок: {e}", exc_info=True)
        return []


def get_statistics():
    """
    Получает статистику по заявкам.
    
    Returns:
        dict с статистикой (total_requests, unique_users)
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Всего заявок
        cursor.execute("SELECT COUNT(*) FROM requests")
        total_requests = cursor.fetchone()[0]
        
        # Уникальных пользователей
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM requests")
        unique_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_requests": total_requests,
            "unique_users": unique_users
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения статистики: {e}", exc_info=True)
        return {
            "total_requests": 0,
            "unique_users": 0
        }


# Инициализируем БД при импорте модуля
init_database()

