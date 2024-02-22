from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import Character
from game.utils.character import (
    check_nickname_correct,
    check_nickname_exist,
    get_character_info,
    get_hunting_loot,
)

from bot.constants.actions import character_action
from bot.constants.buttons.main_buttons import CHARACTER_BUTTON
from bot.constants.callback_data import CharacterData
from bot.constants.messages import character_messages, main_menu_messages
from bot.constants.states import CharacterState
from bot.keyboards import character_keyboards, main_keyboards
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

router = Router()


@router.message(F.text == CHARACTER_BUTTON)
@log_in_dev
async def character_get(message: types.Message, state: FSMContext):
    """Хендлер получения персонажа."""
    user = await get_user(message.from_user.id)
    if not user.character:
        inline_keyboard = await main_keyboards.user_created_keyboard()
        await message.answer(
            text=main_menu_messages.NOT_CREATED_CHARACTER_MESSAGE,
            reply_markup=inline_keyboard.as_markup(),
        )
        return
    keyboard = await character_keyboards.character_get(user.character)
    await message.answer(
        text=get_character_info(user.character),
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(CharacterData.filter(F.action == character_action.get))
@log_in_dev
async def character_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Коллбек получения персонажа."""
    user = await get_user(callback.from_user.id)
    if not user.character:
        inline_keyboard = await main_keyboards.user_created_keyboard()
        await callback.message.edit_text(
            text=main_menu_messages.NOT_CREATED_CHARACTER_MESSAGE,
            reply_markup=inline_keyboard.as_markup(),
        )
        return
    keyboard = await character_keyboards.character_get(user.character)
    await callback.message.edit_text(
        text=get_character_info(user.character),
        reply_markup=keyboard.as_markup(),
    )


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
    keyboard = await character_keyboards.character_get(user.character)
    await message.answer(
        text=get_character_info(character), reply_markup=keyboard.as_markup()
    )


@router.callback_query(
    CharacterData.filter(F.action == character_action.exit_location_confirm)
)
@log_in_dev
async def exit_location_confirm(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер подтверждения выхода из локации."""
    user = await get_user(callback.from_user.id)
    if not user.character.current_location:
        await callback.message.delete()
        return
    keyboard = await character_keyboards.exit_location_confirmation()
    await callback.message.edit_text(
        text=character_messages.EXIT_LOCATION_CONFIRMATION_MESSAGE,
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(
    CharacterData.filter(F.action == character_action.exit_location)
)
@log_in_dev
async def exit_location(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер выхода из локации."""
    user = await get_user(callback.from_user.id)
    if not user.character.current_location:
        await callback.message.delete()
        return
    exp, drop_data = await get_hunting_loot(user.character)
    drop_text = ""
    for name, amount in drop_data.items():
        drop_text += f"<b>{name}</b> - {amount} шт.\n"
    if not drop_data:
        drop_text = "Не получено"
    await callback.message.edit_text(
        text=character_messages.EXIT_LOCATION_MESSAGE.format(exp, drop_text)
    )
