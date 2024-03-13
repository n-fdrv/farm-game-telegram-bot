from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.command.buttons import BACK_BUTTON
from bot.constants.actions import premium_action
from bot.constants.callback_data import PremiumData
from bot.premium_shop.buttons import (
    DIAMOND_100_BUTTON,
    DIAMOND_300_BUTTON,
    DIAMOND_500_BUTTON,
    DIAMONDS_BUTTON,
    MONTH_PREMIUM_BUTTON,
    PREMIUM_BUTTON,
    START_PACK_BUTTON,
    START_PACK_BUY_BUTTON,
    WEEK_PREMIUM_BUTTON,
)


async def premium_list_keyboard():
    """Список Товаров."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=DIAMONDS_BUTTON,
        callback_data=PremiumData(
            action=premium_action.get, type=DIAMONDS_BUTTON
        ),
    )
    keyboard.button(
        text=PREMIUM_BUTTON,
        callback_data=PremiumData(
            action=premium_action.get, type=PREMIUM_BUTTON
        ),
    )
    keyboard.button(
        text=START_PACK_BUTTON,
        callback_data=PremiumData(
            action=premium_action.get, type=START_PACK_BUTTON
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def diamonds_keyboard():
    """Клавиатура алмазов."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=DIAMOND_100_BUTTON,
        callback_data=PremiumData(
            action=premium_action.buy, type=DIAMOND_100_BUTTON
        ),
    )
    keyboard.button(
        text=DIAMOND_300_BUTTON,
        callback_data=PremiumData(
            action=premium_action.buy, type=DIAMOND_300_BUTTON
        ),
    )
    keyboard.button(
        text=DIAMOND_500_BUTTON,
        callback_data=PremiumData(
            action=premium_action.buy, type=DIAMOND_500_BUTTON
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=PremiumData(action=premium_action.list),
    )
    keyboard.adjust(1)
    return keyboard


async def premium_keyboard():
    """Клавиатура премиум подписки."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=WEEK_PREMIUM_BUTTON,
        callback_data=PremiumData(
            action=premium_action.buy, type=WEEK_PREMIUM_BUTTON, price=100
        ),
    )
    keyboard.button(
        text=MONTH_PREMIUM_BUTTON,
        callback_data=PremiumData(
            action=premium_action.buy, type=MONTH_PREMIUM_BUTTON, price=250
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=PremiumData(action=premium_action.list),
    )
    keyboard.adjust(1)
    return keyboard


async def pack_keyboard():
    """Клавиатура стартовых наборов."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=START_PACK_BUY_BUTTON,
        callback_data=PremiumData(action=premium_action.buy, price=300),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=PremiumData(action=premium_action.list),
    )
    keyboard.adjust(1)
    return keyboard


async def premium_get_keyboard(callback_data: PremiumData):
    """Распределение клавиатуры в зависимости от категории."""
    keyboard_data = {
        DIAMONDS_BUTTON: diamonds_keyboard,
        PREMIUM_BUTTON: premium_keyboard,
        START_PACK_BUTTON: pack_keyboard,
    }
    return await keyboard_data[callback_data.type]()
