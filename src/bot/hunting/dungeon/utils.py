import datetime

from character.models import (
    Character,
    CharacterItem,
)
from django.utils import timezone
from location.models import (
    Dungeon,
    DungeonCharacter,
    DungeonRequiredItem,
)

from bot.hunting.dungeon.messages import (
    NOT_READY_DUNGEON_MESSAGE,
)
from bot.utils.game_utils import get_expired_text, remove_item
from bot.utils.messages import NOT_ENOUGH_REQUIRED_ITEMS_MESSAGE


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


async def check_dungeon_access_text(character: Character, dungeon: Dungeon):
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


async def check_required_items(character: Character, dungeon: Dungeon):
    """Метод проверки наличия предмета для крафта."""
    async for required_item in DungeonRequiredItem.objects.select_related(
        "item"
    ).filter(dungeon=dungeon):
        is_exist = await character.items.filter(
            pk=required_item.item.pk
        ).aexists()
        if not is_exist:
            return False, NOT_ENOUGH_REQUIRED_ITEMS_MESSAGE
        item = await CharacterItem.objects.aget(
            character=character, item=required_item.item.pk
        )
        if item.amount < required_item.amount:
            return False, NOT_ENOUGH_REQUIRED_ITEMS_MESSAGE
    return True, "Доступно"


async def check_dungeon_access(character: Character, dungeon: Dungeon):
    """Проверка доступности подземелья."""
    dungeon_character, created = await DungeonCharacter.objects.aget_or_create(
        character=character, dungeon=dungeon
    )
    if dungeon_character.hunting_begin < timezone.now() - datetime.timedelta(
        hours=dungeon.cooldown_hours
    ):
        return await check_required_items(character, dungeon)
    return False, NOT_READY_DUNGEON_MESSAGE.format(dungeon.name_with_level)


async def enter_dungeon(character: Character, dungeon: Dungeon):
    """Обработка входа в подземелье."""
    dungeon_character, created = await DungeonCharacter.objects.aget_or_create(
        character=character, dungeon=dungeon
    )
    dungeon_character.hunting_begin = timezone.now()
    await dungeon_character.asave(update_fields=("hunting_begin",))
    async for required_item in DungeonRequiredItem.objects.select_related(
        "item"
    ).filter(dungeon=dungeon):
        await remove_item(
            character=character,
            item=required_item.item,
            amount=required_item.amount,
        )
