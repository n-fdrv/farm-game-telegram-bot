from aiogram.utils.keyboard import InlineKeyboardBuilder
from game.models import Character

from bot.constants.actions import character_action, location_action
from bot.constants.buttons import character_buttons, main_buttons
from bot.constants.callback_data import CharacterData, LocationData


async def character_get(character: Character):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    if character.current_location:
        keyboard.button(
            text=character_buttons.EXIT_LOCATION_BUTTON,
            callback_data=CharacterData(
                action=character_action.exit_location_confirm
            ),
        )
        keyboard.button(
            text=character_buttons.BACKPACK_BUTTON,
            callback_data=CharacterData(action=character_action.get),
        )
        keyboard.adjust(1)
        return keyboard
    keyboard.button(
        text=character_buttons.LOCATIONS_BUTTON,
        callback_data=LocationData(action=location_action.list),
    )
    keyboard.button(
        text=character_buttons.BACKPACK_BUTTON,
        callback_data=CharacterData(action=character_action.get),
    )
    keyboard.button(
        text=character_buttons.SHOP_BUTTON,
        callback_data=CharacterData(action=character_action.get),
    )
    keyboard.adjust(1)
    return keyboard


async def exit_location_confirmation():
    """Клавиатура подтверждения выхода из локации."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=main_buttons.YES_BUTTON,
        callback_data=CharacterData(action=character_action.exit_location),
    )
    keyboard.button(
        text=main_buttons.NO_BUTTON,
        callback_data=CharacterData(action=character_action.get),
    )
    keyboard.adjust(2)
    return keyboard
