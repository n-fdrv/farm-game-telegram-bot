import datetime
from random import randint

from character.models import Character
from django.utils import timezone
from item.models import EffectProperty
from location.models import Location

from bot.character.utils import get_character_property
from bot.location.messages import LOCATION_GET_MESSAGE
from bot.utils.schedulers import (
    kill_character_scheduler,
)


async def get_location_info(character: Character, location: Location) -> str:
    """Возвращает сообщение с данными о персонаже."""
    drop_data = ""
    async for item in location.drop.all():
        drop_data += f"<b>{item.name_with_type}</b>\n"
    attack = await get_character_property(character, EffectProperty.ATTACK)
    defence = await get_character_property(character, EffectProperty.DEFENCE)
    attack_buff = attack / location.attack
    drop_buff = await get_character_property(character, EffectProperty.DROP)
    drop_buff *= attack_buff * 100
    defence_buff = 100 - defence / location.defence * 100
    hunting_time = await get_character_property(
        character, EffectProperty.HUNTING_TIME
    )

    hunting_time *= defence / location.defence
    if defence_buff < 0:
        defence_buff = 0
    attack_text = f"Шанс падения предметов {int(drop_buff)}%"
    defence_text = f"Шанс погибнуть: {int(defence_buff)}%"
    return LOCATION_GET_MESSAGE.format(
        location.name,
        location.attack,
        attack_text,
        location.defence,
        defence_text,
        int(hunting_time),
        drop_data,
    )


async def enter_location(character: Character, location: Location):
    """Вход в локацию."""
    character.current_location = location
    character.hunting_begin = timezone.now()
    dead_chance = 100 - character.defence / location.defence * 100
    hunting_time = await get_character_property(
        character, EffectProperty.HUNTING_TIME
    )
    if character.defence > location.defence:
        hunting_time *= character.defence / location.defence
    character.hunting_end = timezone.now() + datetime.timedelta(
        minutes=int(hunting_time),
    )
    await character.asave(
        update_fields=("current_location", "hunting_begin", "hunting_end")
    )
    if randint(1, 100) <= dead_chance:
        end_of_hunting = timezone.now() + datetime.timedelta(
            minutes=randint(1, hunting_time),
        )
        await kill_character_scheduler(character, end_of_hunting)
