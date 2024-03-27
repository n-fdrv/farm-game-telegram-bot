from aiogram.utils.keyboard import InlineKeyboardBuilder
from clan.models import ClanRequest

from bot.clan.requests.buttons import (
    ACCEPT_REQUEST_BUTTON,
    DECLINE_REQUEST_BUTTON,
)
from bot.command.buttons import (
    BACK_BUTTON,
    NO_BUTTON,
    YES_BUTTON,
)
from bot.constants.actions import clan_action
from bot.constants.callback_data import ClanData
from bot.utils.paginator import Paginator


async def create_request_confirm_keyboard(callback_data: ClanData):
    """Клавиатура подтверждения названия Клана."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=ClanData(
            action=clan_action.create_request, id=callback_data.id
        ),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=ClanData(action=clan_action.get, id=callback_data.id),
    )
    keyboard.adjust(2)
    return keyboard


async def create_request_keyboard(callback_data: ClanData):
    """Клавиатура подтверждения названия Клана."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=ClanData(action=clan_action.get, id=callback_data.id),
    )
    keyboard.adjust(1)
    return keyboard


async def request_list_keyboard(callback_data: ClanData):
    """Клавиатура подтверждения названия Клана."""
    keyboard = InlineKeyboardBuilder()
    async for clan_request in ClanRequest.objects.select_related(
        "character", "character__character_class"
    ).filter(clan__id=callback_data.id):
        keyboard.button(
            text=(
                f"{clan_request.character.name_with_class} "
                f"Ур. {clan_request.character.level}"
            ),
            callback_data=ClanData(
                action=clan_action.request_get,
                id=callback_data.id,
                character_id=clan_request.character.id,
                page=callback_data.page,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=clan_action.request_list,
        size=6,
        page=callback_data.page,
    )
    return paginator.get_paginator_with_buttons_list(
        [
            [
                BACK_BUTTON,
                ClanData(
                    action=clan_action.preview,
                ),
            ]
        ]
    )


async def request_get_keyboard(callback_data: ClanData):
    """Клавиатура подтверждения названия Клана."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=ACCEPT_REQUEST_BUTTON,
        callback_data=ClanData(
            action=clan_action.request_accept,
            id=callback_data.id,
            character_id=callback_data.character_id,
        ),
    )
    keyboard.button(
        text=DECLINE_REQUEST_BUTTON,
        callback_data=ClanData(
            action=clan_action.request_decline,
            id=callback_data.id,
            character_id=callback_data.character_id,
        ),
    )
    keyboard.adjust(2)
    return keyboard
