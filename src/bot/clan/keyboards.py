from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character

from bot.clan.buttons import (
    CLAN_MEMBERS_BUTTON,
    CLAN_WARS_BUTTON,
    CREATE_CLAN_BUTTON,
    ENTER_CLAN_BUTTON,
    EXIT_CLAN_BUTTON,
    SETTINGS_BUTTON,
)
from bot.command.buttons import CANCEL_BUTTON, NO_BUTTON, YES_BUTTON
from bot.constants.actions import clan_action
from bot.constants.callback_data import ClanData


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
