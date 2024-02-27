import random
import re

from character.models import Character, CharacterClass, CharacterItem
from django.conf import settings
from django.utils import timezone
from location.models import LocationDrop
from loguru import logger

from bot.character.messages import (
    CHARACTER_INFO_MESSAGE,
    CHARACTER_KILL_MESSAGE,
)
from bot.models import User


async def check_nickname_exist(nickname: str) -> bool:
    """Проверка занят ли никнейм персонажа."""
    return await Character.objects.filter(name=nickname).aexists()


def check_nickname_correct(nickname: str) -> bool:
    """Валидатор проверки корректности ввода имени и фамилии."""
    if not re.search("^[А-Яа-яA-Za-z0-9]{1,16}$", nickname):
        return False
    return True


async def create_character(
    user: User, name: str, character_class: CharacterClass
) -> Character:
    """Создает персонажа и присваивает его пользователю."""
    character = await Character.objects.acreate(
        name=name,
        character_class=character_class,
        attack=character_class.attack,
        defence=character_class.defence,
    )
    user.character = character
    await user.asave(update_fields=("character",))
    return character


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
        character.attack,
        character.defence,
        location,
    )


async def get_hunting_hours_with_effects(character: Character):
    """Метод получения часов охоты с эффектами."""
    buff_percent = character.attack / character.current_location.attack
    hunting_end_time = timezone.now()
    if hunting_end_time > character.hunting_end:
        hunting_end_time = character.hunting_end
    hunting_hours = (
        (hunting_end_time - character.hunting_begin).seconds
        * buff_percent
        / 3600
    )
    return hunting_hours


async def get_hunting_minutes(character: Character):
    """Метод получения минут охоты."""
    hunting_end_time = timezone.now()
    if hunting_end_time > character.hunting_end:
        hunting_end_time = character.hunting_end
    minutes = (hunting_end_time - character.hunting_begin).seconds / 60
    return int(minutes)


async def get_exp(character: Character, exp_amount: int):
    """Метод получения опыта."""
    character.exp += exp_amount
    while character.exp >= character.exp_for_level_up:
        character.exp = character.exp - character.exp_for_level_up
        character.exp_for_level_up += (
            character.exp_for_level_up * settings.EXP_FOR_LEVEL_UP_MULTIPLIER
        )
        character.attack += character.character_class.attack_level_increase
        character.defence += character.character_class.defence_level_increase
        character.level += 1
    await character.asave(
        update_fields=("level", "exp", "exp_for_level_up", "attack", "defence")
    )
    return character


async def remove_exp(character: Character, exp_amount: int):
    """Метод отнятия опыта."""
    character.exp -= exp_amount
    if character.exp < 0:
        character.exp = 0
    await character.asave(update_fields=("exp",))
    return character


async def get_hunting_loot(character: Character):
    """Метод получения трофеев с охоты."""
    hunting_minutes = await get_hunting_minutes(character)
    exp_gained = int(character.current_location.exp * hunting_minutes)
    drop_data = {}
    drop_modifier = character.attack / character.current_location.attack
    await get_exp(character, exp_gained)
    async for drop in LocationDrop.objects.select_related(
        "item", "location"
    ).filter(location=character.current_location):
        for _minute in range(hunting_minutes):
            chance = drop.chance * drop_modifier
            success = random.uniform(0.01, 100) <= chance
            if success:
                amount = random.randint(drop.min_amount, drop.max_amount)
                item, created = await CharacterItem.objects.aget_or_create(
                    character=character, item=drop.item
                )
                if drop.item.name_with_grade not in drop_data:
                    drop_data[drop.item.name_with_grade] = 0
                drop_data[drop.item.name_with_grade] += amount
                item.amount += amount
                await item.asave(update_fields=("amount",))
    logger.info(
        f"{character} - Вышел из {character.current_location} "
        f"и получил {exp_gained} опыта и "
        f"{drop_data} за {hunting_minutes} минут"
    )
    character.current_location = None
    character.hunting_begin = None
    character.hunting_end = None
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


async def kill_character(character: Character, bot):
    """Убийство персонажа."""
    character.hunting_end = timezone.now()
    await character.asave(update_fields=("hunting_end",))
    exp_gained, drop_data = await get_hunting_loot(character)
    lost_exp = character.exp_for_level_up // 10
    await remove_exp(character, lost_exp)
    drop_text = ""
    for name, amount in drop_data.items():
        drop_text += f"<b>{name}</b> - {amount} шт.\n"
    if not drop_data:
        drop_text = "Не получено"
    user = await User.objects.aget(character=character)
    await bot.send_message(
        user.telegram_id,
        CHARACTER_KILL_MESSAGE.format(exp_gained - lost_exp, drop_text),
    )
