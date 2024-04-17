from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Power

from bot.character.powers.buttons import ADD_POWER_BUTTON, RESET_POWERS_BUTTON
from bot.command.buttons import BACK_BUTTON, NO_BUTTON, YES_BUTTON
from bot.constants.actions import (
    character_action,
)
from bot.constants.callback_data import (
    CharacterData,
)


async def powers_list_keyboard():
    """Клавиатура списка доступных сил."""
    keyboard = InlineKeyboardBuilder()
    async for power in Power.objects.order_by("price").all():
        keyboard.button(
            text=f"{power.name} ✨{power.price}",
            callback_data=CharacterData(
                action=character_action.power_get,
                id=power.id,
            ),
        )
    keyboard.button(
        text=RESET_POWERS_BUTTON,
        callback_data=CharacterData(
            action=character_action.power_reset_confirm
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.get),
    )
    keyboard.adjust(2, 2, 2, 2, 1)
    return keyboard


async def powers_reset_confirm_keyboard():
    """Клавиатура подтверждения сброса силы."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=CharacterData(action=character_action.power_reset),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=CharacterData(action=character_action.power_list),
    )
    keyboard.adjust(2)
    return keyboard


async def powers_reset_keyboard():
    """Клавиатура подтверждения сброса силы."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.power_list),
    )
    keyboard.adjust(1)
    return keyboard


async def powers_get_keyboard(callback_data: CharacterData):
    """Клавиатура подтверждения сброса силы."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=ADD_POWER_BUTTON,
        callback_data=CharacterData(
            action=character_action.power_add_confirm, id=callback_data.id
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.power_list),
    )
    keyboard.adjust(1)
    return keyboard


async def powers_add_confirm_keyboard(callback_data: CharacterData):
    """Клавиатура подтверждения добавления силы."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=CharacterData(
            action=character_action.power_add, id=callback_data.id
        ),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=CharacterData(
            action=character_action.power_get, id=callback_data.id
        ),
    )
    keyboard.adjust(2)
    return keyboard
