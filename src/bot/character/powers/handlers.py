from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import Power

from bot.character.powers.keyboards import (
    powers_add_confirm_keyboard,
    powers_get_keyboard,
    powers_list_keyboard,
    powers_reset_confirm_keyboard,
    powers_reset_keyboard,
)
from bot.character.powers.messages import (
    POWER_ADD_CONFIRM_MESSAGE,
    POWER_RESET_CONFIRM_MESSAGE,
)
from bot.character.powers.utils import (
    get_character_power_info,
    get_power_info,
    power_add,
    power_reset,
)
from bot.constants.actions import character_action
from bot.constants.callback_data import CharacterData
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

character_powers_router = Router()


@character_powers_router.callback_query(
    CharacterData.filter(F.action == character_action.power_list)
)
@log_in_dev
async def powers_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер получения списка сил."""
    user = await get_user(callback.from_user.id)
    keyboard = await powers_list_keyboard()
    await callback.message.edit_text(
        text=await get_character_power_info(user.character),
        reply_markup=keyboard.as_markup(),
    )


@character_powers_router.callback_query(
    CharacterData.filter(F.action == character_action.power_reset_confirm)
)
@log_in_dev
async def powers_reset_confirm_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер получения списка сил."""
    keyboard = await powers_reset_confirm_keyboard()
    await callback.message.edit_text(
        text=POWER_RESET_CONFIRM_MESSAGE, reply_markup=keyboard.as_markup()
    )


@character_powers_router.callback_query(
    CharacterData.filter(F.action == character_action.power_reset)
)
@log_in_dev
async def powers_reset_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер получения списка сил."""
    user = await get_user(callback.from_user.id)
    success, text = await power_reset(user.character)
    keyboard = await powers_reset_keyboard()
    await callback.message.edit_text(
        text=text, reply_markup=keyboard.as_markup()
    )


@character_powers_router.callback_query(
    CharacterData.filter(F.action == character_action.power_get)
)
@log_in_dev
async def powers_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер получения списка сил."""
    power = await Power.objects.select_related("effect").aget(
        pk=callback_data.id
    )
    keyboard = await powers_get_keyboard(callback_data)
    await callback.message.edit_text(
        text=await get_power_info(power), reply_markup=keyboard.as_markup()
    )


@character_powers_router.callback_query(
    CharacterData.filter(F.action == character_action.power_add_confirm)
)
@log_in_dev
async def powers_add_confirm_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер получения списка сил."""
    keyboard = await powers_add_confirm_keyboard(callback_data)
    await callback.message.edit_text(
        text=POWER_ADD_CONFIRM_MESSAGE, reply_markup=keyboard.as_markup()
    )


@character_powers_router.callback_query(
    CharacterData.filter(F.action == character_action.power_add)
)
@log_in_dev
async def powers_add_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер получения списка сил."""
    user = await get_user(callback.from_user.id)
    power = await Power.objects.aget(pk=callback_data.id)
    success, text = await power_add(user.character, power)
    keyboard = await powers_reset_keyboard()
    await callback.message.edit_text(
        text=text, reply_markup=keyboard.as_markup()
    )
