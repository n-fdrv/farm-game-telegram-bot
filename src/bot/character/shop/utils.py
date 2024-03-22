import re

from character.models import Character, CharacterItem
from django.conf import settings
from item.models import Item

from bot.character.backpack.utils import add_item, remove_item
from bot.character.shop.messages import (
    CHARACTER_IN_LOCATION_MESSAGE,
    EQUIPPED_ITEM_MESSAGE,
    ITEM_GET_MESSAGE,
    NOT_ENOUGH_GOLD_MESSAGE,
    NOT_ENOUGH_ITEMS_MESSAGE,
    SUCCESS_BUY_MESSAGE,
    SUCCESS_SELL_MESSAGE,
)


async def check_item_amount(
    character: Character,
    item: Item,
    amount: int = 1,
    enhancement_level: int = 0,
) -> bool:
    """Метод проверки наличия товара у персонажа."""
    exists = await character.items.filter(pk=item.pk).aexists()
    if not exists:
        return False
    character_item = await CharacterItem.objects.aget(
        character=character, item=item, enhancement_level=enhancement_level
    )
    if character_item.amount < amount:
        return False
    return True


async def check_correct_amount(message: str):
    """Метод проверки правильности ввода количества товаров."""
    if not re.search("^[0-9]{1,16}$", message):
        return False
    if int(message) == 0:
        return False
    return True


async def get_item_info_text(item: Item):
    """Метод получения текста информации о товаре."""
    effects = ""
    if await item.effects.aexists():
        effects = "\n<b>Эффекты:</b>\n"
        async for effect in item.effects.all():
            effects += f"{effect.get_property_display()} - {effect.amount}"
            if effect.in_percent:
                effects += "%"
            effects += "\n"
    shop_text = ""
    if item.buy_price:
        shop_text += f"Покупка: <b>{item.buy_price}🟡</b> "
    if item.sell_price:
        shop_text += f"Продажа: <b>{item.sell_price}🟡</b>"
    return ITEM_GET_MESSAGE.format(
        item.name_with_type, item.description, effects, shop_text
    )


async def sell_item(character_item: CharacterItem, amount: int):
    """Метод продажи товара в магазин."""
    if character_item.equipped and character_item.amount <= amount:
        return False, EQUIPPED_ITEM_MESSAGE
    if character_item.character.current_location:
        return False, CHARACTER_IN_LOCATION_MESSAGE
    gold = await Item.objects.aget(name=settings.GOLD_NAME)
    enough_amount = await check_item_amount(
        character_item.character,
        character_item.item,
        amount,
        character_item.enhancement_level,
    )

    if not enough_amount:
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
    enough_amount = await check_item_amount(character, gold, item.buy_price)
    if not enough_amount:
        return False, NOT_ENOUGH_GOLD_MESSAGE
    await remove_item(character, gold, item.buy_price)
    await add_item(character, item)
    return True, SUCCESS_BUY_MESSAGE.format(item.name_with_type)
