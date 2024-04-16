import asyncio

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import Character
from location.models import Location, LocationBoss

from bot.character.keyboards import character_get_keyboard
from bot.character.utils import (
    check_clan_war_exists,
    get_character_info,
)
from bot.constants.actions import location_action
from bot.constants.callback_data import LocationData
from bot.location.keyboards import (
    attack_more_keyboard,
    boss_get_keyboard,
    boss_list_keyboard,
    character_list_keyboard,
    exit_location_confirmation,
    kill_character_confirm_keyboard,
    location_character_get_keyboard,
    location_get_keyboard,
    location_list_keyboard,
)
from bot.location.messages import (
    ATTACK_CHARACTER_MESSAGE,
    BOSS_LIST_MESSAGE,
    CHARACTER_KILL_CONFIRM_MESSAGE,
    CHARACTER_LIST_MESSAGE,
    EXIT_LOCATION_CONFIRMATION_MESSAGE,
    LOCATION_LIST_MESSAGE,
    NO_WAR_KILL_CONFIRM_MESSAGE,
    PREPARING_HUNTING_END_MESSAGE,
    WAR_KILL_CONFIRM_MESSAGE,
)
from bot.location.utils import (
    accept_location_boss_raid,
    attack_character,
    enter_location,
    exit_location,
    get_location_boss_info,
    get_location_info,
    location_get_character_about,
)
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
    location = await Location.objects.aget(pk=callback_data.id)
    success, text = await enter_location(
        user.character, location, callback.bot
    )
    keyboard = await character_get_keyboard(user.character)
    await callback.message.edit_text(
        text=text,
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
async def exit_location_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: LocationData,
):
    """Хендлер выхода из локации."""
    user = await get_user(callback.from_user.id)
    if not user.character.current_location:
        await callback.message.delete()
        return
    await callback.message.edit_text(text=PREPARING_HUNTING_END_MESSAGE)
    text = await exit_location(user.character, callback.bot)
    keyboard = await character_get_keyboard(user.character)
    await callback.message.edit_text(
        text=text,
    )
    await callback.message.answer(
        text=await get_character_info(user.character),
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
    user = await get_user(callback.from_user.id)
    if user.character.current_location:
        await callback.message.delete()
        return
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
    user = await get_user(callback.from_user.id)
    if user.character.current_location:
        await callback.message.delete()
        return
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
    user = await get_user(callback.from_user.id)
    enemy = await Character.objects.select_related(
        "character_class", "clan"
    ).aget(id=callback_data.character_id)
    keyboard = await kill_character_confirm_keyboard(callback_data)
    war_text = NO_WAR_KILL_CONFIRM_MESSAGE.format(enemy.name_with_clan)
    if await check_clan_war_exists(user.character, enemy):
        war_text = WAR_KILL_CONFIRM_MESSAGE
    await callback.message.edit_text(
        text=CHARACTER_KILL_CONFIRM_MESSAGE.format(
            enemy.name_with_class, enemy.name_with_class, war_text
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
    user = await get_user(callback.from_user.id)
    (more_attack, text, damage, callback_data.message_id) = (
        await attack_character(
            user.character,
            character,
            callback.bot,
            callback.message,
            callback_data.message_id,
        )
    )
    if not more_attack:
        keyboard = await character_get_keyboard(user.character)
        await callback.message.delete()
        await callback.message.answer(
            text=text,
            reply_markup=keyboard.as_markup(),
        )
        return
    await callback.message.edit_text(
        text=text,
    )
    seconds = 2
    for i in range(seconds):
        await asyncio.sleep(1)
        await callback.message.edit_text(
            text=ATTACK_CHARACTER_MESSAGE.format(damage, seconds - i),
        )
    keyboard = await attack_more_keyboard(callback_data)
    await callback.message.edit_text(
        text=ATTACK_CHARACTER_MESSAGE.format(damage, 0),
        reply_markup=keyboard.as_markup(),
    )


@location_router.callback_query(
    LocationData.filter(F.action == location_action.boss_list)
)
@log_in_dev
async def location_boss_list_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: LocationData,
):
    """Хендлер списка боссов локации."""
    paginator = await boss_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=BOSS_LIST_MESSAGE,
        reply_markup=paginator,
    )


@location_router.callback_query(
    LocationData.filter(F.action == location_action.boss_get)
)
@log_in_dev
async def location_boss_get_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: LocationData,
):
    """Хендлер списка боссов локации."""
    keyboard = await boss_get_keyboard(callback_data)
    boss = await LocationBoss.objects.aget(pk=callback_data.boss_id)
    await callback.message.edit_text(
        text=await get_location_boss_info(boss),
        reply_markup=keyboard.as_markup(),
    )


@location_router.callback_query(
    LocationData.filter(F.action == location_action.boss_accept)
)
@log_in_dev
async def location_boss_accept_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: LocationData,
):
    """Коллбек принятия участия в охоте на босса."""
    user = await get_user(callback.from_user.id)
    boss = await LocationBoss.objects.aget(pk=callback_data.id)
    success, text = await accept_location_boss_raid(boss, user.character)
    await callback.message.edit_text(
        text=text,
    )
