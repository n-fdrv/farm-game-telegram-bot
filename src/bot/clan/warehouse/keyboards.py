from aiogram.utils.keyboard import InlineKeyboardBuilder
from clan.models import Clan, ClanWarehouse
from django.db.models import Count
from item.models import ItemType

from bot.clan.warehouse.buttons import LOOK_WAREHOUSE_BUTTON, PUT_ITEM_BUTTON
from bot.command.buttons import BACK_BUTTON
from bot.constants.actions import (
    clan_action,
    clan_warehouse_action,
)
from bot.constants.callback_data import (
    ClanData,
    ClanWarehouseData,
)
from bot.utils.paginator import Paginator


async def clan_warehouse_preview_keyboard(callback_data: ClanWarehouseData):
    """Клавиатура неудачного надевания предмета."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=LOOK_WAREHOUSE_BUTTON,
        callback_data=ClanWarehouseData(
            action=clan_warehouse_action.look,
            id=callback_data.id,
        ),
    )
    keyboard.button(
        text=PUT_ITEM_BUTTON,
        callback_data=ClanWarehouseData(
            action=clan_warehouse_action.put,
            id=callback_data.id,
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=ClanData(
            action=clan_action.preview,
            id=callback_data.id,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def clan_warehouse_look_keyboard(callback_data: ClanWarehouseData):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    button_number = 0
    row = []
    button_in_row = 2
    clan = await Clan.objects.aget(pk=callback_data.id)
    items_data = [
        x
        async for x in clan.warehouse.values_list("type", flat=True)
        .annotate(Count("type"))
        .all()
    ]
    for item_type in ItemType.choices:
        if item_type[0] in items_data:
            keyboard.button(
                text=item_type[1],
                callback_data=ClanWarehouseData(
                    action=clan_warehouse_action.list,
                    id=callback_data.id,
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
        callback_data=ClanWarehouseData(
            action=clan_warehouse_action.preview, id=callback_data.id
        ),
    )
    keyboard.adjust(*row, 1)
    return keyboard


async def clan_warehouse_list_keyboard(callback_data: ClanWarehouseData):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    clan = await Clan.objects.aget(pk=callback_data.id)
    async for item in (
        ClanWarehouse.objects.select_related("item")
        .filter(clan=clan, item__type=callback_data.type)
        .order_by("item__name")
    ):
        keyboard.button(
            text=f"{item.name_with_enhance} - {item.amount} шт.",
            callback_data=ClanWarehouseData(
                action=clan_warehouse_action.get,
                id=callback_data.id,
                page=callback_data.page,
                item_id=item.id,
                type=callback_data.type,
                amount=item.amount,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=clan_warehouse_action.list,
        size=6,
        id=callback_data.id,
        page=callback_data.page,
        type=callback_data.type,
    )
    return paginator.get_paginator_with_buttons_list(
        [
            [
                BACK_BUTTON,
                ClanWarehouseData(
                    action=clan_warehouse_action.look,
                    id=callback_data.id,
                ),
            ]
        ]
    )


async def clan_warehouse_get_keyboard(callback_data: ClanWarehouseData):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=ClanWarehouseData(
            action=clan_warehouse_action.list,
            id=callback_data.id,
            page=callback_data.page,
            type=callback_data.type,
        ),
    )
    keyboard.adjust(1)
    return keyboard