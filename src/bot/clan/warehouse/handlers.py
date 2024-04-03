from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from bot.clan.warehouse.keyboards import (
    clan_warehouse_get_keyboard,
    clan_warehouse_list_keyboard,
    clan_warehouse_look_keyboard,
    clan_warehouse_preview_keyboard,
)
from bot.clan.warehouse.messages import (
    LOOK_WAREHOUSE_MESSAGE,
    WAREHOUSE_PREVIEW_MESSAGE,
)
from bot.constants.actions import clan_warehouse_action
from bot.constants.callback_data import ClanWarehouseData
from core.config.logging import log_in_dev

clan_warehouse_router = Router()


@clan_warehouse_router.callback_query(
    ClanWarehouseData.filter(F.action == clan_warehouse_action.preview)
)
@log_in_dev
async def clan_warehouse_preview_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanWarehouseData,
):
    """Коллбек получения хранилища."""
    keyboard = await clan_warehouse_preview_keyboard(callback_data)
    await callback.message.edit_text(
        text=WAREHOUSE_PREVIEW_MESSAGE,
        reply_markup=keyboard.as_markup(),
    )


@clan_warehouse_router.callback_query(
    ClanWarehouseData.filter(F.action == clan_warehouse_action.look)
)
@log_in_dev
async def clan_warehouse_look_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanWarehouseData,
):
    """Коллбек просмотра хранилища."""
    keyboard = await clan_warehouse_look_keyboard(callback_data)
    await callback.message.edit_text(
        text=LOOK_WAREHOUSE_MESSAGE,
        reply_markup=keyboard.as_markup(),
    )


@clan_warehouse_router.callback_query(
    ClanWarehouseData.filter(F.action == clan_warehouse_action.list)
)
@log_in_dev
async def clan_warehouse_list_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanWarehouseData,
):
    """Коллбек просмотра типа предметов в хранилище."""
    paginator = await clan_warehouse_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=LOOK_WAREHOUSE_MESSAGE,
        reply_markup=paginator,
    )


@clan_warehouse_router.callback_query(
    ClanWarehouseData.filter(F.action == clan_warehouse_action.get)
)
@log_in_dev
async def clan_warehouse_get_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanWarehouseData,
):
    """Коллбек просмотра предмета в хранилище."""
    paginator = await clan_warehouse_get_keyboard(callback_data)
    await callback.message.edit_text(
        text=LOOK_WAREHOUSE_MESSAGE,
        reply_markup=paginator,
    )
