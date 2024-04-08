from character.models import Character
from clan.models import Clan, ClanWarehouse
from item.models import Item

from bot.clan.warehouse.messages import (
    SUCCESS_SEND_MESSAGE,
    SUCCESS_SEND_MESSAGE_TO_USER,
)
from bot.models import User
from bot.utils.game_utils import add_item


async def send_item_from_warehouse(
    item: ClanWarehouse,
    character: Character,
    bot,
    amount: int = 1,
):
    """Отправка предмета с хранилища клана персонажу."""
    if item.amount < amount:
        amount = item.amount
    item.amount -= amount
    await add_item(
        character=character,
        item=item.item,
        amount=amount,
        enhancement_level=item.enhancement_level,
    )
    if item.amount == 0:
        await item.adelete()
    else:
        await item.asave(update_fields=("amount",))
    character_telegram_id = await User.objects.values_list(
        "telegram_id", flat=True
    ).aget(character=character)
    await bot.send_message(
        character_telegram_id,
        SUCCESS_SEND_MESSAGE_TO_USER.format(item.name_with_enhance, amount),
    )
    return True, SUCCESS_SEND_MESSAGE.format(
        item.name_with_enhance, amount, character.name_with_class
    )


async def add_clan_item(
    clan: Clan,
    item: Item,
    amount: int = 1,
    enhancement_level: int = 0,
):
    """Метод добавления предмета персонажу."""
    exists = await ClanWarehouse.objects.filter(
        clan=clan, item=item, enhancement_level=enhancement_level
    ).aexists()
    if not exists:
        clan_item = await ClanWarehouse.objects.select_related(
            "item", "clan"
        ).acreate(
            clan=clan,
            item=item,
            amount=amount,
            enhancement_level=enhancement_level,
        )
        return clan_item
    clan_item = await ClanWarehouse.objects.select_related(
        "item", "clan"
    ).aget(clan=clan, item=item, enhancement_level=enhancement_level)
    clan_item.amount += amount
    await clan_item.asave(update_fields=("amount",))
    return clan_item
