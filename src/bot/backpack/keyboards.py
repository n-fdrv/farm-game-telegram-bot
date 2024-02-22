from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import CharacterItem

from bot.command.buttons import BACK_BUTTON
from bot.constants.actions import (
    backpack_action,
    character_action,
)
from bot.constants.callback_data import (
    BackpackData,
)
from bot.models import User
from bot.utils.paginator import Paginator


async def backpack_list_keyboard(user: User, callback_data: BackpackData):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    async for item in CharacterItem.objects.select_related("item").filter(
        character=user.character
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
        BACK_BUTTON, character_action.get
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
