from aiogram.utils.keyboard import InlineKeyboardBuilder
from location.models import Location

from bot.command.buttons import BACK_BUTTON, NO_BUTTON, YES_BUTTON
from bot.constants.actions import character_action, location_action
from bot.constants.callback_data import CharacterData, LocationData
from bot.location.buttons import GET_DROP_MESSAGE, START_HUNTING_MESSAGE
from bot.utils.paginator import Paginator


async def location_list_keyboard(callback_data: LocationData):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    async for location in Location.objects.all():
        keyboard.button(
            text=location.name,
            callback_data=LocationData(
                action=location_action.get,
                page=callback_data.page,
                id=location.id,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=location_action.list,
        size=6,
        page=callback_data.page,
    )
    return paginator.get_paginator_with_button(
        BACK_BUTTON, character_action.get
    )


async def location_get_keyboard(callback_data: LocationData):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=START_HUNTING_MESSAGE,
        callback_data=LocationData(
            action=location_action.enter, id=callback_data.id
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=LocationData(
            action=location_action.list, page=callback_data.page
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def get_drop_keyboard():
    """Клавиатура получения дропа с локации."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=GET_DROP_MESSAGE,
        callback_data=LocationData(action=location_action.exit_location),
    )
    keyboard.adjust(1)
    return keyboard


async def exit_location_confirmation():
    """Клавиатура подтверждения выхода из локации."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=LocationData(action=location_action.exit_location),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=CharacterData(action=character_action.get),
    )
    keyboard.adjust(2)
    return keyboard
