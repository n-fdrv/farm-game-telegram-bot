from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import CharacterItem
from item.models import Item

from bot.command.buttons import BACK_BUTTON
from bot.constants.actions import (
    character_action,
    shop_action,
)
from bot.constants.callback_data import (
    CharacterData,
    ShopData,
)
from bot.models import User
from bot.shop.buttons import BUY_BUTTON, SELL_BUTTON
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
            text=f"{item.name_with_grade} - {item.buy_price} золота",
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
    async for item in CharacterItem.objects.select_related("item").exclude(
        item__sell_price=0
    ).filter(character=user.character):
        keyboard.button(
            text=f"{item.item.name_with_grade} - {item.amount} шт.",
            callback_data=ShopData(
                action=shop_action.sell_get,
                page=callback_data.page,
                id=item.id,
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
