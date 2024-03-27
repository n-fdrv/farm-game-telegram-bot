from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import Character

from bot.character.utils import get_character_about
from bot.command.buttons import TOP_BUTTON
from bot.constants.actions import top_action
from bot.constants.callback_data import TopData
from bot.top.keyboards import (
    top_get_keyboard,
    top_list_keyboard,
    top_preview_keyboard,
)
from bot.top.messages import (
    TOP_LIST_MESSAGE,
    TOP_PREVIEW_MESSAGE,
)
from core.config.logging import log_in_dev

top_router = Router()


@top_router.message(F.text == TOP_BUTTON)
@log_in_dev
async def top_preview_handler(message: types.Message, state: FSMContext):
    """Хендлер меню Топа персонажей."""
    await state.clear()
    keyboard = await top_preview_keyboard()
    await message.answer(
        text=TOP_PREVIEW_MESSAGE,
        reply_markup=keyboard.as_markup(),
    )


@top_router.callback_query(TopData.filter(F.action == top_action.preview))
@log_in_dev
async def top_preview_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: TopData,
):
    """Коллбек меню Топа персонажей."""
    await state.clear()
    keyboard = await top_preview_keyboard()
    await callback.message.edit_text(
        text=TOP_PREVIEW_MESSAGE,
        reply_markup=keyboard.as_markup(),
    )


@top_router.callback_query(TopData.filter(F.action == top_action.list))
@log_in_dev
async def top_by_kills_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: TopData,
):
    """Коллбек меню Топа персонажей."""
    paginator = await top_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=TOP_LIST_MESSAGE,
        reply_markup=paginator,
    )


@top_router.callback_query(TopData.filter(F.action == top_action.get))
@log_in_dev
async def top_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: TopData,
):
    """Коллбек меню Топа персонажей."""
    character = await Character.objects.select_related(
        "character_class", "clan"
    ).aget(pk=callback_data.id)
    keyboard = await top_get_keyboard(callback_data)
    await callback.message.edit_text(
        text=await get_character_about(character),
        reply_markup=keyboard.as_markup(),
    )
