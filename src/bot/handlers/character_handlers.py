from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from game.models import Character
from game.utils.character import (
    check_nickname_correct,
    check_nickname_exist,
    get_character_info,
)

from bot.constants.actions import character_action
from bot.constants.callback_data import CharacterData
from bot.constants.messages import character_messages
from bot.constants.states import CharacterState
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

router = Router()


@router.callback_query(
    CharacterData.filter(F.action == character_action.create_preview)
)
@log_in_dev
async def character_create(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер создания персонажа."""
    await callback.message.edit_text(
        text=character_messages.CREATE_CHARACTER_MESSAGE
        # TODO Возможно сделать клавиатуру отмены и редиректа куда-то
    )
    await state.set_state(CharacterState.enter_nickname)


@router.message(CharacterState.enter_nickname)
@log_in_dev
async def enter_nickname(message: types.Message, state: FSMContext):
    """Хендлер ввода никнейма персонажа."""
    nickname = message.text
    if await check_nickname_exist(nickname):
        await message.answer(text=character_messages.NICKNAME_TAKEN_MESSAGE)
        await state.set_state(CharacterState.enter_nickname)
        return
    if not check_nickname_correct(nickname):
        await message.answer(
            text=character_messages.NICKNAME_NOT_CORRECT_MESSAGE
        )
        await state.set_state(CharacterState.enter_nickname)
        return
    character = await Character.objects.acreate(name=nickname)
    user = await get_user(message.from_user.id)
    user.character = character
    await user.asave(update_fields=("character",))
    await message.answer(
        text=get_character_info(character),
        # TODO Клавиатура локаций, предметов и тд
    )
