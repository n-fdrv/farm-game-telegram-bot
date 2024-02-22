from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.command.buttons import (
    CHARACTER_BUTTON,
    CREATE_CHARACTER_BUTTON,
    INFORMATION_BUTTON,
    MARKET_BUTTON,
    PREMIUM_SHOP_BUTTON,
    TOP_BUTTON,
)
from bot.constants.actions import character_action
from bot.constants.callback_data import CharacterData


async def start_keyboard():
    """Основная клавиатура под чатом."""
    keyboard = ReplyKeyboardBuilder()
    keyboard.row(
        KeyboardButton(text=CHARACTER_BUTTON),
        KeyboardButton(text=TOP_BUTTON),
    )
    keyboard.row(
        KeyboardButton(text=PREMIUM_SHOP_BUTTON),
        KeyboardButton(text=MARKET_BUTTON),
    )
    keyboard.row(
        KeyboardButton(text=INFORMATION_BUTTON),
    )
    return keyboard


async def user_created_keyboard():
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=CREATE_CHARACTER_BUTTON,
        callback_data=CharacterData(action=character_action.create_preview),
    )
    keyboard.adjust(1)
    return keyboard
