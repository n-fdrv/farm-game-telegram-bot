from character.models import Character, CharacterItem
from django.conf import settings
from item.models import Item

from bot.character.backpack.utils import add_item
from bot.character.shop.messages import (
    CHARACTER_IN_LOCATION_MESSAGE,
    EQUIPPED_ITEM_MESSAGE,
    NOT_ENOUGH_GOLD_MESSAGE,
    NOT_ENOUGH_ITEMS_MESSAGE,
    SUCCESS_BUY_MESSAGE,
    SUCCESS_SELL_MESSAGE,
)
from bot.utils.game_utils import get_item_amount, remove_item


async def sell_item(character_item: CharacterItem, amount: int):
    """Метод продажи товара в магазин."""
    if character_item.equipped and character_item.amount <= amount:
        return False, EQUIPPED_ITEM_MESSAGE
    if character_item.character.current_location:
        return False, CHARACTER_IN_LOCATION_MESSAGE
    gold = await Item.objects.aget(name=settings.GOLD_NAME)
    character_amount = await get_item_amount(
        character_item.character,
        character_item.item.name,
        character_item.enhancement_level,
    )
    if character_amount < amount:
        return False, NOT_ENOUGH_ITEMS_MESSAGE
    await remove_item(
        character_item.character,
        character_item.item,
        amount,
        character_item.enhancement_level,
    )
    await add_item(
        character_item.character,
        gold,
        amount * character_item.item.sell_price,
    )
    return True, SUCCESS_SELL_MESSAGE.format(
        character_item.name_with_enhance,
        amount,
        amount * character_item.item.sell_price,
    )


async def buy_item(character: Character, item: Item):
    """Метод покупки товара."""
    if character.current_location:
        return False, CHARACTER_IN_LOCATION_MESSAGE
    gold = await Item.objects.aget(name=settings.GOLD_NAME)
    character_amount = await get_item_amount(
        character,
        gold.name,
    )
    if character_amount < item.buy_price:
        return False, NOT_ENOUGH_GOLD_MESSAGE
    success, amount = await remove_item(character, gold, item.buy_price)
    await add_item(character, item)
    return True, SUCCESS_BUY_MESSAGE.format(item.name_with_type, amount)
