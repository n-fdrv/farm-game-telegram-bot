from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character
from clan.models import ClanBoss, ClanBossClan

from bot.clan.bosses.buttons import ACCEPT_RAID_BUTTON, DECLINE_RAID_BUTTON
from bot.command.buttons import (
    BACK_BUTTON,
)
from bot.constants.actions import (
    clan_action,
    clan_bosses_action,
)
from bot.constants.callback_data import (
    ClanBossesData,
    ClanData,
)
from bot.utils.paginator import Paginator


async def clan_bosses_list_keyboard(callback_data: ClanBossesData):
    """Клавиатура персонажа."""
    keyboard = InlineKeyboardBuilder()
    async for boss in ClanBoss.objects.all():
        keyboard.button(
            text=boss.name_with_power,
            callback_data=ClanBossesData(
                action=clan_bosses_action.get,
                id=boss.pk,
                page=callback_data.page,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=clan_bosses_action.list,
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


async def clan_bosses_get_keyboard(character: Character, boss: ClanBoss):
    """Клавиатура возврата к превью."""
    keyboard = InlineKeyboardBuilder()
    if character.clan.leader == character:
        btn_text = ACCEPT_RAID_BUTTON
        if await ClanBossClan.objects.filter(clan=character.clan).aexists():
            btn_text = DECLINE_RAID_BUTTON
        keyboard.button(
            text=btn_text,
            callback_data=ClanBossesData(
                action=clan_bosses_action.create,
                id=boss.pk,
                clan_id=character.clan.pk,
            ),
        )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=ClanBossesData(action=clan_bosses_action.list),
    )
    keyboard.adjust(1)
    return keyboard


async def alert_about_clan_boss_respawn_keyboard(boss: ClanBoss):
    """Клавиатура подтверждения названия Клана."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=ACCEPT_RAID_BUTTON,
        callback_data=ClanBossesData(
            action=clan_bosses_action.accept_raid, id=boss.pk
        ),
    )
    keyboard.adjust(1)
    return keyboard
