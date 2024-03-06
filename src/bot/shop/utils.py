import re

from character.models import Character, CharacterItem
from item.models import Item

from bot.shop.messages import ITEM_GET_MESSAGE


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
    if await item.effect.aexists():
        effects = "\nЭффекты:\n"
        async for effect in item.effect.all():
            effects += f"{effect.get_property_display()} - {effect.amount}"
            if effect.in_percent:
                effects += "%"
            effects += "\n"
    shop_text = ""
    if item.buy_price:
        shop_text += f"Покупка: {item.buy_price} золота."
    if item.sell_price:
        shop_text += f"\nПродажа: {item.sell_price} золота."
    return ITEM_GET_MESSAGE.format(
        item.name_with_type, item.description, effects, shop_text
    )
