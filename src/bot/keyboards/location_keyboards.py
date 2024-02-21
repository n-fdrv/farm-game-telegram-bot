from aiogram.utils.keyboard import InlineKeyboardBuilder
from game.models import Location

from bot.constants.actions import character_action, location_action
from bot.constants.buttons import (
    location_buttons,
    main_buttons,
)
from bot.constants.callback_data import LocationData
from bot.utils.paginator import Paginator


async def location_list(callback_data: LocationData):
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
        main_buttons.BACK_BUTTON, character_action.get
    )


async def location_get(callback_data: LocationData):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=location_buttons.START_HUNTING_MESSAGE,
        callback_data=LocationData(
            action=location_action.enter, id=callback_data.id
        ),
    )
    keyboard.button(
        text=main_buttons.BACK_BUTTON,
        callback_data=LocationData(
            action=location_action.list, page=callback_data.page
        ),
    )
    keyboard.adjust(1)
    return keyboard
