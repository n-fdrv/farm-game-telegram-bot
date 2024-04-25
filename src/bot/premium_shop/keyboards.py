from aiogram.utils.keyboard import InlineKeyboardBuilder
from premium_shop.models import PremiumLot, PremiumLotType

from bot.command.buttons import BACK_BUTTON, NO_BUTTON, YES_BUTTON
from bot.constants.actions import premium_action
from bot.constants.callback_data import PremiumData
from bot.premium_shop.buttons import (
    BUY_BUTTON,
    DIAMOND_100_BUTTON,
    DIAMOND_300_BUTTON,
    DIAMOND_500_BUTTON,
    DIAMONDS_BUTTON,
    PREMIUM_LOTS_BUTTON,
)
from bot.utils.paginator import Paginator


async def premium_preview_keyboard():
    """Список Товаров."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=PREMIUM_LOTS_BUTTON,
        callback_data=PremiumData(action=premium_action.choose_type),
    )
    keyboard.button(
        text=DIAMONDS_BUTTON,
        callback_data=PremiumData(action=premium_action.diamonds),
    )
    keyboard.adjust(1)
    return keyboard


async def diamonds_keyboard():
    """Клавиатура алмазов."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=DIAMOND_100_BUTTON,
        url="http://127.0.0.1:8000",
    )
    keyboard.button(
        text=DIAMOND_300_BUTTON,
        url="http://127.0.0.1:8000",
    )
    keyboard.button(
        text=DIAMOND_500_BUTTON,
        url="http://127.0.0.1:8000",
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=PremiumData(action=premium_action.preview),
    )
    keyboard.adjust(1)
    return keyboard


async def premium_choose_type_keyboard():
    """Распределение клавиатуры в зависимости от категории."""
    keyboard = InlineKeyboardBuilder()
    button_number = 0
    row = []
    button_in_row = 2
    for premium_type in PremiumLotType.choices:
        keyboard.button(
            text=premium_type[1],
            callback_data=PremiumData(
                action=premium_action.list,
                type=premium_type[0],
            ),
        )
        button_number += 1
        if button_number == button_in_row:
            row.append(button_number)
            button_number = 0
    if button_number > 0:
        row.append(button_number)
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=PremiumData(action=premium_action.preview),
    )
    keyboard.adjust(*row, 1)
    return keyboard


async def premium_list_keyboard(callback_data: PremiumData):
    """Распределение клавиатуры в зависимости от категории."""
    keyboard = InlineKeyboardBuilder()
    async for lot in PremiumLot.objects.filter(type=callback_data.type):
        keyboard.button(
            text=lot.name,
            callback_data=PremiumData(
                action=premium_action.get,
                id=lot.id,
                type=callback_data.type,
                page=callback_data.page,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=premium_action.list,
        size=6,
        page=callback_data.page,
        type=callback_data.type,
    )
    return paginator.get_paginator_with_buttons_list(
        [[BACK_BUTTON, PremiumData(action=premium_action.choose_type)]]
    )


async def premium_get_keyboard(callback_data: PremiumData):
    """Распределение клавиатуры в зависимости от категории."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BUY_BUTTON,
        callback_data=PremiumData(
            action=premium_action.buy_confirm,
            id=callback_data.id,
            type=callback_data.type,
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=PremiumData(
            action=premium_action.list,
            type=callback_data.type,
            page=callback_data.page,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def premium_buy_confirm_keyboard(callback_data: PremiumData):
    """Распределение клавиатуры в зависимости от категории."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=PremiumData(
            action=premium_action.buy,
            id=callback_data.id,
            type=callback_data.type,
        ),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=PremiumData(
            action=premium_action.get,
            id=callback_data.id,
            type=callback_data.type,
            page=callback_data.page,
        ),
    )
    keyboard.adjust(2)
    return keyboard


async def premium_buy_keyboard(callback_data: PremiumData):
    """Распределение клавиатуры в зависимости от категории."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=PremiumData(
            action=premium_action.list, type=callback_data.type
        ),
    )
    keyboard.adjust(1)
    return keyboard
