from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character
from clan.models import Clan

from bot.clan.members.buttons import (
    KICK_CHARACTER_BUTTON,
)
from bot.command.buttons import (
    BACK_BUTTON,
    NO_BUTTON,
    YES_BUTTON,
)
from bot.constants.actions import clan_action
from bot.constants.callback_data import ClanData
from bot.utils.paginator import Paginator


async def members_list_keyboard(callback_data: ClanData):
    """Клавиатура подтверждения входа в клан."""
    keyboard = InlineKeyboardBuilder()
    async for character in (
        Character.objects.select_related("character_class")
        .order_by("-level", "-exp")
        .filter(clan__id=callback_data.id)
    ):
        keyboard.button(
            text=f"{character.name_with_class} " f"Ур. {character.level}",
            callback_data=ClanData(
                action=clan_action.members_get,
                id=callback_data.id,
                character_id=character.id,
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


async def members_get_keyboard(callback_data: ClanData, viewer: Character):
    """Клавиатура подтверждения входа в клан."""
    keyboard = InlineKeyboardBuilder()
    clan = await Clan.objects.select_related("leader").aget(
        pk=callback_data.id
    )
    if clan.leader == viewer and viewer.pk != callback_data.character_id:
        keyboard.button(
            text=KICK_CHARACTER_BUTTON,
            callback_data=ClanData(
                action=clan_action.member_kick_confirm,
                id=callback_data.id,
                character_id=callback_data.character_id,
                page=callback_data.page,
            ),
        )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=ClanData(
            action=clan_action.members,
            id=callback_data.id,
            page=callback_data.page,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def member_kick_confirm_keyboard(callback_data: ClanData):
    """Клавиатура подтверждения входа в клан."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=ClanData(
            action=clan_action.member_kick,
            id=callback_data.id,
            character_id=callback_data.character_id,
            page=callback_data.page,
        ),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=ClanData(
            action=clan_action.members_get,
            id=callback_data.id,
            character_id=callback_data.character_id,
            page=callback_data.page,
        ),
    )
    keyboard.adjust(2)
    return keyboard


async def member_kick_keyboard(callback_data: ClanData):
    """Клавиатура подтверждения входа в клан."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=ClanData(
            action=clan_action.members,
            id=callback_data.id,
            page=callback_data.page,
        ),
    )

    keyboard.adjust(1)
    return keyboard
