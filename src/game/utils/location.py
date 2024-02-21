import datetime

from django.utils import timezone

from game.models import Character, Location

from bot.constants.messages import location_messages


async def get_location_info(character: Character, location: Location) -> str:
    """Возвращает сообщение с данными о персонаже."""
    drop_data = ""
    async for item in location.drop.all():
        drop_data += f"- <b>{item.name}</b>\n"
    drop_multiplier = character.power / location.required_power * 100 - 100
    drop_text = f"штраф {drop_multiplier}"
    if drop_multiplier > 0:
        drop_text = f"бонус {drop_multiplier}"
    return location_messages.LOCATION_GET_MESSAGE.format(
        location.name,
        location.required_power,
        character.power - location.required_power,
        drop_text,
        drop_data,
    )


async def enter_location(character: Character, location: Location):
    """Вход в локацию."""
    character.current_location = location
    character.hunting_begin = timezone.now()
    character.hunting_end = timezone.now() + datetime.timedelta(
        hours=character.max_hunting_time.hour,
        minutes=character.max_hunting_time.minute,
        seconds=character.max_hunting_time.second,
    )
    await character.asave(
        update_fields=("current_location", "hunting_begin", "hunting_end")
    )
