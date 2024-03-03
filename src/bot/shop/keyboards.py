from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import CharacterItem
from item.models import Item

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
        callback_data=ShopData(action=shop_action.buy_list),
    )
    keyboard.button(
        text=SELL_BUTTON,
        callback_data=ShopData(action=shop_action.sell_list),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.get),
    )
    keyboard.adjust(1)
    return keyboard


async def buy_list_keyboard(callback_data: ShopData):
    """Клавиатура для списка покупок."""
    keyboard = InlineKeyboardBuilder()
    async for item in Item.objects.exclude(buy_price=0):
        keyboard.button(
            text=f"{item.name_with_type} - {item.buy_price} золота",
            callback_data=ShopData(
                action=shop_action.buy_get,
                page=callback_data.page,
                id=item.id,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=shop_action.buy_list,
        size=6,
        page=callback_data.page,
    )
    return paginator.get_paginator_with_button(BACK_BUTTON, shop_action.get)


async def buy_get_keyboard(callback_data: ShopData):
    """Клавиатура для покупки товара."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BUY_BUTTON,
        callback_data=ShopData(action=shop_action.buy, id=callback_data.id),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=ShopData(action=shop_action.buy_list),
    )
    keyboard.adjust(1)
    return keyboard


async def buy_keyboard():
    """Клавиатура для покупки товара."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=ShopData(action=shop_action.buy_list),
    )
    keyboard.adjust(1)
    return keyboard


async def sell_list_keyboard(user: User, callback_data: ShopData):
    """Клавиатура для списка продаж."""
    keyboard = InlineKeyboardBuilder()
    async for item in (
        CharacterItem.objects.select_related("item")
        .exclude(item__sell_price=0)
        .filter(character=user.character)
    ):
        keyboard.button(
            text=f"{item.item.name_with_type} - {item.amount} шт.",
            callback_data=ShopData(
                action=shop_action.sell_get,
                page=callback_data.page,
                id=item.item.id,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=shop_action.get,
        size=6,
        page=callback_data.page,
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
        callback_data=ShopData(action=shop_action.sell_list),
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


async def in_shop_keyboard():
    """Клавиатура перехода в магазин."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=IN_SHOP_BUTTON,
        callback_data=ShopData(action=shop_action.get),
    )
    keyboard.adjust(1)
    return keyboard


async def sell_amount_confirm_keyboard(item_id, amount):
    """Клавиатура подтверждения продажи товара."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=ShopData(
            action=shop_action.sell, id=item_id, amount=amount
        ),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=ShopData(action=shop_action.sell_get, id=item_id),
    )
    keyboard.adjust(2)
    return keyboard
