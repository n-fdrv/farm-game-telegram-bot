from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character
from location.models import Dungeon

from bot.command.buttons import BACK_BUTTON, NO_BUTTON, YES_BUTTON
from bot.constants.actions import (
    character_action,
    dungeon_action,
)
from bot.constants.callback_data import (
    DungeonData,
)
from bot.hunting.dungeon.buttons import ENTER_DUNGEON_BUTTON
from bot.utils.paginator import Paginator


async def dungeon_list_keyboard(
    character: Character, callback_data: DungeonData
):
    """Клавиатура списка локаций."""
    keyboard = InlineKeyboardBuilder()
    async for dungeon in Dungeon.objects.order_by("min_level").filter(
        min_level__lte=character.level, max_level__gte=character.level
    ):
        keyboard.button(
            text=dungeon.name_with_level,
            callback_data=DungeonData(
                action=dungeon_action.get,
                page=callback_data.page,
                id=dungeon.id,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=dungeon_action.list,
        size=6,
        page=callback_data.page,
    )
    return paginator.get_paginator_with_button(
        BACK_BUTTON, character_action.get
    )


async def dungeon_get_keyboard(callback_data: DungeonData):
    """Клавиатура локации."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=ENTER_DUNGEON_BUTTON,
        callback_data=DungeonData(
            action=dungeon_action.enter_confirm, id=callback_data.id
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=DungeonData(
            action=dungeon_action.list, page=callback_data.page
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def enter_dungeon_confirm_keyboard(callback_data: DungeonData):
    """Клавиатура подтверждения входа в подземелье."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=DungeonData(action=dungeon_action.enter),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=DungeonData(
            action=dungeon_action.get, id=callback_data.id
        ),
    )
    keyboard.adjust(2)
    return keyboard
