from character.models import Character, CharacterItem
from item.models import Item, Recipe

from bot.craft.messages import CRAFTING_GET_MESSAGE


async def get_item_effects_text(item: Item):
    """Метод получения текста эффектов предмета."""
    text = ""
    async for effect in item.effect.all():
        text += f"{effect.get_property_display()} - {effect.amount}"
        if effect.in_percent:
            text += "%"
        text += "\n"
    return text


async def get_crafting_item_text(recipe: Recipe):
    """Метод получения текста материавлов для крафта."""
    text = ""
    async for material in recipe.materials.select_related("material").all():
        text += (
            f"{material.material.name_with_grade} - "
            f"{material.amount} шт.\n"
        )
    return CRAFTING_GET_MESSAGE.format(
        recipe.create.name_with_grade,
        await get_item_effects_text(recipe.create),
        text,
    )


async def check_crafting_items(character: Character, recipe: Recipe):
    """Метод проверки наличия предмета для крафта."""
    async for material in recipe.materials.select_related("material").all():
        is_exist = await character.items.filter(
            pk=material.material.pk
        ).acount()
        if not is_exist:
            return False
        item = await CharacterItem.objects.aget(
            character=character, item=material.material
        )
        if item.amount < material.amount:
            return False
    return True
