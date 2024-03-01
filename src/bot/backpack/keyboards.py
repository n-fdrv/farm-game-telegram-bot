from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import CharacterItem
from item.models import ItemType

from bot.command.buttons import BACK_BUTTON
from bot.constants.actions import (
    backpack_action,
    character_action,
)
from bot.constants.callback_data import (
    BackpackData,
    CharacterData,
)
from bot.models import User
from bot.utils.paginator import Paginator


async def backpack_preview_keyboard():
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    button_number = 0
    row = []
    button_in_row = 2
    for item_type in ItemType.choices:
        keyboard.button(
            text=item_type[1],
            callback_data=BackpackData(
                action=backpack_action.list,
                type=item_type[0],
            ),
        )
        button_number += 1
        if button_number == button_in_row:
            row.append(button_number)
            button_number = 0
    row.append(button_number)
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.get),
    )
    keyboard.adjust(*row, 1)
    return keyboard


async def backpack_list_keyboard(user: User, callback_data: BackpackData):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    async for item in CharacterItem.objects.select_related("item").filter(
        character=user.character, item__type=callback_data.type
    ):
        keyboard.button(
            text=f"{item.item.name_with_grade} - {item.amount} шт.",
            callback_data=BackpackData(
                action=backpack_action.get,
                page=callback_data.page,
                id=item.id,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=backpack_action.list,
        size=6,
        page=callback_data.page,
    )
    return paginator.get_paginator_with_button(
        BACK_BUTTON, backpack_action.preview
    )


async def item_get_keyboard(callback_data: BackpackData):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    # TODO Использовать/надеть предмет
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=BackpackData(
            action=backpack_action.list, page=callback_data.page
        ),
    )
    keyboard.adjust(1)
    return keyboard
