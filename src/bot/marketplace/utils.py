from character.models import Character, CharacterItem, MarketplaceItem
from item.models import Etc, ItemType

from bot.marketplace.messages import (
    BUY_GET_MESSAGE,
    MAX_LOT_AMOUNT_MESSAGE,
    NOT_ENOUGH_CURRENCY,
    REMOVE_LOT_MESSAGE,
    SUCCESS_ADD_LOT_MESSAGE,
    SUCCESS_BUY_MESSAGE,
)
from bot.utils.game_utils import (
    add_item,
    get_bag_loot,
    get_item_amount,
    get_item_effects,
    remove_item,
)
from core.config import game_config


async def get_marketplace_item(marketplace_id: int):
    """Метод проверки и получения лота."""
    if not await MarketplaceItem.objects.filter(pk=marketplace_id).aexists():
        return False
    return await MarketplaceItem.objects.select_related(
        "seller", "item", "sell_currency", "seller__clan"
    ).aget(pk=marketplace_id)


async def add_item_on_marketplace(
    character_item: CharacterItem, price: int, amount: int, sell_currency: str
):
    """Метод добавления предмета на торговую площадку."""
    lots_amount = await MarketplaceItem.objects.filter(
        seller=character_item.character
    ).acount()
    if lots_amount >= game_config.MAX_LOT_AMOUNT:
        return False, MAX_LOT_AMOUNT_MESSAGE
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
    return True, SUCCESS_ADD_LOT_MESSAGE


async def get_lot_text(marketplace_item: MarketplaceItem):
    """Метод получения текста информации о товаре."""
    additional_info = await get_item_effects(marketplace_item)
    if marketplace_item.item.type == ItemType.BAG:
        additional_info += await get_bag_loot(marketplace_item.item)
    description = marketplace_item.item.description

    return BUY_GET_MESSAGE.format(
        marketplace_item.name_with_enhance,
        marketplace_item.amount,
        description,
        additional_info,
        marketplace_item.seller.name_with_clan,
        f"{marketplace_item.price}{marketplace_item.sell_currency.emoji}",
    )


async def buy_item(marketplace_item: MarketplaceItem, buyer: Character):
    """Метод добавления предмета на торговую площадку."""
    character_amount = await get_item_amount(
        buyer,
        marketplace_item.sell_currency.name,
    )
    if character_amount < marketplace_item.price:
        return False, NOT_ENOUGH_CURRENCY.format(
            marketplace_item.sell_currency.emoji
        )
    await remove_item(
        character=buyer,
        item=marketplace_item.sell_currency,
        amount=marketplace_item.price,
    )
    price_after_tax = int(
        marketplace_item.price
        - marketplace_item.price / game_config.MARKETPLACE_TAX
    )
    await add_item(
        character=marketplace_item.seller,
        item=marketplace_item.sell_currency,
        amount=price_after_tax,
    )
    await add_item(
        character=buyer,
        item=marketplace_item.item,
        amount=marketplace_item.amount,
        enhancement_level=marketplace_item.enhancement_level,
    )
    await marketplace_item.adelete()
    return True, SUCCESS_BUY_MESSAGE.format(
        marketplace_item.name_with_enhance,
        f"{marketplace_item.price}{marketplace_item.sell_currency.emoji}",
    )


async def remove_lot(marketplace_item: MarketplaceItem):
    """Метод добавления предмета на торговую площадку."""
    await add_item(
        character=marketplace_item.seller,
        item=marketplace_item.item,
        amount=marketplace_item.amount,
        enhancement_level=marketplace_item.enhancement_level,
    )
    await marketplace_item.adelete()
    return True, REMOVE_LOT_MESSAGE.format(marketplace_item.name_with_enhance)
