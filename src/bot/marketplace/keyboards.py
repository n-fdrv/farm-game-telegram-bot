from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character, CharacterItem, MarketplaceItem
from django.conf import settings
from django.db.models import Count, F
from item.models import ItemType

from bot.command.buttons import (
    BACK_BUTTON,
    CANCEL_BUTTON,
    NO_BUTTON,
    YES_BUTTON,
)
from bot.constants.actions import marketplace_action
from bot.constants.callback_data import (
    MarketplaceData,
)
from bot.marketplace.buttons import (
    ADD_BUTTON,
    ADD_ON_MARKETPLACE_BUTTON,
    BUY_BUTTON,
    ITEMS_BUTTON,
    REMOVE_LOT_BUTTON,
    SEARCH_ITEM_BUTTON,
    SEARCH_LOT_LIST_BUTTON,
    SELL_BUTTON,
)
from bot.models import User
from bot.utils.paginator import Paginator


async def marketplace_preview_keyboard():
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BUY_BUTTON,
        callback_data=MarketplaceData(action=marketplace_action.buy_currency),
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
        type=callback_data.type,
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


async def choose_buy_currency_keyboard():
    """Клавиатура получения предмета для продажи."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=settings.GOLD_NAME,
        callback_data=MarketplaceData(
            action=marketplace_action.buy_preview,
            currency=settings.GOLD_NAME,
        ),
    )
    keyboard.button(
        text=settings.DIAMOND_NAME,
        callback_data=MarketplaceData(
            action=marketplace_action.buy_preview,
            currency=settings.DIAMOND_NAME,
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=MarketplaceData(
            action=marketplace_action.preview,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def buy_preview_keyboard(callback_data: MarketplaceData):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    button_number = 0
    row = []
    button_in_row = 2
    items_data = [
        x
        async for x in MarketplaceItem.objects.values_list(
            "item__type", flat=True
        )
        .annotate(Count("item__type"))
        .filter(sell_currency__name=callback_data.currency)
    ]
    if items_data:
        for item_type in ItemType.choices:
            if item_type[0] == ItemType.ETC:
                continue
            if item_type[0] in items_data:
                keyboard.button(
                    text=item_type[1],
                    callback_data=MarketplaceData(
                        action=marketplace_action.buy_list,
                        type=item_type[0],
                        currency=callback_data.currency,
                    ),
                )
                button_number += 1
                if button_number == button_in_row:
                    row.append(button_number)
                    button_number = 0
        if button_number > 0:
            row.append(button_number)
        keyboard.button(
            text=SEARCH_ITEM_BUTTON,
            callback_data=MarketplaceData(
                action=marketplace_action.item_search,
                currency=callback_data.currency,
            ),
        )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=MarketplaceData(action=marketplace_action.buy_currency),
    )

    keyboard.adjust(*row, 1, 1)
    return keyboard


async def buy_list_keyboard(callback_data: MarketplaceData):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    async for item in (
        MarketplaceItem.objects.select_related("item", "sell_currency")
        .annotate(price_per_item=F("price") / F("amount"))
        .filter(
            item__type=callback_data.type,
            sell_currency__name=callback_data.currency,
        )
        .order_by("price_per_item")
    ):
        keyboard.button(
            text=item.name_with_price_and_amount,
            callback_data=MarketplaceData(
                action=marketplace_action.buy_get,
                page=callback_data.page,
                id=item.id,
                currency=callback_data.currency,
                type=callback_data.type,
                back_action=callback_data.action,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=marketplace_action.buy_list,
        size=6,
        page=callback_data.page,
        type=callback_data.type,
        currency=callback_data.currency,
    )
    return paginator.get_paginator_with_buttons_list(
        [
            (
                BACK_BUTTON,
                MarketplaceData(
                    action=marketplace_action.buy_preview,
                    currency=callback_data.currency,
                ),
            ),
        ]
    )


async def buy_get_keyboard(callback_data: MarketplaceData):
    """Клавиатура получения предмета для продажи."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BUY_BUTTON,
        callback_data=MarketplaceData(
            action=marketplace_action.buy_confirm,
            page=callback_data.page,
            id=callback_data.id,
            currency=callback_data.currency,
            type=callback_data.type,
        ),
    )
    if not callback_data.back_action:
        callback_data.back_action = marketplace_action.buy_preview
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=MarketplaceData(
            action=callback_data.back_action,
            page=callback_data.page,
            type=callback_data.type,
            name_contains=callback_data.name_contains,
            currency=callback_data.currency,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def buy_confirm_keyboard(callback_data: MarketplaceData):
    """Клавиатура получения предмета для продажи."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=MarketplaceData(
            action=marketplace_action.buy,
            id=callback_data.id,
        ),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=MarketplaceData(
            action=marketplace_action.buy_get,
            page=callback_data.page,
            id=callback_data.id,
            currency=callback_data.currency,
            type=callback_data.type,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def to_buy_preview_keyboard():
    """Клавиатура получения предмета для продажи."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=CANCEL_BUTTON,
        callback_data=MarketplaceData(
            action=marketplace_action.buy_currency,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def items_list_keyboard(character: Character):
    """Клавиатура получения предмета для продажи."""
    keyboard = InlineKeyboardBuilder()
    async for marketplace_item in MarketplaceItem.objects.select_related(
        "sell_currency", "item"
    ).filter(seller=character):
        keyboard.button(
            text=marketplace_item.name_with_price_and_amount,
            callback_data=MarketplaceData(
                action=marketplace_action.item_get, id=marketplace_item.id
            ),
        )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=MarketplaceData(action=marketplace_action.preview),
    )
    keyboard.adjust(1)
    return keyboard


async def item_get_keyboard(callback_data: MarketplaceData):
    """Клавиатура получения предмета для продажи."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=REMOVE_LOT_BUTTON,
        callback_data=MarketplaceData(
            action=marketplace_action.remove_preview, id=callback_data.id
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=MarketplaceData(action=marketplace_action.items_list),
    )
    keyboard.adjust(1)
    return keyboard


async def remove_preview_keyboard(callback_data: MarketplaceData):
    """Клавиатура получения предмета для продажи."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=MarketplaceData(
            action=marketplace_action.remove, id=callback_data.id
        ),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=MarketplaceData(
            action=marketplace_action.item_get, id=callback_data.id
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def item_search_keyboard(currency_name: str, item_name_contains: str):
    """Клавиатура получения предмета для продажи."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=SEARCH_LOT_LIST_BUTTON,
        callback_data=MarketplaceData(
            action=marketplace_action.search_lot_list,
            currency=currency_name,
            name_contains=item_name_contains,
        ),
    )
    keyboard.button(
        text=CANCEL_BUTTON,
        callback_data=MarketplaceData(action=marketplace_action.buy_preview),
    )
    keyboard.adjust(1)
    return keyboard


async def lot_item_list_keyboard(callback_data: MarketplaceData):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    async for item in (
        MarketplaceItem.objects.select_related("item", "sell_currency")
        .annotate(price_per_item=F("price") / F("amount"))
        .filter(
            item__name__contains=callback_data.name_contains,
            sell_currency__name=callback_data.currency,
        )
        .order_by("price_per_item")
    ):
        keyboard.button(
            text=item.name_with_price_and_amount,
            callback_data=MarketplaceData(
                action=marketplace_action.buy_get,
                page=callback_data.page,
                id=item.id,
                currency=callback_data.currency,
                name_contains=callback_data.name_contains,
                back_action=callback_data.action,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=marketplace_action.search_lot_list,
        size=6,
        page=callback_data.page,
        name_contains=callback_data.name_contains,
        currency=callback_data.currency,
    )
    return paginator.get_paginator_with_buttons_list(
        [
            (
                BACK_BUTTON,
                MarketplaceData(
                    action=marketplace_action.buy_preview,
                    currency=callback_data.currency,
                ),
            ),
        ]
    )
