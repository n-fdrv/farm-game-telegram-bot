from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from item.models import Item

from bot.backpack.utils import add_item, remove_item
from bot.constants.actions import shop_action
from bot.constants.callback_data import ShopData
from bot.shop.keyboards import (
    buy_get_keyboard,
    buy_keyboard,
    buy_list_keyboard,
    sell_list_keyboard,
    shop_get_keyboard,
)
from bot.shop.messages import (
    BUY_LIST_MESSAGE,
    NOT_ENOUGH_GOLD_MESSAGE,
    SELL_LIST_MESSAGE,
    SHOP_GET_MESSAGE,
    SUCCESS_BUY_MESSAGE,
)
from bot.shop.utils import check_item_amount, get_item_info_text
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


@shop_router.callback_query(ShopData.filter(F.action == shop_action.buy_get))
@log_in_dev
async def shop_buy_get_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Хендлер товара для покупки."""
    item = await Item.objects.aget(pk=callback_data.id)
    keyboard = await buy_get_keyboard(callback_data)
    await callback.message.edit_text(
        text=await get_item_info_text(item), reply_markup=keyboard.as_markup()
    )


@shop_router.callback_query(ShopData.filter(F.action == shop_action.buy))
@log_in_dev
async def shop_buy_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Хендлер покупки товара."""
    item = await Item.objects.aget(pk=callback_data.id)
    user = await get_user(callback.from_user.id)
    gold = await Item.objects.aget(name="Золото")
    enough_amount = await check_item_amount(
        user.character, gold, item.buy_price
    )
    keyboard = await buy_keyboard()
    if not enough_amount:
        await callback.message.edit_text(
            text=NOT_ENOUGH_GOLD_MESSAGE, reply_markup=keyboard.as_markup()
        )
        return
    await remove_item(user.character, gold, item.buy_price)
    await add_item(user.character, item)
    await callback.message.edit_text(
        text=SUCCESS_BUY_MESSAGE.format(item.name_with_grade),
        reply_markup=keyboard.as_markup(),
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
