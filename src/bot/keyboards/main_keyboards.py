from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.constants.actions import character_action
from bot.constants.buttons import main_buttons
from bot.constants.callback_data import CharacterData


async def main_keyboard():
    """Основная клавиатура под чатом."""
    keyboard = ReplyKeyboardBuilder()
    keyboard.row(
        KeyboardButton(text=main_buttons.CHARACTER_BUTTON),
        KeyboardButton(text=main_buttons.TOP_BUTTON),
    )
    keyboard.row(
        KeyboardButton(text=main_buttons.SHOP_BUTTON),
        KeyboardButton(text=main_buttons.MARKET_BUTTON),
    )
    keyboard.row(
        KeyboardButton(text=main_buttons.INFORMATION_BUTTON),
    )
    return keyboard


async def user_created_keyboard():
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=main_buttons.CREATE_CHARACTER_BUTTON,
        callback_data=CharacterData(action=character_action.create_preview),
    )
    keyboard.adjust(1)
    return keyboard
