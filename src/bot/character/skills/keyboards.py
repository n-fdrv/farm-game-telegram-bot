from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character, Skill

from bot.character.skills.buttons import (
    RECIPE_BUTTON,
)
from bot.command.buttons import BACK_BUTTON
from bot.constants.actions import (
    character_action,
    craft_action,
)
from bot.constants.callback_data import (
    CharacterData,
    CraftData,
)
from bot.utils.paginator import Paginator


async def skill_list_keyboard(
    character: Character, callback_data: CharacterData
):
    """Клавиатура выбора класса персонажа."""
    keyboard = InlineKeyboardBuilder()
    async for skill in character.skills.all():
        keyboard.button(
            text=skill.name_with_level,
            callback_data=CharacterData(
                action=character_action.skill_get,
                id=skill.id,
                page=callback_data.page,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=character_action.skill_list,
        size=6,
        page=callback_data.page,
    )
    return paginator.get_paginator_with_button(
        BACK_BUTTON, character_action.get
    )


async def skill_get_keyboard(skill: Skill):
    """Клавиатура выбора класса персонажа."""
    keyboard = InlineKeyboardBuilder()
    # TODO Улучшение способностей
    if skill.name == "Мастер Создания":
        keyboard.button(
            text=RECIPE_BUTTON,
            callback_data=CraftData(action=craft_action.list),
        )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.skill_list),
    )
    keyboard.adjust(1)
    return keyboard
