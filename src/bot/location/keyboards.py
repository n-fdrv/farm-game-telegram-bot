from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character
from django.utils import timezone
from item.models import EffectProperty
from location.models import Location

from bot.command.buttons import BACK_BUTTON, NO_BUTTON, YES_BUTTON
from bot.constants.actions import character_action, location_action
from bot.constants.callback_data import CharacterData, LocationData
from bot.location.buttons import (
    CHARACTER_KILL_BUTTON,
    GET_DROP_MESSAGE,
    LOCATION_BUTTON,
    LOCATION_CHARACTERS_BUTTON,
    START_HUNTING_MESSAGE,
)
from bot.utils.paginator import Paginator


async def location_list_keyboard(callback_data: LocationData):
    """Клавиатура списка локаций."""
    keyboard = InlineKeyboardBuilder()
    async for location in Location.objects.order_by("attack").all():
        keyboard.button(
            text=LOCATION_BUTTON.format(
                location.name, location.attack, location.defence
            ),
            callback_data=LocationData(
                action=location_action.get,
                page=callback_data.page,
                id=location.id,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=location_action.list,
        size=6,
        page=callback_data.page,
    )
    return paginator.get_paginator_with_button(
        BACK_BUTTON, character_action.get
    )


async def location_get_keyboard(callback_data: LocationData):
    """Клавиатура локации."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=START_HUNTING_MESSAGE,
        callback_data=LocationData(
            action=location_action.enter, id=callback_data.id
        ),
    )
    keyboard.button(
        text=LOCATION_CHARACTERS_BUTTON,
        callback_data=LocationData(
            action=location_action.characters_list, id=callback_data.id
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=LocationData(
            action=location_action.list, page=callback_data.page
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def get_drop_keyboard():
    """Клавиатура получения дропа с локации."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=GET_DROP_MESSAGE,
        callback_data=LocationData(action=location_action.exit_location),
    )
    keyboard.adjust(1)
    return keyboard


async def exit_location_confirmation():
    """Клавиатура подтверждения выхода из локации."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=LocationData(action=location_action.exit_location),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=CharacterData(action=character_action.get),
    )
    keyboard.adjust(2)
    return keyboard


async def character_list_keyboard(callback_data: LocationData):
    """Клавиатура списка локаций."""
    keyboard = InlineKeyboardBuilder()
    async for character in (
        Character.objects.select_related("character_class", "clan")
        .filter(current_location__id=callback_data.id)
        .all()
    ):
        if await character.effects.filter(
            charactereffect__effect__property=EffectProperty.INVISIBLE,
            charactereffect__expired__gt=timezone.now(),
        ).aexists():
            continue
        keyboard.button(
            text=character.name_with_clan,
            callback_data=LocationData(
                action=location_action.characters_get,
                id=callback_data.id,
                character_id=character.id,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=location_action.list,
        size=6,
        page=callback_data.page,
    )
    return paginator.get_paginator_with_buttons_list(
        [
            [
                BACK_BUTTON,
                LocationData(
                    action=location_action.get,
                    page=callback_data.page,
                    id=callback_data.id,
                ),
            ]
        ]
    )


async def location_character_get_keyboard(callback_data: LocationData):
    """Клавиатура подтверждения выхода из локации."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=CHARACTER_KILL_BUTTON,
        callback_data=LocationData(
            action=location_action.characters_kill_confirm,
            id=callback_data.id,
            character_id=callback_data.character_id,
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=LocationData(
            action=location_action.characters_list,
            id=callback_data.id,
            character_id=callback_data.character_id,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def kill_character_confirm_keyboard(callback_data: LocationData):
    """Клавиатура подтверждения выхода из локации."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=LocationData(
            action=location_action.characters_kill,
            id=callback_data.id,
            character_id=callback_data.character_id,
        ),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=LocationData(
            action=location_action.characters_get,
            id=callback_data.id,
            character_id=callback_data.character_id,
        ),
    )
    keyboard.adjust(2)
    return keyboard
