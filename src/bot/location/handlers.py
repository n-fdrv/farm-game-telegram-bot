from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import Character
from location.models import Location

from bot.character.keyboards import character_get_keyboard
from bot.character.utils import (
    get_character_info,
    get_hunting_loot,
)
from bot.constants.actions import location_action
from bot.constants.callback_data import LocationData
from bot.location.keyboards import (
    character_list_keyboard,
    exit_location_confirmation,
    kill_character_confirm_keyboard,
    location_character_get_keyboard,
    location_get_keyboard,
    location_list_keyboard,
)
from bot.location.messages import (
    CHARACTER_KILL_CONFIRM_MESSAGE,
    CHARACTER_LIST_MESSAGE,
    EXIT_LOCATION_CONFIRMATION_MESSAGE,
    HUNTING_END_MESSAGE,
    LOCATION_ENTER_MESSAGE,
    LOCATION_LIST_MESSAGE,
    NO_CHARACTER_CURRENT_LOCATION,
)
from bot.location.utils import (
    attack_character,
    check_location_access,
    enter_location,
    get_location_info,
    location_get_character_about,
)
from bot.utils.schedulers import remove_scheduler
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

location_router = Router()


@location_router.callback_query(
    LocationData.filter(F.action == location_action.list)
)
@log_in_dev
async def location_list_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: LocationData,
):
    """Коллбек получения списка локаций."""
    paginator = await location_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=LOCATION_LIST_MESSAGE, reply_markup=paginator
    )


@location_router.callback_query(
    LocationData.filter(F.action == location_action.get)
)
@log_in_dev
async def location_get_handler(
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
    success, text = await check_location_access(user.character, location)
    if not success:
        paginator = await location_list_keyboard(callback_data)
        await callback.message.edit_text(
            text=text,
            reply_markup=paginator,
        )
        return
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
    exp, drop_text = await get_hunting_loot(user.character)
    keyboard = await character_get_keyboard(user.character)
    await callback.message.edit_text(
        text=HUNTING_END_MESSAGE.format(int(exp), drop_text),
        reply_markup=keyboard.as_markup(),
    )


@location_router.callback_query(
    LocationData.filter(F.action == location_action.characters_list)
)
@log_in_dev
async def character_list_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: LocationData,
):
    """Хендлер подтверждения выхода из локации."""
    paginator = await character_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=CHARACTER_LIST_MESSAGE,
        reply_markup=paginator,
    )


@location_router.callback_query(
    LocationData.filter(F.action == location_action.characters_get)
)
@log_in_dev
async def location_character_get_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: LocationData,
):
    """Хендлер подтверждения выхода из локации."""
    character = await Character.objects.select_related(
        "current_location", "character_class", "clan"
    ).aget(id=callback_data.character_id)
    keyboard = await location_character_get_keyboard(callback_data)
    await callback.message.edit_text(
        text=await location_get_character_about(character),
        reply_markup=keyboard.as_markup(),
    )


@location_router.callback_query(
    LocationData.filter(F.action == location_action.characters_kill_confirm)
)
@log_in_dev
async def location_character_kill_confirm_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: LocationData,
):
    """Хендлер подтверждения выхода из локации."""
    character = await Character.objects.select_related(
        "character_class", "clan"
    ).aget(id=callback_data.character_id)
    keyboard = await kill_character_confirm_keyboard(callback_data)
    await callback.message.edit_text(
        text=CHARACTER_KILL_CONFIRM_MESSAGE.format(
            character.name_with_class, character.name_with_class
        ),
        reply_markup=keyboard.as_markup(),
    )


@location_router.callback_query(
    LocationData.filter(F.action == location_action.characters_kill)
)
@log_in_dev
async def location_character_kill_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: LocationData,
):
    """Хендлер подтверждения выхода из локации."""
    character = await Character.objects.select_related(
        "current_location", "character_class", "clan"
    ).aget(id=callback_data.character_id)
    if not character.current_location:
        await callback.message.edit_text(
            NO_CHARACTER_CURRENT_LOCATION.format(character.name_with_class),
        )
        return
    user = await get_user(callback.from_user.id)
    success, text = await attack_character(user.character, character)
    keyboard = await character_get_keyboard(user.character)
    await callback.message.edit_text(
        text=text,
    )
    await callback.message.answer(
        text=await get_character_info(user.character),
        reply_markup=keyboard.as_markup(),
    )
