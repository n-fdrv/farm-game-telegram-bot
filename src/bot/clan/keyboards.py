from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character
from clan.models import Clan

from bot.clan.buttons import (
    CLAN_MEMBERS_BUTTON,
    CLAN_WARS_BUTTON,
    CREATE_CLAN_BUTTON,
    CREATE_REQUEST_BUTTON,
    ENTER_CLAN_BUTTON,
    EXIT_CLAN_BUTTON,
    REQUEST_LIST_BUTTON,
    SEARCH_CLAN_BUTTON,
    SEARCH_CLAN_LIST_BUTTON,
    SETTINGS_BUTTON,
)
from bot.command.buttons import (
    BACK_BUTTON,
    CANCEL_BUTTON,
    NO_BUTTON,
    YES_BUTTON,
)
from bot.constants.actions import clan_action
from bot.constants.callback_data import ClanData
from bot.utils.paginator import Paginator


async def no_clan_preview_keyboard():
    """Клавиатура персонажа."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=ENTER_CLAN_BUTTON, callback_data=ClanData(action=clan_action.list)
    )
    keyboard.button(
        text=CREATE_CLAN_BUTTON,
        callback_data=ClanData(action=clan_action.create_preview),
    )
    keyboard.adjust(1)
    return keyboard


async def to_preview_keyboard():
    """Клавиатура возврата к превью."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=CANCEL_BUTTON, callback_data=ClanData(action=clan_action.preview)
    )
    keyboard.adjust(1)
    return keyboard


async def confirm_clan_name_keyboard():
    """Клавиатура подтверждения названия Клана."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON, callback_data=ClanData(action=clan_action.create)
    )
    keyboard.button(
        text=NO_BUTTON, callback_data=ClanData(action=clan_action.preview)
    )
    keyboard.adjust(2)
    return keyboard


async def clan_get_keyboard(character: Character):
    """Клавиатура подтверждения названия Клана."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=CLAN_MEMBERS_BUTTON,
        callback_data=ClanData(
            action=clan_action.members, id=character.clan.id
        ),
    )
    keyboard.button(
        text=CLAN_WARS_BUTTON,
        callback_data=ClanData(action=clan_action.wars, id=character.clan.id),
    )
    if character.clan.leader == character:
        if character.clan.by_request:
            keyboard.button(
                text=REQUEST_LIST_BUTTON,
                callback_data=ClanData(
                    action=clan_action.request_list, id=character.clan.id
                ),
            )
        keyboard.button(
            text=SETTINGS_BUTTON,
            callback_data=ClanData(
                action=clan_action.settings, id=character.clan.id
            ),
        )
    else:
        keyboard.button(
            text=EXIT_CLAN_BUTTON,
            callback_data=ClanData(
                action=clan_action.exit_confirm, id=character.clan.id
            ),
        )
    keyboard.adjust(1)
    return keyboard


async def clan_list_keyboard(callback_data: ClanData):
    """Клавиатура списка Кланов."""
    keyboard = InlineKeyboardBuilder()
    async for clan in Clan.objects.order_by("-level").all():
        access = "Открытый"
        if clan.by_request:
            access = "По заявке"
        keyboard.button(
            text=f"{clan.name_with_emoji} Ур. {clan.level} ({access})",
            callback_data=ClanData(action=clan_action.get, id=clan.id),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=clan_action.list,
        size=6,
        page=callback_data.page,
    )
    return paginator.get_paginator_with_buttons_list(
        [
            [
                SEARCH_CLAN_BUTTON,
                ClanData(
                    action=clan_action.search_clan,
                ),
            ],
            [
                BACK_BUTTON,
                ClanData(
                    action=clan_action.preview,
                ),
            ],
        ]
    )


async def clan_search_keyboard(item_name_contains: str):
    """Клавиатура получения предмета для продажи."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=SEARCH_CLAN_LIST_BUTTON,
        callback_data=ClanData(
            action=clan_action.search_list,
            name_contains=item_name_contains,
        ),
    )
    keyboard.button(
        text=CANCEL_BUTTON,
        callback_data=ClanData(action=clan_action.list),
    )
    keyboard.adjust(1)
    return keyboard


async def search_clan_list_keyboard(callback_data: ClanData):
    """Клавиатура списка Кланов."""
    keyboard = InlineKeyboardBuilder()
    async for clan in (
        Clan.objects.filter(name__contains=callback_data.name_contains)
        .order_by("-level")
        .all()
    ):
        access = "Открытый"
        if clan.by_request:
            access = "По заявке"
        keyboard.button(
            text=f"{clan.name_with_emoji} Ур. {clan.level} ({access})",
            callback_data=ClanData(action=clan_action.get, id=clan.id),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=clan_action.list,
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


async def clan_guest_get_keyboard(clan: Clan):
    """Клавиатура подтверждения названия Клана."""
    keyboard = InlineKeyboardBuilder()
    if clan.by_request:
        keyboard.button(
            text=CREATE_REQUEST_BUTTON,
            callback_data=ClanData(
                action=clan_action.create_request_confirm, id=clan.pk
            ),
        )
    else:
        keyboard.button(
            text=ENTER_CLAN_BUTTON,
            callback_data=ClanData(
                action=clan_action.enter_clan_confirm, id=clan.pk
            ),
        )
    keyboard.button(
        text=CLAN_MEMBERS_BUTTON,
        callback_data=ClanData(action=clan_action.members, id=clan.pk),
    )
    keyboard.button(
        text=CLAN_WARS_BUTTON,
        callback_data=ClanData(action=clan_action.wars, id=clan.pk),
    )
    keyboard.button(
        text=BACK_BUTTON, callback_data=ClanData(action=clan_action.list)
    )
    keyboard.adjust(1)
    return keyboard


async def clan_enter_confirm_keyboard(callback_data: ClanData):
    """Клавиатура подтверждения входа в клан."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=ClanData(
            action=clan_action.enter_clan, id=callback_data.id
        ),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=ClanData(action=clan_action.get, id=callback_data.id),
    )
    keyboard.adjust(2)
    return keyboard


async def clan_exit_confirm_keyboard(callback_data: ClanData):
    """Клавиатура подтверждения входа в клан."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=ClanData(action=clan_action.exit, id=callback_data.id),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=ClanData(action=clan_action.preview),
    )
    keyboard.adjust(2)
    return keyboard
