from character.models import Character, CharacterItem
from item.models import Item

from bot.backpack.messages import ITEM_GET_MESSAGE


async def remove_item(character: Character, item: Item, amount: int):
    """Метод удаление предметов у персонажа."""
    exists = await character.items.filter(pk=item.pk).aexists()
    if not exists:
        return False
    character_items = await CharacterItem.objects.aget(
        character=character, item=item
    )
    character_items.amount -= amount
    if character_items.amount == 0:
        await character_items.adelete()
        return True
    await character_items.asave(update_fields=("amount",))
    return True


async def add_item(character: Character, item: Item, amount: int = 1):
    """Метод добавления предмета персонажу."""
    exists = await character.items.filter(pk=item.pk).aexists()
    if not exists:
        await character.items.aadd(item)
    character_items = await CharacterItem.objects.aget(
        character=character, item=item
    )
    character_items.amount += amount
    await character_items.asave(update_fields=("amount",))
    return True


async def get_character_item_info_text(character_item: CharacterItem):
    """Метод получения текста информации о товаре."""
    effects = ""
    if await character_item.item.effect.aexists():
        effects = "\nЭффекты:\n"
        async for effect in character_item.item.effect.all():
            effects += f"{effect.get_property_display()} - {effect.amount}"
            if effect.in_percent:
                effects += "%"
            effects += "\n"
    description = character_item.item.description
    if character_item.equipped:
        description += "\n<b>Надето</b>"
    shop_text = ""
    if character_item.item.buy_price:
        shop_text += f"Покупка: {character_item.item.buy_price} золота."
    if character_item.item.sell_price:
        shop_text += f"\nПродажа: {character_item.item.sell_price} золота."
    return ITEM_GET_MESSAGE.format(
        character_item.item.name_with_grade,
        character_item.amount,
        description,
        effects,
        shop_text,
    )


async def equip_item(item: CharacterItem):
    """Метод надевания, снятия предмета."""
    if item.equipped:
        item.equipped = False
        await item.asave(update_fields=("equipped",))
        return
    type_equipped = await item.character.items.filter(
        characteritem__equipped=True, type=item.item.type
    ).aexists()
    if type_equipped:
        equipped_item = await CharacterItem.objects.aget(
            character=item.character, item__type=item.item.type, equipped=True
        )
        equipped_item.equipped = False
        await equipped_item.asave(update_fields=("equipped",))
    item.equipped = True
    await item.asave(update_fields=("equipped",))
