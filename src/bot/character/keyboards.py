from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character, CharacterClass, Skill

from bot.character.buttons import (
    ABOUT_BUTTON,
    BACKPACK_BUTTON,
    CLASS_CHOOSE_BUTTON,
    EXIT_LOCATION_BUTTON,
    LOCATIONS_BUTTON,
    RECIPE_BUTTON,
    SHOP_BUTTON,
    SKILLS_BUTTON,
)
from bot.command.buttons import BACK_BUTTON, YES_BUTTON
from bot.constants.actions import (
    backpack_action,
    character_action,
    craft_action,
    location_action,
    shop_action,
)
from bot.constants.callback_data import (
    BackpackData,
    CharacterData,
    CraftData,
    LocationData,
    ShopData,
)
from bot.utils.paginator import Paginator


async def character_get_keyboard(character: Character):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    if character.current_location:
        keyboard.button(
            text=EXIT_LOCATION_BUTTON,
            callback_data=LocationData(
                action=location_action.exit_location_confirm
            ),
        )
    else:
        keyboard.button(
            text=SHOP_BUTTON,
            callback_data=ShopData(action=shop_action.get),
        )
    keyboard.button(
        text=LOCATIONS_BUTTON,
        callback_data=LocationData(action=location_action.list),
    )
    keyboard.button(
        text=BACKPACK_BUTTON,
        callback_data=BackpackData(action=backpack_action.list),
    )
    keyboard.button(
        text=SKILLS_BUTTON,
        callback_data=CharacterData(action=character_action.skill_list),
    )
    keyboard.button(
        text=ABOUT_BUTTON,
        callback_data=CharacterData(action=character_action.about),
    )
    keyboard.adjust(1)
    return keyboard


async def confirm_nickname_keyboard():
    """Клавиатура подтверждения выбора никнейма."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=CharacterData(
            action=character_action.class_list,
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.get),
    )
    keyboard.adjust(1)
    return keyboard


async def choose_class_keyboard():
    """Клавиатура выбора класса персонажа."""
    keyboard = InlineKeyboardBuilder()
    async for character_class in CharacterClass.objects.all():
        keyboard.button(
            text=character_class.emoji_name,
            callback_data=CharacterData(
                action=character_action.class_get, id=character_class.id
            ),
        )
    keyboard.adjust(1)
    return keyboard


async def class_get_keyboard(callback_data: CharacterData):
    """Клавиатура выбора класса персонажа."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=CLASS_CHOOSE_BUTTON,
        callback_data=CharacterData(
            action=character_action.create, id=callback_data.id
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.class_list),
    )
    keyboard.adjust(1)
    return keyboard


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
