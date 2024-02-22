from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import CharacterItem
from item.models import Item

from bot.constants.actions import (
    character_action,
    shop_action,
)
from bot.constants.buttons import (
    main_buttons,
    shop_buttons,
)
from bot.constants.callback_data import (
    CharacterData,
    ShopData,
)
from bot.models import User
from bot.utils.paginator import Paginator


async def shop_get():
    """Клавиатура для магазина."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=shop_buttons.BUY_BUTTON,
        callback_data=ShopData(action=shop_action.buy_list),
    )
    keyboard.button(
        text=shop_buttons.SELL_BUTTON,
        callback_data=ShopData(action=shop_action.sell_list),
    )
    keyboard.button(
        text=main_buttons.BACK_BUTTON,
        callback_data=CharacterData(action=character_action.get),
    )
    keyboard.adjust(1)
    return keyboard


async def buy_list(callback_data: ShopData):
    """Клавиатура для списка покупок."""
    keyboard = InlineKeyboardBuilder()
    async for item in Item.objects.exclude(buy_price=0):
        keyboard.button(
            text=f"{item.name_with_grade} - {item.buy_price} золота",
            callback_data=ShopData(
                action=shop_action.get,
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
    return paginator.get_paginator_with_button(
        main_buttons.BACK_BUTTON, shop_action.get
    )


async def sell_list(user: User, callback_data: ShopData):
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
    return paginator.get_paginator_with_button(
        main_buttons.BACK_BUTTON, shop_action.get
    )
