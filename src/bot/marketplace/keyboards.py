from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character, CharacterItem
from django.conf import settings
from django.db.models import Count
from item.models import ItemType

from bot.command.buttons import BACK_BUTTON, CANCEL_BUTTON
from bot.constants.actions import marketplace_action
from bot.constants.callback_data import (
    MarketplaceData,
)
from bot.marketplace.buttons import (
    ADD_BUTTON,
    ADD_ON_MARKETPLACE_BUTTON,
    BUY_BUTTON,
    ITEMS_BUTTON,
    SELL_BUTTON,
)
from bot.models import User
from bot.utils.paginator import Paginator


async def marketplace_preview_keyboard():
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BUY_BUTTON,
        callback_data=MarketplaceData(action=marketplace_action.buy_preview),
    )
    keyboard.button(
        text=SELL_BUTTON,
        callback_data=MarketplaceData(action=marketplace_action.sell_preview),
    )
    keyboard.button(
        text=ITEMS_BUTTON,
        callback_data=MarketplaceData(action=marketplace_action.items_list),
    )
    keyboard.adjust(1)
    return keyboard


async def sell_preview_keyboard(character: Character):
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
                callback_data=MarketplaceData(
                    action=marketplace_action.sell_list,
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
        callback_data=MarketplaceData(action=marketplace_action.preview),
    )
    keyboard.adjust(*row, 1)
    return keyboard


async def sell_list_keyboard(user: User, callback_data: MarketplaceData):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    async for item in CharacterItem.objects.select_related("item").filter(
        character=user.character, item__type=callback_data.type
    ):
        keyboard.button(
            text=f"{item.name_with_enhance} - {item.amount} шт.",
            callback_data=MarketplaceData(
                action=marketplace_action.sell_get,
                page=callback_data.page,
                id=item.id,
                type=callback_data.type,
                amount=item.amount,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=marketplace_action.sell_list,
        size=6,
        page=callback_data.page,
    )
    return paginator.get_paginator_with_button(
        BACK_BUTTON, marketplace_action.sell_preview
    )


async def sell_get_keyboard(callback_data: MarketplaceData):
    """Клавиатура получения предмета для продажи."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=ADD_ON_MARKETPLACE_BUTTON,
        callback_data=MarketplaceData(
            action=marketplace_action.add_preview,
            id=callback_data.id,
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=MarketplaceData(
            action=marketplace_action.sell_list,
            page=callback_data.page,
            type=callback_data.type,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def add_preview_keyboard():
    """Клавиатура получения предмета для продажи."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=settings.GOLD_NAME,
        callback_data=MarketplaceData(
            action=marketplace_action.choose_currency,
            currency=settings.GOLD_NAME,
        ),
    )
    keyboard.button(
        text=settings.DIAMOND_NAME,
        callback_data=MarketplaceData(
            action=marketplace_action.choose_currency,
            currency=settings.DIAMOND_NAME,
        ),
    )
    keyboard.button(
        text=CANCEL_BUTTON,
        callback_data=MarketplaceData(
            action=marketplace_action.sell_preview,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def to_sell_preview_keyboard():
    """Клавиатура получения предмета для продажи."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=CANCEL_BUTTON,
        callback_data=MarketplaceData(
            action=marketplace_action.sell_preview,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def sell_confirm_keyboard():
    """Клавиатура получения предмета для продажи."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=ADD_BUTTON,
        callback_data=MarketplaceData(
            action=marketplace_action.add,
        ),
    )
    keyboard.button(
        text=CANCEL_BUTTON,
        callback_data=MarketplaceData(
            action=marketplace_action.sell_preview,
        ),
    )
    keyboard.adjust(1)
    return keyboard
