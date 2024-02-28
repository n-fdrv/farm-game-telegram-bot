from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character
from item.models import Recipe

from bot.character.buttons import CRAFT_BUTTON
from bot.command.buttons import BACK_BUTTON
from bot.constants.actions import character_action, craft_action
from bot.constants.callback_data import CharacterData, CraftData


async def craft_list_keyboard(character: Character):
    """Клавиатура списка созданий."""
    keyboard = InlineKeyboardBuilder()
    async for recipe in character.recipes.all():
        keyboard.button(
            text=recipe.get_name(),
            callback_data=CraftData(action=craft_action.get, id=recipe.id),
        )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.skill_list),
    )
    keyboard.adjust(1)
    return keyboard


async def craft_get_keyboard(recipe: Recipe):
    """Клавиатура получения предмета создания."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=CRAFT_BUTTON.format(recipe.chance),
        callback_data=CraftData(action=craft_action.create, id=recipe.pk),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CraftData(action=craft_action.list),
    )
    keyboard.adjust(1)
    return keyboard
