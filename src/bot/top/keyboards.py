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
        text=BY_EXP_BUTTON,
        callback_data=TopData(
            action=top_action.list, filter_by=top_action.by_exp
        ),
    )
    keyboard.button(
        text=BY_KILL_BUTTON,
        callback_data=TopData(
            action=top_action.list, filter_by=top_action.by_kills
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def top_list_keyboard(callback_data: TopData):
    """Клавиатура персонажа."""
    keyboard = InlineKeyboardBuilder()
    size = 6
    i = 1
    order_by = ("-level", "-exp")
    if callback_data.filter_by == top_action.by_kills:
        order_by = ("-kills",)
    if callback_data.page > 1:
        i = (callback_data.page - 1) * size + 1
    async for character in (
        Character.objects.select_related("character_class")
        .order_by(*order_by)
        .all()[:20]
    ):
        button_text = f"{i}. {character.name_with_level}"
        if callback_data.filter_by == top_action.by_kills:
            button_text = (
                f"{i} {character.name_with_class} {character.kills}🩸"
            )
        keyboard.button(
            text=button_text,
            callback_data=TopData(
                action=top_action.get,
                id=character.id,
                filter_by=callback_data.action,
            ),
        )
        i += 1
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=callback_data.action,
        size=size,
        page=callback_data.page,
        filter_by=callback_data.filter_by,
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


async def top_get_keyboard(callback_data: TopData):
    """Клавиатура возврата к превью."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=TopData(
            action=top_action.list, filter_by=callback_data.filter_by
        ),
    )
    keyboard.adjust(1)
    return keyboard
