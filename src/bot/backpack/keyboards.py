from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character, CharacterItem
from django.db.models import Count
from item.models import ItemType

from bot.backpack.buttons import (
    EQUIP_BUTTON,
    OPEN_ALL_BUTTON,
    OPEN_BUTTON,
    OPEN_MORE_BUTTON,
    USE_BUTTON,
)
from bot.command.buttons import BACK_BUTTON
from bot.constants.actions import (
    backpack_action,
    character_action,
)
from bot.constants.callback_data import (
    BackpackData,
    CharacterData,
)
from bot.models import User
from bot.utils.paginator import Paginator


async def backpack_preview_keyboard(character: Character):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    button_number = 0
    row = []
    button_in_row = 2
    items_data = [
        x
        async for x in character.items.values_list("type", flat=True)
        .annotate(Count("type"))
        .all()
    ]
    for item_type in ItemType.choices:
        if item_type[0] == ItemType.ETC:
            continue
        if item_type[0] in items_data:
            keyboard.button(
                text=item_type[1],
                callback_data=BackpackData(
                    action=backpack_action.list,
                    type=item_type[0],
                ),
            )
            button_number += 1
            if button_number == button_in_row:
                row.append(button_number)
                button_number = 0
    if button_number > 0:
        row.append(button_number)
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.get),
    )
    keyboard.adjust(*row, 1)
    return keyboard


async def backpack_list_keyboard(user: User, callback_data: BackpackData):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    async for item in CharacterItem.objects.select_related("item").filter(
        character=user.character, item__type=callback_data.type
    ):
        keyboard.button(
            text=f"{item.item.name_with_type} - {item.amount} шт.",
            callback_data=BackpackData(
                action=backpack_action.get,
                page=callback_data.page,
                id=item.id,
                type=callback_data.type,
                amount=item.amount,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=backpack_action.list,
        size=6,
        page=callback_data.page,
    )
    return paginator.get_paginator_with_button(
        BACK_BUTTON, backpack_action.preview
    )


async def item_get_keyboard(callback_data: BackpackData):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    equipped_data = [ItemType.WEAPON, ItemType.ARMOR, ItemType.TALISMAN]
    usable_data = [ItemType.SCROLL, ItemType.RECIPE, ItemType.POTION]
    if callback_data.type in equipped_data:
        keyboard.button(
            text=EQUIP_BUTTON,
            callback_data=BackpackData(
                action=backpack_action.equip,
                id=callback_data.id,
                type=callback_data.type,
            ),
        )
    elif callback_data.type in usable_data:
        keyboard.button(
            text=USE_BUTTON,
            callback_data=BackpackData(
                action=backpack_action.use, id=callback_data.id
            ),
        )
    elif callback_data.type == ItemType.BAG:
        keyboard.button(
            text=OPEN_BUTTON,
            callback_data=BackpackData(
                action=backpack_action.open, id=callback_data.id, amount=1
            ),
        )
        keyboard.button(
            text=OPEN_ALL_BUTTON,
            callback_data=BackpackData(
                action=backpack_action.open,
                id=callback_data.id,
                amount=callback_data.amount,
            ),
        )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=BackpackData(
            action=backpack_action.list,
            page=callback_data.page,
            type=callback_data.type,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def not_success_equip_keyboard(callback_data: BackpackData):
    """Клавиатура неудачного надевания предмета."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=BackpackData(
            action=backpack_action.get,
            page=callback_data.page,
            id=callback_data.id,
            type=callback_data.type,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def in_backpack_keyboard():
    """Клавиатура возвращения в инвентарь."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=BackpackData(
            action=backpack_action.preview,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def open_more_keyboard(callback_data: BackpackData):
    """Клавиатура предложения открыть еще."""
    keyboard = InlineKeyboardBuilder()
    if callback_data.amount > 0:
        keyboard.button(
            text=OPEN_MORE_BUTTON,
            callback_data=BackpackData(
                action=backpack_action.open, id=callback_data.id
            ),
        )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=BackpackData(
            action=backpack_action.preview,
        ),
    )
    keyboard.adjust(1)
    return keyboard
