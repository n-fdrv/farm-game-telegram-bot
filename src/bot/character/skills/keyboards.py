from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character, CharacterSkill, SkillType

from bot.character.skills.buttons import (
    ACTIVE_BUTTON,
    RECIPE_BUTTON,
    TOGGLE_OFF_BUTTON,
    TOGGLE_ON_BUTTON,
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
    async for character_skill in CharacterSkill.objects.select_related(
        "skill"
    ).filter(character=character):
        keyboard.button(
            text=character_skill.skill.name_with_level,
            callback_data=CharacterData(
                action=character_action.skill_get,
                id=character_skill.id,
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


async def skill_get_keyboard(character_skill: CharacterSkill):
    """Клавиатура выбора класса персонажа."""
    keyboard = InlineKeyboardBuilder()
    if character_skill.skill.name == "Мастер Создания":
        keyboard.button(
            text=RECIPE_BUTTON,
            callback_data=CraftData(action=craft_action.list),
        )
    if character_skill.skill.type == SkillType.TOGGLE:
        button_text = TOGGLE_ON_BUTTON
        if character_skill.turn_on:
            button_text = TOGGLE_OFF_BUTTON
        keyboard.button(
            text=button_text,
            callback_data=CharacterData(
                action=character_action.skill_toggle, id=character_skill.pk
            ),
        )
    elif character_skill.skill.type == SkillType.ACTIVE:
        keyboard.button(
            text=ACTIVE_BUTTON,
            callback_data=CharacterData(
                action=character_action.skill_use, id=character_skill.pk
            ),
        )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.skill_list),
    )
    keyboard.adjust(1)
    return keyboard


async def skill_use_keyboard():
    """Клавиатура выбора класса персонажа."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.skill_list),
    )
    keyboard.adjust(1)
    return keyboard
