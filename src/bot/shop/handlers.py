from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from bot.constants.actions import shop_action
from bot.constants.callback_data import ShopData
from bot.shop.keyboards import (
    buy_list_keyboard,
    sell_list_keyboard,
    shop_get_keyboard,
)
from bot.shop.messages import (
    BUY_LIST_MESSAGE,
    SELL_LIST_MESSAGE,
    SHOP_GET_MESSAGE,
)
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

shop_router = Router()


@shop_router.callback_query(ShopData.filter(F.action == shop_action.get))
@log_in_dev
async def shop_get(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Коллбек перехода в магазин."""
    keyboard = await shop_get_keyboard()
    await callback.message.edit_text(
        text=SHOP_GET_MESSAGE, reply_markup=keyboard.as_markup()
    )


@shop_router.callback_query(ShopData.filter(F.action == shop_action.buy_list))
@log_in_dev
async def shop_buy_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Коллбек перехода в покупки."""
    paginator = await buy_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=BUY_LIST_MESSAGE, reply_markup=paginator
    )


@shop_router.callback_query(ShopData.filter(F.action == shop_action.sell_list))
@log_in_dev
async def shop_sell_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Коллбек перехода в продажи."""
    user = await get_user(callback.from_user.id)
    paginator = await sell_list_keyboard(user, callback_data)
    await callback.message.edit_text(
        text=SELL_LIST_MESSAGE, reply_markup=paginator
    )
