import re

from game.models import Character

from bot.constants.messages.character_messages import CHARACTER_INFO_MESSAGE


async def check_nickname_exist(nickname: str) -> bool:
    """Проверка занят ли никнейм персонажа."""
    return await Character.objects.filter(name=nickname).aexists()


def check_nickname_correct(nickname: str) -> bool:
    """Валидатор проверки корректности ввода имени и фамилии."""
    if not re.search("^[А-Яа-яA-Za-z0-9]{1,16}$", nickname):
        return False
    return True


def get_character_info(character: Character) -> str:
    """Возвращает сообщение с данными о персонаже."""
    exp_in_percent = character.exp / character.exp_for_level_up * 100
    return CHARACTER_INFO_MESSAGE.format(
        character.name, character.level, exp_in_percent, character.power
    )
