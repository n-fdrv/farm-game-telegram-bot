from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.constants.buttons import main_buttons


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
