from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.clan.settings.buttons import (
    CHANGE_ACCESS_BUTTON,
    CHANGE_DESCRIPTION_BUTTON,
    CHANGE_EMOJI_BUTTON,
    REMOVE_CLAN_BUTTON,
)
from bot.clan.settings.utils import EMOJI_DATA
from bot.command.buttons import BACK_BUTTON, NO_BUTTON, YES_BUTTON
from bot.constants.actions import clan_action
from bot.constants.callback_data import ClanData
from bot.utils.paginator import Paginator


async def settings_list_keyboard(callback_data: ClanData):
    """Клавиатура подтверждения входа в клан."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=CHANGE_EMOJI_BUTTON,
        callback_data=ClanData(
            action=clan_action.settings_emoji,
            id=callback_data.id
        )
    )
    keyboard.button(
        text=CHANGE_DESCRIPTION_BUTTON,
        callback_data=ClanData(
            action=clan_action.settings_description,
            id=callback_data.id
        )
    )
    keyboard.button(
        text=CHANGE_ACCESS_BUTTON,
        callback_data=ClanData(
            action=clan_action.settings_access_confirm,
            id=callback_data.id
        )
    )
    keyboard.button(
        text=REMOVE_CLAN_BUTTON,
        callback_data=ClanData(
            action=clan_action.settings_remove,
            id=callback_data.id
        )
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=ClanData(
            action=clan_action.preview
        )
    )
    keyboard.adjust(1)
    return keyboard


async def to_settings_keyboard(callback_data: ClanData):
    """Клавиатура возвращения к настройкам."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=ClanData(action=clan_action.settings,
                               id=callback_data.id)
    )
    keyboard.adjust(1)
    return keyboard


async def settings_emoji_keyboard(callback_data: ClanData):
    """Клавиатура подтверждения входа в клан."""
    keyboard = InlineKeyboardBuilder()
    max_col = 3
    button_number = 1
    rows = []
    for emoji in EMOJI_DATA:
        keyboard.button(
            text=emoji,
            callback_data=ClanData(
                action=clan_action.settings_emoji_set,
                id=callback_data.id,
                settings_value=emoji,
                page=callback_data.page
            )
        )
        if button_number == max_col:
            rows.append(button_number)
            button_number = 1
        button_number += 1
    rows.append(1)
    keyboard.adjust(*rows)
    paginator = Paginator(
        keyboard=keyboard,
        action=clan_action.settings_emoji,
        size=6,
        page=callback_data.page,
        id=callback_data.id
    )
    return paginator.get_paginator_with_buttons_list(
        [
            [
                BACK_BUTTON,
                ClanData(
                    action=clan_action.settings,
                    id=callback_data.id
                ),
            ]
        ]
    )


async def settings_access_confirm_keyboard(callback_data: ClanData):
    """Клавиатура возвращения к настройкам."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=ClanData(action=clan_action.settings_access,
                               id=callback_data.id)
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=ClanData(action=clan_action.settings,
                               id=callback_data.id)
    )
    keyboard.adjust(2)
    return keyboard


async def settings_remove_confirm_keyboard(callback_data: ClanData):
    """Клавиатура возвращения к настройкам."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=ClanData(action=clan_action.remove,
                               id=callback_data.id)
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=ClanData(action=clan_action.settings,
                               id=callback_data.id)
    )
    keyboard.adjust(2)
    return keyboard
