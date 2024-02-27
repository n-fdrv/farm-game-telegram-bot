from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Skill
from item.models import Item

from bot.command.buttons import BACK_BUTTON
from bot.constants.actions import character_action, craft_action
from bot.constants.callback_data import CharacterData, CraftData


async def craft_list_keyboard(skill: Skill):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    async for item in Item.objects.filter(crafting_level=skill.level):
        keyboard.button(
            text=item.name_with_grade,
            callback_data=CraftData(action=craft_action.get),
        )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.skill_list),
    )
    keyboard.adjust(1)
    return keyboard
