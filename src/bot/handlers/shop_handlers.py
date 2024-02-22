from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from bot.constants.actions import shop_action
from bot.constants.callback_data import ShopData
from bot.constants.messages import shop_messages
from bot.keyboards import shop_keyboards
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

router = Router()


@router.callback_query(ShopData.filter(F.action == shop_action.get))
@log_in_dev
async def shop_get(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Коллбек перехода в магазин."""
    keyboard = await shop_keyboards.shop_get()
    await callback.message.edit_text(
        text=shop_messages.SHOP_GET_MESSAGE, reply_markup=keyboard.as_markup()
    )


@router.callback_query(ShopData.filter(F.action == shop_action.buy_list))
@log_in_dev
async def shop_buy_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Коллбек перехода в покупки."""
    paginator = await shop_keyboards.buy_list(callback_data)
    await callback.message.edit_text(
        text=shop_messages.BUY_LIST_MESSAGE, reply_markup=paginator
    )


@router.callback_query(ShopData.filter(F.action == shop_action.sell_list))
@log_in_dev
async def shop_sell_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Коллбек перехода в продажи."""
    user = await get_user(callback.from_user.id)
    paginator = await shop_keyboards.sell_list(user, callback_data)
    await callback.message.edit_text(
        text=shop_messages.SELL_LIST_MESSAGE, reply_markup=paginator
    )
