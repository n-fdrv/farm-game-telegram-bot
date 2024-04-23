from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character

from bot.command.buttons import BACK_BUTTON, NO_BUTTON, YES_BUTTON
from bot.constants.actions import pvp_action
from bot.constants.callback_data import PvPData
from bot.pvp.buttons import ATTACK_BUTTON
from bot.utils.paginator import get_callback_by_action


async def pvp_get_keyboard(callback_data: PvPData):
    """Клавиатура подтверждения выхода из локации."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=ATTACK_BUTTON,
        callback_data=PvPData(
            action=pvp_action.attack_confirm,
            id=callback_data.id,
            back_action=callback_data.back_action,
            back_id=callback_data.back_id,
        ),
    )
    back_data = get_callback_by_action(callback_data.back_action)
    back_data.id = callback_data.back_id
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=back_data,
    )
    keyboard.adjust(1)
    return keyboard


async def attack_character_confirm_keyboard(callback_data: PvPData):
    """Клавиатура подтверждения выхода из локации."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=PvPData(
            action=pvp_action.attack,
            id=callback_data.id,
            back_action=callback_data.back_action,
            back_id=callback_data.back_id,
        ),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=PvPData(
            action=pvp_action.get,
            id=callback_data.id,
            back_action=callback_data.back_action,
            back_id=callback_data.back_id,
        ),
    )
    keyboard.adjust(2)
    return keyboard


async def attack_keyboard(attacker_message_id, target: Character):
    """Клавиатура цели атаки персонажа."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=ATTACK_BUTTON,
        callback_data=PvPData(
            action=pvp_action.attack,
            message_id=attacker_message_id,
            id=target.pk,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def attack_more_keyboard(callback_data: PvPData):
    """Клавиатура после атаки персонажа."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=ATTACK_BUTTON,
        callback_data=PvPData(
            action=pvp_action.attack,
            id=callback_data.id,
            message_id=callback_data.message_id,
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=PvPData(
            action=pvp_action.get,
            id=callback_data.id,
            message_id=callback_data.message_id,
        ),
    )
    keyboard.adjust(2)
    return keyboard
