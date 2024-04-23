import datetime

from character.models import (
    Character,
)
from django.utils import timezone
from location.models import (
    Dungeon,
    DungeonCharacter,
    DungeonRequiredItem,
)

from bot.utils.game_utils import get_expired_text


async def get_dungeon_required_items(dungeon: Dungeon) -> str:
    """Получение информации об эффектах защиты локации."""
    items_data = ""
    async for required_item in (
        DungeonRequiredItem.objects.select_related("item")
        .filter(dungeon=dungeon)
        .order_by("-amount")
    ):
        items_data += (
            f"<b>{required_item.item.name_with_type}</b> - "
            f"<i>{required_item.amount} шт.</i>\n"
        )
    return items_data


async def check_dungeon_access(character: Character, dungeon: Dungeon):
    """Проверка доступности подземелья."""
    dungeon_character, created = await DungeonCharacter.objects.aget_or_create(
        character=character, dungeon=dungeon
    )
    if (
        created
        or dungeon_character.hunting_begin
        < timezone.now() - datetime.timedelta(hours=dungeon.cooldown_hours)
    ):
        return "Доступно"
    time_left = (
        dungeon_character.hunting_begin
        + datetime.timedelta(hours=dungeon.cooldown_hours)
        - timezone.now()
    )
    return await get_expired_text(time_left)
