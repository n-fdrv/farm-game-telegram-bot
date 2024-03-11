from character.models import CharacterItem, MarketplaceItem
from item.models import Etc, ItemType

from bot.backpack.utils import (
    get_bag_loot,
    get_character_item_effects,
    remove_item,
)
from bot.marketplace.messages import SELL_GET_MESSAGE


async def get_character_item_marketplace_text(character_item: CharacterItem):
    """Метод получения текста информации о товаре."""
    additional_info = await get_character_item_effects(character_item)
    if character_item.item.type == ItemType.BAG:
        additional_info += get_bag_loot(character_item.item)
    description = character_item.item.description

    return SELL_GET_MESSAGE.format(
        character_item.name_with_enhance,
        character_item.amount,
        description,
        additional_info,
        "Пусто",
    )


async def add_item_on_marketplace(
    character_item: CharacterItem, price: int, amount: int, sell_currency: str
):
    """Метод добавления предмета на торговую площадку."""
    sell_currency = await Etc.objects.aget(name=sell_currency)
    await MarketplaceItem.objects.acreate(
        seller=character_item.character,
        item=character_item.item,
        amount=amount,
        enhancement_level=character_item.enhancement_level,
        sell_currency=sell_currency,
        price=price,
    )
    await remove_item(
        character=character_item.character,
        item=character_item.item,
        enhancement_level=character_item.enhancement_level,
        amount=amount,
    )
