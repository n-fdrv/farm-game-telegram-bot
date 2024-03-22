from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from bot.clan.keyboards import no_clan_preview_keyboard
from bot.clan.messages import NO_CLAN_MESSAGE
from bot.command.buttons import CLAN_BUTTON
from bot.command.keyboards import user_created_keyboard
from bot.command.messages import NOT_CREATED_CHARACTER_MESSAGE
from bot.constants.actions import clan_action
from bot.constants.callback_data import ClanData
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

clan_router = Router()


@clan_router.message(F.text == CLAN_BUTTON)
@log_in_dev
async def clan_preview_handler(message: types.Message, state: FSMContext):
    """Хендлер меню Клана."""
    await state.clear()
    user = await get_user(message.from_user.id)
    if not user.character:
        inline_keyboard = await user_created_keyboard()
        await message.answer(
            text=NOT_CREATED_CHARACTER_MESSAGE,
            reply_markup=inline_keyboard.as_markup(),
        )
        return
    if not user.character.clan:
        keyboard = await no_clan_preview_keyboard()
        await message.answer(
            text=NO_CLAN_MESSAGE,
            reply_markup=keyboard.as_markup(),
        )
        return


@clan_router.callback_query(ClanData.filter(F.action == clan_action.preview))
@log_in_dev
async def clan_preview_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек меню Клана."""
    await state.clear()
    user = await get_user(callback.from_user.id)
    if not user.character:
        inline_keyboard = await user_created_keyboard()
        await callback.message.edit_text(
            text=NOT_CREATED_CHARACTER_MESSAGE,
            reply_markup=inline_keyboard.as_markup(),
        )
        return
    if not user.character.clan:
        keyboard = await no_clan_preview_keyboard()
        await callback.message.edit_text(
            text=NO_CLAN_MESSAGE,
            reply_markup=keyboard.as_markup(),
        )
        return
