from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from location.models import Location

from bot.character.keyboards import character_get_keyboard
from bot.character.utils import get_hunting_loot
from bot.constants.actions import location_action
from bot.constants.callback_data import LocationData
from bot.location.keyboards import (
    exit_location_confirmation,
    location_get_keyboard,
    location_list_keyboard,
)
from bot.location.messages import (
    EXIT_LOCATION_CONFIRMATION_MESSAGE,
    EXIT_LOCATION_MESSAGE,
    LOCATION_ENTER_MESSAGE,
    LOCATION_LIST_MESSAGE,
)
from bot.location.utils import enter_location, get_location_info
from bot.utils.schedulers import hunting_end_scheduler, remove_scheduler
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

location_router = Router()


@location_router.callback_query(
    LocationData.filter(F.action == location_action.list)
)
@log_in_dev
async def location_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: LocationData,
):
    """Коллбек получения локаций."""
    paginator = await location_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=LOCATION_LIST_MESSAGE, reply_markup=paginator
    )


@location_router.callback_query(
    LocationData.filter(F.action == location_action.get)
)
@log_in_dev
async def location_get(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: LocationData,
):
    """Коллбек получения локации."""
    user = await get_user(callback.from_user.id)
    keyboard = await location_get_keyboard(callback_data)
    location = await Location.objects.aget(pk=callback_data.id)
    await callback.message.edit_text(
        text=await get_location_info(user.character, location),
        reply_markup=keyboard.as_markup(),
    )


@location_router.callback_query(
    LocationData.filter(F.action == location_action.enter)
)
@log_in_dev
async def location_enter(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: LocationData,
):
    """Коллбек входа в локацию."""
    user = await get_user(callback.from_user.id)
    if user.character.current_location:
        await callback.message.delete()
        return
    location = await Location.objects.aget(pk=callback_data.id)
    await enter_location(user.character, location)
    time_left = str(
        user.character.hunting_end - user.character.hunting_begin
    ).split(".")[0]
    keyboard = await character_get_keyboard(user.character)
    await callback.message.edit_text(
        text=LOCATION_ENTER_MESSAGE.format(
            location.name,
            time_left,
        ),
        reply_markup=keyboard.as_markup(),
    )

    await hunting_end_scheduler(user)


@location_router.callback_query(
    LocationData.filter(F.action == location_action.exit_location_confirm)
)
@log_in_dev
async def exit_location_confirm(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: LocationData,
):
    """Хендлер подтверждения выхода из локации."""
    user = await get_user(callback.from_user.id)
    if not user.character.current_location:
        await callback.message.delete()
        return
    keyboard = await exit_location_confirmation()
    await callback.message.edit_text(
        text=EXIT_LOCATION_CONFIRMATION_MESSAGE,
        reply_markup=keyboard.as_markup(),
    )


@location_router.callback_query(
    LocationData.filter(F.action == location_action.exit_location)
)
@log_in_dev
async def exit_location(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: LocationData,
):
    """Хендлер выхода из локации."""
    user = await get_user(callback.from_user.id)
    if not user.character.current_location:
        await callback.message.delete()
        return
    await remove_scheduler(user.character.job_id)
    exp, drop_data = await get_hunting_loot(user.character)
    drop_text = ""
    for name, amount in drop_data.items():
        drop_text += f"<b>{name}</b> - {amount} шт.\n"
    if not drop_data:
        drop_text = "Не получено"
    keyboard = await character_get_keyboard(user.character)
    await callback.message.edit_text(
        text=EXIT_LOCATION_MESSAGE.format(exp, drop_text),
        reply_markup=keyboard.as_markup(),
    )
