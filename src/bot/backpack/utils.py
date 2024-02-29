from character.models import Character, CharacterItem
from item.models import Item


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
