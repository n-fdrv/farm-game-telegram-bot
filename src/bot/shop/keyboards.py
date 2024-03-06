from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character, CharacterItem
from django.db.models import Count
from item.models import Item, ItemType

from bot.command.buttons import BACK_BUTTON, NO_BUTTON, YES_BUTTON
from bot.constants.actions import (
    character_action,
    shop_action,
)
from bot.constants.callback_data import (
    CharacterData,
    ShopData,
)
from bot.models import User
from bot.shop.buttons import (
    BUY_BUTTON,
    IN_SHOP_BUTTON,
    SELL_ALL_BUTTON,
    SELL_AMOUNT_BUTTON,
    SELL_BUTTON,
)
from bot.utils.paginator import Paginator


async def shop_get_keyboard():
    """Клавиатура для магазина."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BUY_BUTTON,
        callback_data=ShopData(action=shop_action.buy_preview),
    )
    keyboard.button(
        text=SELL_BUTTON,
        callback_data=ShopData(action=shop_action.sell_preview),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.get),
    )
    keyboard.adjust(1)
    return keyboard


async def buy_preview_keyboard():
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    button_number = 0
    row = []
    button_in_row = 2
    items_data = [
        x
        async for x in Item.objects.values_list("type", flat=True)
        .annotate(Count("type"))
        .filter(buy_price__gt=0)
    ]
    for item_type in ItemType.choices:
        if item_type[0] == ItemType.ETC:
            continue
        if item_type[0] in items_data:
            keyboard.button(
                text=item_type[1],
                callback_data=ShopData(
                    action=shop_action.buy_list,
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
        callback_data=ShopData(action=shop_action.get),
    )
    keyboard.adjust(*row, 1)
    return keyboard


async def buy_list_keyboard(callback_data: ShopData):
    """Клавиатура для списка покупок."""
    keyboard = InlineKeyboardBuilder()
    async for item in Item.objects.filter(
        buy_price__gt=0, type=callback_data.type
    ):
        keyboard.button(
            text=f"{item.name_with_type} - {item.buy_price} золота",
            callback_data=ShopData(
                action=shop_action.buy_get,
                page=callback_data.page,
                id=item.id,
                type=callback_data.type,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=shop_action.buy_list,
        size=6,
        type=callback_data.type,
        page=callback_data.page,
    )
    return paginator.get_paginator_with_button(
        BACK_BUTTON, shop_action.buy_preview
    )


async def buy_get_keyboard(callback_data: ShopData):
    """Клавиатура для покупки товара."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BUY_BUTTON,
        callback_data=ShopData(action=shop_action.buy, id=callback_data.id),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=ShopData(
            action=shop_action.buy_list, type=callback_data.type
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def buy_keyboard():
    """Клавиатура для покупки товара."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=ShopData(action=shop_action.buy_preview),
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
                callback_data=ShopData(
                    action=shop_action.sell_list,
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
        callback_data=ShopData(action=shop_action.get),
    )
    keyboard.adjust(*row, 1)
    return keyboard


async def sell_list_keyboard(user: User, callback_data: ShopData):
    """Клавиатура для списка продаж."""
    keyboard = InlineKeyboardBuilder()
    async for item in CharacterItem.objects.select_related("item").filter(
        character=user.character,
        item__sell_price__gt=0,
        item__type=callback_data.type,
    ):
        keyboard.button(
            text=f"{item.name_with_enhance} - {item.amount} шт.",
            callback_data=ShopData(
                action=shop_action.sell_get,
                page=callback_data.page,
                id=item.id,
                type=callback_data.type,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=shop_action.sell_list,
        size=6,
        page=callback_data.page,
        type=callback_data.type,
    )
    return paginator.get_paginator_with_button(BACK_BUTTON, shop_action.get)


async def sell_get_keyboard(callback_data: ShopData):
    """Клавиатура для продажи товара."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=SELL_ALL_BUTTON,
        callback_data=ShopData(
            action=shop_action.sell,
            id=callback_data.id,
            amount=callback_data.amount,
        ),
    )
    keyboard.button(
        text=SELL_AMOUNT_BUTTON,
        callback_data=ShopData(
            action=shop_action.sell_amount, id=callback_data.id
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=ShopData(
            action=shop_action.sell_list, type=callback_data.type
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def sell_keyboard(callback_data: ShopData):
    """Клавиатура для продажи всех товаров."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=ShopData(
            action=shop_action.sell_get, id=callback_data.id
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def in_sell_keyboard(item_type: str):
    """Клавиатура для продажи всех товаров."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=ShopData(action=shop_action.sell_list, type=item_type),
    )
    keyboard.adjust(1)
    return keyboard


async def in_shop_keyboard():
    """Клавиатура перехода в магазин."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=IN_SHOP_BUTTON,
        callback_data=ShopData(action=shop_action.get),
    )
    keyboard.adjust(1)
    return keyboard


async def sell_amount_confirm_keyboard(character_item_id, amount):
    """Клавиатура подтверждения продажи товара."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=ShopData(
            action=shop_action.sell, id=character_item_id, amount=amount
        ),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=ShopData(
            action=shop_action.sell_get, id=character_item_id
        ),
    )
    keyboard.adjust(2)
    return keyboard
