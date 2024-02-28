from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Skill
from item.models import Item

from bot.character.buttons import CRAFT_BUTTON
from bot.command.buttons import BACK_BUTTON
from bot.constants.actions import character_action, craft_action
from bot.constants.callback_data import CharacterData, CraftData


async def craft_list_keyboard(skill: Skill):
    """Клавиатура списка созданий."""
    keyboard = InlineKeyboardBuilder()
    async for item in Item.objects.filter(crafting_level=skill.level):
        keyboard.button(
            text=item.name_with_grade,
            callback_data=CraftData(action=craft_action.get, id=item.id),
        )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.skill_list),
    )
    keyboard.adjust(1)
    return keyboard


async def craft_get_keyboard(item: Item):
    """Клавиатура получения предмета создания."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=CRAFT_BUTTON,
        callback_data=CraftData(action=craft_action.create, id=item.pk),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CraftData(action=craft_action.list),
    )
    keyboard.adjust(1)
    return keyboard
