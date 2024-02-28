from item.models import Item

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


async def get_crafting_item_text(item: Item):
    """Метод получения текста материавлов для крафта."""
    text = ""
    async for material in item.used_in_craft.select_related(
        "crafting_item"
    ).all():
        text += (
            f"{material.crafting_item.name_with_grade} - "
            f"{material.amount} шт.\n"
        )
    return CRAFTING_GET_MESSAGE.format(
        item.name_with_grade, await get_item_effects_text(item), text
    )
