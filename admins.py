"""
Список администраторов бота.

Администраторы имеют доступ к админ-панели через команду /admin.
Для добавления нового админа - добавь его user_id и username в список ADMINS.
"""

# Список администраторов
# Формат: (user_id, "username")
ADMINS = [
    (991411028, "conqu3st"),
    (374996796, "DogXe7"),
    (476915109, "no_username"),  # У этого пользователя нет username
]


def is_admin(user_id: int) -> bool:
    """
    Проверяет, является ли пользователь администратором.
    
    Args:
        user_id: ID пользователя Telegram
        
    Returns:
        True если пользователь админ, False иначе
    """
    return any(admin[0] == user_id for admin in ADMINS)


def get_admin_usernames() -> list[str]:
    """
    Возвращает список username всех админов.
    
    Returns:
        Список username админов
    """
    return [admin[1] for admin in ADMINS]

