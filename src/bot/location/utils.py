import datetime
from random import randint

from character.models import Character
from django.utils import timezone
from location.models import Location

from bot.location.messages import LOCATION_GET_MESSAGE
from bot.utils.schedulers import (
    kill_character_scheduler,
)


async def get_location_info(location: Location) -> str:
    """Возвращает сообщение с данными о персонаже."""
    drop_data = ""
    async for item in location.drop.all():
        drop_data += f"<b>{item.name_with_grade}</b>\n"
    return LOCATION_GET_MESSAGE.format(
        location.name,
        location.attack,
        location.defence,
        drop_data,
    )


async def enter_location(character: Character, location: Location):
    """Вход в локацию."""
    character.current_location = location
    character.hunting_begin = timezone.now()
    dead_chance = 100 - character.defence / location.defence * 100
    farm_seconds = (
        character.max_hunting_time.hour * 3600
        + character.max_hunting_time.minute * 60
        + character.max_hunting_time.second
    )
    if character.defence > location.defence:
        farm_seconds *= character.defence / location.defence
    character.hunting_end = timezone.now() + datetime.timedelta(
        seconds=farm_seconds,
    )
    await character.asave(
        update_fields=("current_location", "hunting_begin", "hunting_end")
    )
    if randint(1, 100) <= dead_chance:
        end_of_hunting = timezone.now() + datetime.timedelta(
            seconds=randint(1, farm_seconds),
        )
        await kill_character_scheduler(character, end_of_hunting)
