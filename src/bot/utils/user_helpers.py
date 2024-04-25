from bot.models import User


async def get_user(user_id: int) -> User:
    """Метод получения пользователя из базы данных."""
    user, created = await User.objects.select_related(
        "character",
        "character__current_place",
        "character__character_class",
        "character__clan",
        "character__clan__leader",
        "character__clan__leader__character_class",
        "character__clan__leader__clan",
    ).aget_or_create(telegram_id=user_id)
    return user


def get_user_url(user: User) -> str:
    """Метод формирования ссылки на пользователя."""
    name = user.telegram_username
    if user.first_name:
        name = user.first_name
    if user.last_name:
        name += f" {user.last_name}"
    return f"[{name}](tg://user?id={str(user.telegram_id)})"
