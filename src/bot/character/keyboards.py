from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character

from bot.character.buttons import (
    BACKPACK_BUTTON,
    EXIT_LOCATION_BUTTON,
    LOCATIONS_BUTTON,
    SHOP_BUTTON,
)
from bot.constants.actions import (
    backpack_action,
    location_action,
    shop_action,
)
from bot.constants.callback_data import (
    BackpackData,
    LocationData,
    ShopData,
)


async def character_get_keyboard(character: Character):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    if character.current_location:
        keyboard.button(
            text=EXIT_LOCATION_BUTTON,
            callback_data=LocationData(
                action=location_action.exit_location_confirm
            ),
        )
        keyboard.button(
            text=BACKPACK_BUTTON,
            callback_data=BackpackData(action=backpack_action.list),
        )
        keyboard.adjust(1)
        return keyboard
    keyboard.button(
        text=LOCATIONS_BUTTON,
        callback_data=LocationData(action=location_action.list),
    )
    keyboard.button(
        text=BACKPACK_BUTTON,
        callback_data=BackpackData(action=backpack_action.list),
    )
    keyboard.button(
        text=SHOP_BUTTON,
        callback_data=ShopData(action=shop_action.get),
    )
    keyboard.adjust(1)
    return keyboard
