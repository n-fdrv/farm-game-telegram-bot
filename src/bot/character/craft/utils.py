import random

from character.models import Character, CharacterItem
from item.models import Recipe
from loguru import logger

from bot.character.craft.messages import CRAFTING_GET_MESSAGE
from bot.utils.game_utils import add_item, get_item_effects, remove_item


async def get_crafting_item_text(recipe: Recipe):
    """Метод получения текста материавлов для крафта."""
    text = ""
    async for material in recipe.materials.select_related("material").all():
        text += (
            f"{material.material.name_with_type} - " f"{material.amount} шт.\n"
        )
    return CRAFTING_GET_MESSAGE.format(
        recipe.create.name_with_type,
        await get_item_effects(recipe.create),
        text,
    )


async def check_crafting_items(character: Character, recipe: Recipe):
    """Метод проверки наличия предмета для крафта."""
    async for material in recipe.materials.select_related("material").all():
        is_exist = await character.items.filter(
            pk=material.material.pk
        ).aexists()
        if not is_exist:
            return False
        item = await CharacterItem.objects.aget(
            character=character, item=material.material
        )
        if item.amount < material.amount:
            return False
    return True


async def craft_item(character: Character, recipe: Recipe):
    """Метод крафта предмета."""
    async for material in recipe.materials.select_related("material").all():
        removed = await remove_item(
            character, material.material, material.amount
        )
        if not removed:
            logger.error(
                "Произошла ошибка при крафте предмета: "
                f"Character: {character} | Recipe: {recipe}"
            )
            return False
    success = random.randint(1, 100) <= recipe.chance
    if success:
        await add_item(character, recipe.create, 1)
        return True
    return False
