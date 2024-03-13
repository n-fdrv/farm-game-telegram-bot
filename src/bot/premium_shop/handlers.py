from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from bot.command.buttons import PREMIUM_SHOP_BUTTON
from bot.constants.actions import premium_action
from bot.constants.callback_data import PremiumData
from bot.premium_shop.keyboards import (
    premium_get_keyboard,
    premium_list_keyboard,
)
from bot.premium_shop.messages import (
    NO_CHARACTER_MESSAGE,
    PREMIUM_GET_MESSAGE,
    PREMIUM_LIST_MESSAGE,
)
from bot.premium_shop.utils import buy_premium, buy_start_pack
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

premium_router = Router()


@premium_router.message(F.text == PREMIUM_SHOP_BUTTON)
@log_in_dev
async def premium_list_handler(message: types.Message, state: FSMContext):
    """Хендлер премиум магазина."""
    await state.clear()
    user = await get_user(message.from_user.id)
    if not user.character:
        await message.answer(text=NO_CHARACTER_MESSAGE)
        return
    keyboard = await premium_list_keyboard()
    await message.answer(
        text=PREMIUM_LIST_MESSAGE, reply_markup=keyboard.as_markup()
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
    """Коллбек премиум магазина."""
    user = await get_user(callback.from_user.id)
    if not user.character:
        await callback.message.edit_text(text=NO_CHARACTER_MESSAGE)
        return
    keyboard = await premium_list_keyboard()
    await callback.message.edit_text(
        text=PREMIUM_LIST_MESSAGE, reply_markup=keyboard.as_markup()
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
    await callback.message.edit_text(
        text=PREMIUM_GET_MESSAGE[callback_data.type],
        reply_markup=keyboard.as_markup(),
    )


@premium_router.callback_query(
    PremiumData.filter(F.action == premium_action.buy)
)
@log_in_dev
async def buy_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: PremiumData,
):
    """Покупка в премиум магазине."""
    user = await get_user(callback.from_user.id)
    if callback_data.type:
        success, text = await buy_premium(
            user.character, callback_data.type, callback_data.price
        )
    else:
        success, text = await buy_start_pack(
            user.character, callback_data.price
        )
    await callback.message.edit_text(
        text=text,
    )
