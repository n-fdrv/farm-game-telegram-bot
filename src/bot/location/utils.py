import datetime
from random import randint

from character.models import Character
from django.utils import timezone
from item.models import EffectProperty
from location.models import Location, LocationDrop

from bot.character.utils import get_character_property
from bot.location.messages import LOCATION_GET_MESSAGE
from bot.utils.schedulers import (
    kill_character_scheduler,
)
from core.config import game_config


async def get_location_info(character: Character, location: Location) -> str:
    """Возвращает сообщение с данными о персонаже."""
    drop_data = ""
    attack = await get_character_property(character, EffectProperty.ATTACK)
    defence = await get_character_property(character, EffectProperty.DEFENCE)
    attack_buff = attack / location.attack
    drop_modifier = await get_character_property(
        character, EffectProperty.DROP
    )
    drop_buff = drop_modifier * attack_buff
    drop_effect = drop_buff * 100 - 100
    defence_buff = defence / location.defence * 100 - 100
    hunting_time = await get_character_property(
        character, EffectProperty.HUNTING_TIME
    )
    hunting_time *= defence / location.defence
    dead_text = ""
    if defence_buff < 0:
        dead_text = "☠️ Ваша защита меньше. Вы можете умереть!"
    elif defence_buff > 0:
        dead_text = "✅ Ваша защита больше. Время охоты увеличено!"
    drop_text = (
        f"✅ Ваша атака больше! "
        f"Бонус к падению предметов: +{int(drop_effect)}%"
    )
    if drop_effect < 0:
        drop_text = (
            f"❌ Ваша атака меньше! "
            f"Штраф к падению предметов: {int(drop_effect)}%"
        )

    async for location_drop in LocationDrop.objects.select_related(
        "item"
    ).filter(location=location):
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
            f"<b>{location_drop.item.name_with_type}</b> {amount}{chance}%\n"
        )

    return LOCATION_GET_MESSAGE.format(
        location.name,
        location.attack,
        location.defence,
        drop_text,
        dead_text,
        int(hunting_time),
        drop_data,
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
        return False
    return True


async def enter_location(character: Character, location: Location):
    """Вход в локацию."""
    character.current_location = location
    character.hunting_begin = timezone.now()
    dead_chance = 100 - character.defence / location.defence * 100
    hunting_time = await get_character_property(
        character, EffectProperty.HUNTING_TIME
    )
    if character.defence < location.defence:
        hunting_time *= character.defence / location.defence
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
