from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character

from bot.command.buttons import (
    BACK_BUTTON,
)
from bot.constants.actions import top_action
from bot.constants.callback_data import TopData
from bot.top.buttons import BY_EXP_BUTTON, BY_KILL_BUTTON
from bot.utils.paginator import Paginator


async def top_preview_keyboard():
    """Клавиатура персонажа."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BY_EXP_BUTTON, callback_data=TopData(action=top_action.by_exp)
    )
    keyboard.button(
        text=BY_KILL_BUTTON,
        callback_data=TopData(action=top_action.by_kills),
    )
    keyboard.adjust(1)
    return keyboard


async def top_by_exp_keyboard(callback_data: TopData):
    """Клавиатура персонажа."""
    keyboard = InlineKeyboardBuilder()
    size = 6
    i = 1
    if callback_data.page > 1:
        i = (callback_data.page - 1) * size + 1
    async for character in (
        Character.objects.select_related("character_class")
        .order_by("-level", "-exp")
        .all()[:20]
    ):
        keyboard.button(
            text=f"{i}. {character.name_with_level}",
            callback_data=TopData(
                action=top_action.get,
                id=character.id,
            ),
        )
        i += 1
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=top_action.by_exp,
        size=size,
        page=callback_data.page,
    )
    return paginator.get_paginator_with_buttons_list(
        [
            [
                BACK_BUTTON,
                TopData(
                    action=top_action.preview,
                ),
            ]
        ]
    )


async def top_by_kill_keyboard(callback_data: TopData):
    """Клавиатура персонажа."""
    keyboard = InlineKeyboardBuilder()
    size = 6
    i = 1
    if callback_data.page > 1:
        i = (callback_data.page - 1) * size + 1
    async for character in (
        Character.objects.select_related("character_class")
        .order_by("-kills")
        .all()[:20]
    ):
        keyboard.button(
            text=f"{i}. {character.name_with_kills}",
            callback_data=TopData(
                action=top_action.get,
                id=character.id,
            ),
        )
        i += 1
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=top_action.by_kills,
        size=size,
        page=callback_data.page,
    )
    return paginator.get_paginator_with_buttons_list(
        [
            [
                BACK_BUTTON,
                TopData(
                    action=top_action.preview,
                ),
            ]
        ]
    )


async def to_top_preview_keyboard():
    """Клавиатура возврата к превью."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BACK_BUTTON, callback_data=TopData(action=top_action.preview)
    )
    keyboard.adjust(1)
    return keyboard
