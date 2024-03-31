import datetime
import random
from random import randint

from character.models import Character, CharacterItem
from django.utils import timezone
from item.models import EffectProperty
from location.models import Location, LocationDrop
from loguru import logger

from bot.character.utils import (
    get_character_item_with_effects,
    get_character_property,
    get_elixir_with_effects_and_expired,
)
from bot.location.messages import (
    FAIL_KILL_MESSAGE,
    LOCATION_CHARACTER_GET_MESSAGE,
    LOCATION_FULL_MESSAGE,
    LOCATION_GET_MESSAGE,
    LOCATION_NOT_AVAILABLE,
    LOCATION_WEEK_STRONG_MESSAGE,
    NO_CHARACTER_CURRENT_LOCATION,
    SUCCESS_KILL_MESSAGE,
    TRY_TO_KILL_CHARACTER_WHILE_HUNTING_MESSAGE,
)
from bot.utils.schedulers import (
    hunting_end_scheduler,
    kill_character_scheduler,
)
from core.config import game_config


async def get_location_defence_effect(
    character: Character, location: Location
) -> str:
    """Получение информации об эффектах защиты локации."""
    defence = await get_character_property(character, EffectProperty.DEFENCE)
    defence_buff = defence / location.defence * 100 - 100
    if defence_buff < 0:
        return "<i>☠️ Ваша защита меньше. Вы можете умереть!</i>"
    return "<i>✅ Ваша защита больше. Время охоты увеличено!</i>"


async def get_location_attack_effect(
    character: Character, location: Location
) -> str:
    """Получение информации об эффектах защиты локации."""
    attack = await get_character_property(character, EffectProperty.ATTACK)
    attack_buff = attack / location.attack * 100 - 100
    if attack_buff < 0:
        return (
            f"<i>❌ Ваша атака меньше! "
            f"Штраф к падению предметов:</i> <b>{int(attack_buff)}%</b>"
        )
    return (
        f"<i>✅ Ваша атака больше! "
        f"Бонус к падению предметов:</i> <b>+{int(attack_buff)}%</b>"
    )


async def get_location_drop(character: Character, location: Location) -> str:
    """Получение информации об эффектах защиты локации."""
    attack = await get_character_property(character, EffectProperty.ATTACK)
    attack_buff = attack / location.attack
    drop_modifier = await get_character_property(
        character, EffectProperty.DROP
    )
    drop_buff = drop_modifier * attack_buff
    drop_data = ""
    async for location_drop in (
        LocationDrop.objects.select_related("item")
        .filter(location=location)
        .order_by("-chance")
    ):
        chance = round(location_drop.chance * drop_buff, 2)
        chance_limit = 100
        if chance > chance_limit:
            chance = chance_limit
        amount = ""
        if location_drop.max_amount > 1:
            amount = (
                f"({location_drop.min_amount}-{location_drop.max_amount}) "
            )
        drop_data += (
            f"<b>{location_drop.item.name_with_type}</b> "
            f"<i>{amount}- {chance}%</i>\n"
        )
    return drop_data


async def get_location_info(character: Character, location: Location) -> str:
    """Возвращает сообщение с данными о персонаже."""
    defence = await get_character_property(character, EffectProperty.DEFENCE)
    hunting_time = await get_character_property(
        character, EffectProperty.HUNTING_TIME
    )
    hunting_time *= defence / location.defence
    characters_in_location = await Character.objects.filter(
        current_location=location
    ).acount()
    location_exp = (
        await get_character_property(character, EffectProperty.EXP)
        * location.exp
    )
    exp_in_minute = location_exp / character.exp_for_level_up * 100
    return LOCATION_GET_MESSAGE.format(
        location.name,
        location.attack,
        location.defence,
        f"{characters_in_location}/{location.place}",
        exp_in_minute,
        await get_location_attack_effect(character, location),
        await get_location_defence_effect(character, location),
        int(hunting_time),
        await get_location_drop(character, location),
    )


async def check_location_access(character: Character, location: Location):
    """Проверка доступа в локацию."""
    check_data = [
        location.attack / character.attack,
        location.defence / character.defence,
        character.attack / location.attack,
        character.defence / location.defence,
    ]
    if max(check_data) >= game_config.LOCATION_STAT_DIFFERENCE:
        return False, LOCATION_NOT_AVAILABLE.format(
            LOCATION_WEEK_STRONG_MESSAGE
        )
    characters_in_location = await Character.objects.filter(
        current_location=location
    ).acount()
    if characters_in_location >= location.place:
        return False, LOCATION_NOT_AVAILABLE.format(LOCATION_FULL_MESSAGE)
    return True, "Успешно"


async def enter_location(character: Character, location: Location):
    """Вход в локацию."""
    character.current_location = location
    character.hunting_begin = timezone.now()
    character_defence = await get_character_property(
        character, EffectProperty.DEFENCE
    )
    dead_chance = 100 - character_defence / location.defence * 100
    hunting_time = await get_character_property(
        character, EffectProperty.HUNTING_TIME
    )
    hunting_time *= character_defence / location.defence
    character.hunting_end = timezone.now() + datetime.timedelta(
        minutes=int(hunting_time),
    )
    await character.asave(
        update_fields=("current_location", "hunting_begin", "hunting_end")
    )
    if randint(1, 100) <= dead_chance:
        end_of_hunting = timezone.now() + datetime.timedelta(
            minutes=randint(1, int(hunting_time)),
        )
        await kill_character_scheduler(character, end_of_hunting)
        return
    await hunting_end_scheduler(character)


async def location_get_character_about(character: Character) -> str:
    """Возвращает сообщение с данными о персонаже."""
    clan = "Нет"
    if character.clan:
        clan = character.clan.name_with_emoji
    return LOCATION_CHARACTER_GET_MESSAGE.format(
        character.name_with_class,
        character.level,
        clan,
        int(await get_character_property(character, EffectProperty.ATTACK)),
        int(await get_character_property(character, EffectProperty.DEFENCE)),
        "\n".join(
            [
                await get_character_item_with_effects(x)
                async for x in CharacterItem.objects.select_related(
                    "item"
                ).filter(character=character, equipped=True)
            ]
        ),
        await get_elixir_with_effects_and_expired(character),
    )


async def attack_character(attacker: Character, target: Character):
    """Обработка атаки на персонажа."""
    if attacker.current_location:
        return False, TRY_TO_KILL_CHARACTER_WHILE_HUNTING_MESSAGE
    if not target.current_location:
        return (
            False,
            NO_CHARACTER_CURRENT_LOCATION.format(target.name_with_class),
        )
    attacker_attack = (
        int(await get_character_property(attacker, EffectProperty.ATTACK)),
    )
    attacker_defence = (
        int(await get_character_property(attacker, EffectProperty.DEFENCE)),
    )
    target_attack = (
        int(await get_character_property(target, EffectProperty.ATTACK)),
    )
    target_defence = (
        int(await get_character_property(target, EffectProperty.DEFENCE)),
    )
    attack_difference = attacker_attack[0] / target_defence[0]
    defence_difference = attacker_defence[0] / target_attack[0]
    difference = (attack_difference + defence_difference) / 2
    chance = round(difference * 50, 2)
    text = (
        f"\nПерсонаж: {attacker.name_with_class} "
        f"(Атака: {attacker_attack[0]}, Защита: {attacker_defence[0]})\n"
        f"Атакует: {target.name_with_class} "
        f"(Атака: {target_attack[0]}, Защита: {target_defence[0]})\n"
        f"Шанс успеха: {chance}%"
    )
    if random.uniform(0.01, 100) <= chance:
        text += "\nУспешно"
        await kill_character_scheduler(target, timezone.now(), attacker)
        logger.info(text)
        return True, SUCCESS_KILL_MESSAGE.format(target.name_with_clan)
    await kill_character_scheduler(attacker, timezone.now(), target)
    return False, FAIL_KILL_MESSAGE.format(target.name_with_clan)
