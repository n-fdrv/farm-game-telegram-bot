from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.clan.buttons import CREATE_CLAN_BUTTON, ENTER_CLAN_BUTTON
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
        callback_data=ClanData(action=clan_action.create),
    )
    keyboard.adjust(1)
    return keyboard
