from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from location.models import Dungeon

from bot.character.keyboards import character_get_keyboard
from bot.constants.actions import dungeon_action
from bot.constants.callback_data import DungeonData
from bot.hunting.dungeon.keyboards import (
    dungeon_get_keyboard,
    dungeon_list_keyboard,
    enter_dungeon_confirm_keyboard,
)
from bot.hunting.dungeon.messages import (
    DUNGEON_LIST_MESSAGE,
    ENTER_DUNGEON_CONFIRM_MESSAGE,
)
from bot.hunting.utils import enter_hunting_zone, get_hunting_zone_info
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

dungeon_router = Router()


@dungeon_router.callback_query(
    DungeonData.filter(F.action == dungeon_action.list)
)
@log_in_dev
async def dungeon_list_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: DungeonData,
):
    """Коллбек получения списка подземелий."""
    user = await get_user(callback.from_user.id)
    paginator = await dungeon_list_keyboard(user.character, callback_data)
    await callback.message.edit_text(
        text=DUNGEON_LIST_MESSAGE, reply_markup=paginator
    )


@dungeon_router.callback_query(
    DungeonData.filter(F.action == dungeon_action.get)
)
@log_in_dev
async def dungeon_get_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: DungeonData,
):
    """Коллбек получения подземелья."""
    user = await get_user(callback.from_user.id)
    dungeon = await Dungeon.objects.aget(pk=callback_data.id)
    keyboard = await dungeon_get_keyboard(callback_data)
    await callback.message.edit_text(
        text=await get_hunting_zone_info(user.character, dungeon),
        reply_markup=keyboard.as_markup(),
    )


@dungeon_router.callback_query(
    DungeonData.filter(F.action == dungeon_action.enter_confirm)
)
@log_in_dev
async def dungeon_enter_confirm_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: DungeonData,
):
    """Коллбек получения подземелья."""
    keyboard = await enter_dungeon_confirm_keyboard(callback_data)
    await callback.message.edit_text(
        text=ENTER_DUNGEON_CONFIRM_MESSAGE, reply_markup=keyboard.as_markup()
    )


@dungeon_router.callback_query(
    DungeonData.filter(F.action == dungeon_action.enter)
)
@log_in_dev
async def location_enter(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: DungeonData,
):
    """Коллбек входа в подземелье."""
    user = await get_user(callback.from_user.id)
    dungeon = await Dungeon.objects.aget(pk=callback_data.id)
    success, text = await enter_hunting_zone(
        user.character, dungeon, callback.bot
    )
    keyboard = await character_get_keyboard(user.character)
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup(),
    )
