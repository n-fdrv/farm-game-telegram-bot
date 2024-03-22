from character.models import Character, CharacterItem, MarketplaceItem
from item.models import Etc, ItemType

from bot.character.backpack.utils import (
    add_item,
    get_bag_loot,
    get_character_item_effects,
    remove_item,
)
from bot.character.shop.utils import check_item_amount
from bot.marketplace.messages import (
    BUY_GET_MESSAGE,
    MAX_LOT_AMOUNT_MESSAGE,
    NOT_ENOUGH_CURRENCY,
    REMOVE_LOT_MESSAGE,
    SELL_GET_MESSAGE,
    SUCCESS_ADD_LOT_MESSAGE,
    SUCCESS_BUY_MESSAGE,
)
from core.config import game_config


async def get_marketplace_item(marketplace_id: int):
    """Метод проверки и получения лота."""
    if not await MarketplaceItem.objects.filter(pk=marketplace_id).aexists():
        return False
    return await MarketplaceItem.objects.select_related(
        "seller", "item", "sell_currency"
    ).aget(pk=marketplace_id)


async def get_character_item_marketplace_text(character_item: CharacterItem):
    """Метод получения текста информации о товаре."""
    additional_info = await get_character_item_effects(character_item)
    if character_item.item.type == ItemType.BAG:
        additional_info += await get_bag_loot(character_item.item)
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


async def get_marketplace_item_effects(
    marketplace_item: MarketplaceItem,
) -> str:
    """Метод получения эффектов предмета."""
    effects = ""
    if not await marketplace_item.item.effects.aexists():
        return effects
    effects = "\n<i>Эффекты:</i>\n"
    async for effect in marketplace_item.item.effects.all():
        enhance_type = game_config.ENHANCE_INCREASE
        if effect.in_percent:
            enhance_type = game_config.ENHANCE_IN_PERCENT_INCREASE
        amount = effect.amount + (
            enhance_type * marketplace_item.enhancement_level
        )
        effects += f"{effect.get_property_display()} - {amount}"
        if effect.in_percent:
            effects += "%"
        effects += "\n"
    return effects


async def get_lot_text(marketplace_item: MarketplaceItem):
    """Метод получения текста информации о товаре."""
    additional_info = await get_marketplace_item_effects(marketplace_item)
    if marketplace_item.item.type == ItemType.BAG:
        additional_info += await get_bag_loot(marketplace_item.item)
    description = marketplace_item.item.description

    return BUY_GET_MESSAGE.format(
        marketplace_item.name_with_enhance,
        marketplace_item.amount,
        description,
        additional_info,
        f"{marketplace_item.price}{marketplace_item.sell_currency.emoji}",
    )


async def buy_item(marketplace_item: MarketplaceItem, buyer: Character):
    """Метод добавления предмета на торговую площадку."""
    enough_currency = await check_item_amount(
        character=buyer,
        item=marketplace_item.sell_currency,
        amount=marketplace_item.price,
    )
    if not enough_currency:
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
