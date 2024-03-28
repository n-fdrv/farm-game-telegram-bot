from aiogram.utils.keyboard import InlineKeyboardBuilder
from clan.models import ClanWar
from django.db.models import Q

from bot.clan.wars.buttons import ACCEPT_WAR_BUTTON, END_WAR_BUTTON
from bot.command.buttons import (
    BACK_BUTTON,
    NO_BUTTON,
    YES_BUTTON,
)
from bot.constants.actions import clan_action
from bot.constants.callback_data import ClanData
from bot.utils.paginator import Paginator


async def wars_list_keyboard(callback_data: ClanData):
    """Клавиатура подтверждения входа в клан."""
    keyboard = InlineKeyboardBuilder()
    async for clan_war in (
        ClanWar.objects.select_related("clan", "enemy")
        .order_by("accepted")
        .filter(Q(clan__id=callback_data.id) | Q(enemy__id=callback_data.id))
    ):
        button_text = f"{clan_war.clan.name_with_emoji}"
        if clan_war.clan.id == callback_data.id:
            button_text = f"{clan_war.enemy.name_with_emoji}"
        if clan_war.accepted:
            button_text += "⚔️"
        else:
            button_text += "🗡"
        keyboard.button(
            text=button_text,
            callback_data=ClanData(
                action=clan_action.wars_get,
                id=callback_data.id,
                war_id=clan_war.id,
                page=callback_data.page,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=clan_action.wars,
        size=6,
        page=callback_data.page,
        id=callback_data.id,
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


async def wars_get_keyboard(callback_data: ClanData, clan_war: ClanWar):
    """Клавиатура подтверждения входа в клан."""
    keyboard = InlineKeyboardBuilder()
    if clan_war.enemy.id == callback_data.id and not clan_war.accepted:
        keyboard.button(
            text=ACCEPT_WAR_BUTTON,
            callback_data=ClanData(
                action=clan_action.wars_accept_confirm,
                id=callback_data.id,
                war_id=callback_data.war_id,
                page=callback_data.page,
            ),
        )
    elif clan_war.accepted:
        keyboard.button(
            text=END_WAR_BUTTON,
            callback_data=ClanData(
                action=clan_action.wars_end_confirm,
                id=callback_data.id,
                war_id=callback_data.war_id,
                page=callback_data.page,
            ),
        )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=ClanData(
            action=clan_action.wars,
            id=callback_data.id,
            page=callback_data.page,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def wars_accept_confirm_keyboard(callback_data: ClanData):
    """Клавиатура подтверждения входа в клан."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=ClanData(
            action=clan_action.wars_accept,
            id=callback_data.id,
            war_id=callback_data.war_id,
            page=callback_data.page,
        ),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=ClanData(
            action=clan_action.wars_get,
            id=callback_data.id,
            war_id=callback_data.war_id,
            page=callback_data.page,
        ),
    )
    keyboard.adjust(2)
    return keyboard


async def wars_end_confirm_keyboard(callback_data: ClanData):
    """Клавиатура подтверждения входа в клан."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=ClanData(
            action=clan_action.wars_end,
            id=callback_data.id,
            war_id=callback_data.war_id,
            page=callback_data.page,
        ),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=ClanData(
            action=clan_action.wars_get,
            id=callback_data.id,
            war_id=callback_data.war_id,
            page=callback_data.page,
        ),
    )
    keyboard.adjust(2)
    return keyboard
