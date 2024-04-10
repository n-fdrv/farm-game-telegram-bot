import random

from character.models import (
    Character,
    CharacterItem,
    CharacterRecipe,
    RecipeShare,
)
from django.conf import settings
from item.models import Item, Recipe
from loguru import logger

from bot.master_shop.messages import (
    CHARACTER_RECIPE_GET_MESSAGE,
    FAIL_CRAFT_MESSAGE,
    NOT_ENOUGH_ITEMS_MESSAGE,
    RECIPE_SHARE_GET_MESSAGE,
    SHARE_RECIPE_USED_MESSAGE_TO_MASTER,
    SUCCESS_CRAFT_MESSAGE,
)
from bot.models import User
from bot.utils.game_utils import add_item, get_item_effects, remove_item
from bot.utils.messages import (
    NOT_ENOUGH_GOLD_MESSAGE,
    NOT_UNKNOWN_ERROR_MESSAGE,
)


async def get_recipe_materials(character: Character, recipe: Recipe):
    """Метод получения текста материавлов для крафта."""
    text = ""
    async for material in recipe.materials.select_related("material").all():
        character_amount = 0
        exists = await CharacterItem.objects.filter(
            character=character, item=material.material
        ).aexists()
        if exists:
            character_amount = await CharacterItem.objects.values_list(
                "amount", flat=True
            ).aget(character=character, item=material.material)
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


async def get_character_recipe_info(character_recipe: CharacterRecipe) -> str:
    """Получение информации о рецепте."""
    return CHARACTER_RECIPE_GET_MESSAGE.format(
        character_recipe.recipe.name_with_chance,
        await get_item_effects(character_recipe.recipe.create),
        await get_recipe_materials(
            character_recipe.character, character_recipe.recipe
        ),
    )


async def check_crafting_items(
    character: Character, recipe: [RecipeShare, Recipe]
):
    """Метод проверки наличия предмета для крафта."""
    if type(recipe) is RecipeShare:
        recipe = recipe.character_recipe.recipe
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


async def craft_item(
    character: Character, recipe: [RecipeShare, Recipe], bot=None
):
    """Крафт предмета."""
    if not await check_crafting_items(character, recipe):
        return False, NOT_ENOUGH_ITEMS_MESSAGE
    if type(recipe) is RecipeShare:
        gold = await Item.objects.aget(name=settings.GOLD_NAME)
        removed = await remove_item(character, gold, recipe.price)
        if not removed:
            return False, NOT_ENOUGH_GOLD_MESSAGE
        await add_item(recipe.character_recipe.character, gold, recipe.price)
        master_telegram_id = await User.objects.values_list(
            "telegram_id", flat=True
        ).aget(character=recipe.character_recipe.character)
        if bot and character != recipe.character_recipe.character:
            await bot.send_message(
                chat_id=master_telegram_id,
                text=SHARE_RECIPE_USED_MESSAGE_TO_MASTER.format(
                    character.name_with_clan,
                    recipe.character_recipe.recipe.name_with_chance,
                    recipe.price,
                ),
            )
        recipe = recipe.character_recipe.recipe
    async for material in recipe.materials.select_related("material").all():
        removed = await remove_item(
            character, material.material, material.amount
        )
        if not removed:
            logger.error(
                "Произошла ошибка при крафте предмета: "
                f"Character: {character} | Recipe: {recipe}"
            )
            return False, NOT_UNKNOWN_ERROR_MESSAGE
    success = random.randint(1, 100) <= recipe.chance
    if success:
        await add_item(character, recipe.create, 1)
        return True, SUCCESS_CRAFT_MESSAGE.format(recipe.create.name_with_type)
    return False, FAIL_CRAFT_MESSAGE
