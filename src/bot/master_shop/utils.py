from character.models import Character, CharacterItem, RecipeShare
from item.models import Recipe

from bot.master_shop.messages import RECIPE_SHARE_GET_MESSAGE
from bot.utils.game_utils import get_item_effects


async def get_recipe_materials(character: Character, recipe: Recipe):
    """Метод получения текста материавлов для крафта."""
    text = ""
    async for material in recipe.materials.select_related("material").all():
        character_amount = 0
        exists = await CharacterItem.objects.filter(
            character=character, item=material.material
        ).aexists()
        if exists:
            character_amount = await CharacterItem.objects.filter(
                character=character, item=material.material
            ).acount()
        text += (
            f"\n{material.material.name_with_type} - "
            f"{material.amount} шт.\n"
            f"(В наличии <b>{character_amount} шт.</b>)"
        )
    return text


async def get_share_recipe_info(
    character: Character, recipe_share: RecipeShare
) -> str:
    """Получение информации о рецепте."""
    return RECIPE_SHARE_GET_MESSAGE.format(
        recipe_share.character_recipe.recipe.name_with_chance,
        recipe_share.character_recipe.character.name_with_clan,
        recipe_share.price,
        await get_item_effects(recipe_share.character_recipe.recipe.create),
        await get_recipe_materials(
            character, recipe_share.character_recipe.recipe
        ),
    )
