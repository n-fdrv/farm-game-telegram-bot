import re
from random import randint

from django.conf import settings
from django.utils import timezone
from loguru import logger

from game.models import Character, CharacterItem, LocationDrop

from bot.constants.messages.character_messages import CHARACTER_INFO_MESSAGE
from bot.utils.schedulers import remove_scheduler


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
    exp_in_percent = round(character.exp / character.exp_for_level_up * 100, 2)
    location = "<b>Город</b>"
    if character.current_location:
        time_left_text = "<b>Охота окончена</b>"
        if character.hunting_end > timezone.now():
            time_left = str(character.hunting_end - timezone.now()).split(".")[
                0
            ]
            time_left_text = f"Осталось: <b>{time_left}</b>"
        location = (
            f"<b>{character.current_location.name}</b>\n" f"{time_left_text}"
        )
    return CHARACTER_INFO_MESSAGE.format(
        character.name,
        character.level,
        exp_in_percent,
        character.power,
        location,
    )


async def get_hunting_hours_with_effects(character: Character):
    """Метод получения часов охоты с эффектами."""
    buff_percent = character.power / character.current_location.required_power
    hunting_end_time = timezone.now()
    if hunting_end_time > character.hunting_end:
        hunting_end_time = character.hunting_end
    hunting_hours = (
        (hunting_end_time - character.hunting_begin).seconds
        * buff_percent
        / 3600
    )
    return hunting_hours


async def get_exp(character: Character, exp_amount: int):
    """Метод получения опыта."""
    character.exp += exp_amount
    while character.exp >= character.exp_for_level_up:
        character.exp = character.exp - character.exp_for_level_up
        character.exp_for_level_up += (
            character.exp_for_level_up * settings.EXP_FOR_LEVEL_UP_MULTIPLIER
        )
        character.power += character.power * settings.POWER_LEVEL_UP_MULTIPLIER
        character.level += 1
    await character.asave(
        update_fields=("level", "exp", "exp_for_level_up", "power")
    )
    return character


async def get_hunting_loot(character: Character):
    """Метод получения трофеев с охоты."""
    hunting_hours = await get_hunting_hours_with_effects(character)
    exp_gained = int(character.current_location.exp * hunting_hours)
    drop_data = {}
    await get_exp(character, exp_gained)
    async for drop in LocationDrop.objects.select_related(
        "item", "location"
    ).filter(location=character.current_location):
        for _hour in range(int(hunting_hours)):
            success = randint(1, 100) <= drop.chance
            if success:
                amount = randint(drop.min_amount, drop.max_amount)
                item, created = await CharacterItem.objects.aget_or_create(
                    character=character, item=drop.item
                )
                if drop.item.name not in drop_data:
                    drop_data[drop.item.name] = 0
                drop_data[drop.item.name] += amount
                item.amount += amount
                await item.asave(update_fields=("amount",))
    logger.info(
        f"{character} - Вышел из {character.current_location} "
        f"и получил {exp_gained} опыта и "
        f"{drop_data} зв {hunting_hours} времени"
    )
    character.current_location = None
    character.hunting_begin = None
    character.hunting_end = None
    await remove_scheduler(character.job_id)
    character.job_id = None
    await character.asave(
        update_fields=(
            "current_location",
            "hunting_begin",
            "hunting_end",
            "job_id",
        )
    )
    return exp_gained, drop_data
