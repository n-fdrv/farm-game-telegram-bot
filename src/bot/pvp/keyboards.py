from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character

from bot.constants.actions import pvp_action
from bot.constants.callback_data import PvPData
from bot.pvp.buttons import ATTACK_BUTTON


async def attack_keyboard(
    attacker: Character, attacker_message_id, target: Character
):
    """Клавиатура цели атаки персонажа."""
    keyboard = InlineKeyboardBuilder()
    location_id = 0
    if attacker.current_place:
        location_id = attacker.current_place.pk
    keyboard.button(
        text=ATTACK_BUTTON,
        callback_data=PvPData(
            action=pvp_action.characters_kill,
            message_id=attacker_message_id,
            id=location_id,
            character_id=target.pk,
        ),
    )
    keyboard.adjust(1)
    return keyboard
