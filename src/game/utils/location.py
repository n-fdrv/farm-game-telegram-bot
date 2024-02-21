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
