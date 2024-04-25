from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from premium_shop.models import PremiumLot

from bot.command.buttons import PREMIUM_SHOP_BUTTON
from bot.constants.actions import premium_action
from bot.constants.callback_data import PremiumData
from bot.premium_shop.keyboards import (
    diamonds_keyboard,
    premium_buy_confirm_keyboard,
    premium_buy_keyboard,
    premium_choose_type_keyboard,
    premium_get_keyboard,
    premium_list_keyboard,
    premium_preview_keyboard,
)
from bot.premium_shop.messages import (
    DIAMONDS_MESSAGE,
    NO_CHARACTER_MESSAGE,
    PREMIUM_BUY_CONFIRM_MESSAGE,
    PREMIUM_LIST_MESSAGE,
    PREMIUM_PREVIEW_MESSAGE,
)
from bot.premium_shop.utils import get_premium_lot, premium_lot_get_info
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

premium_router = Router()


@premium_router.message(F.text == PREMIUM_SHOP_BUTTON)
@log_in_dev
async def premium_preview_handler(message: types.Message, state: FSMContext):
    """Хендлер премиум магазина."""
    await state.clear()
    user = await get_user(message.from_user.id)
    if not user.character:
        await message.answer(text=NO_CHARACTER_MESSAGE)
        return
    keyboard = await premium_preview_keyboard()
    await message.answer(
        text=PREMIUM_PREVIEW_MESSAGE, reply_markup=keyboard.as_markup()
    )


@premium_router.callback_query(
    PremiumData.filter(F.action == premium_action.preview)
)
@log_in_dev
async def premium_preview_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: PremiumData,
):
    """Коллбек премиум магазина."""
    user = await get_user(callback.from_user.id)
    if not user.character:
        await callback.message.edit_text(text=NO_CHARACTER_MESSAGE)
        return
    keyboard = await premium_preview_keyboard()
    await callback.message.edit_text(
        text=PREMIUM_PREVIEW_MESSAGE, reply_markup=keyboard.as_markup()
    )


@premium_router.callback_query(
    PremiumData.filter(F.action == premium_action.diamonds)
)
@log_in_dev
async def premium_diamonds_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: PremiumData,
):
    """Коллбек получения предмета премиум магазина."""
    keyboard = await diamonds_keyboard()
    await callback.message.edit_text(
        text=DIAMONDS_MESSAGE,
        reply_markup=keyboard.as_markup(),
    )


@premium_router.callback_query(
    PremiumData.filter(F.action == premium_action.choose_type)
)
@log_in_dev
async def premium_choose_type_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: PremiumData,
):
    """Коллбек получения предмета премиум магазина."""
    keyboard = await premium_choose_type_keyboard()
    await callback.message.edit_text(
        text=PREMIUM_LIST_MESSAGE,
        reply_markup=keyboard.as_markup(),
    )


@premium_router.callback_query(
    PremiumData.filter(F.action == premium_action.list)
)
@log_in_dev
async def premium_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: PremiumData,
):
    """Коллбек получения предмета премиум магазина."""
    paginator = await premium_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=PREMIUM_LIST_MESSAGE,
        reply_markup=paginator,
    )


@premium_router.callback_query(
    PremiumData.filter(F.action == premium_action.get)
)
@log_in_dev
async def premium_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: PremiumData,
):
    """Коллбек получения предмета премиум магазина."""
    keyboard = await premium_get_keyboard(callback_data)
    premium_lot = await PremiumLot.objects.aget(pk=callback_data.id)
    await callback.message.edit_text(
        text=await premium_lot_get_info(premium_lot),
        reply_markup=keyboard.as_markup(),
    )


@premium_router.callback_query(
    PremiumData.filter(F.action == premium_action.buy_confirm)
)
@log_in_dev
async def premium_buy_confirm_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: PremiumData,
):
    """Покупка в премиум магазине."""
    keyboard = await premium_buy_confirm_keyboard(callback_data)
    await callback.message.edit_text(
        text=PREMIUM_BUY_CONFIRM_MESSAGE, reply_markup=keyboard.as_markup()
    )


@premium_router.callback_query(
    PremiumData.filter(F.action == premium_action.buy)
)
@log_in_dev
async def premium_buy_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: PremiumData,
):
    """Покупка в премиум магазине."""
    user = await get_user(callback.from_user.id)
    premium_lot = await PremiumLot.objects.aget(pk=callback_data.id)
    success, text = await get_premium_lot(user.character, premium_lot)
    keyboard = await premium_buy_keyboard(callback_data)
    await callback.message.edit_text(
        text=text, reply_markup=keyboard.as_markup()
    )
