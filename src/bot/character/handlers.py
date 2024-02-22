from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import CharacterClass

from bot.character.keyboards import (
    character_get_keyboard,
    choose_class_keyboard,
    class_get_keyboard,
    confirm_nickname_keyboard,
)
from bot.character.messages import (
    CHOOSE_CLASS_MESSAGE,
    CLASS_GET_MESSAGE,
    CREATE_CHARACTER_MESSAGE,
    NICKNAME_CONFIRM_MESSAGE,
    NICKNAME_NOT_CORRECT_MESSAGE,
    NICKNAME_TAKEN_MESSAGE,
)
from bot.character.utils import (
    check_nickname_correct,
    check_nickname_exist,
    create_character,
    get_character_info,
)
from bot.command.buttons import CHARACTER_BUTTON
from bot.command.keyboards import user_created_keyboard
from bot.command.messages import NOT_CREATED_CHARACTER_MESSAGE
from bot.constants.actions import character_action
from bot.constants.callback_data import CharacterData
from bot.constants.states import CharacterState
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

character_router = Router()


@character_router.message(F.text == CHARACTER_BUTTON)
@log_in_dev
async def character_get(message: types.Message, state: FSMContext):
    """Хендлер получения персонажа."""
    user = await get_user(message.from_user.id)
    if not user.character:
        inline_keyboard = await user_created_keyboard()
        await message.answer(
            text=NOT_CREATED_CHARACTER_MESSAGE,
            reply_markup=inline_keyboard.as_markup(),
        )
        return
    keyboard = await character_get_keyboard(user.character)
    await message.answer(
        text=get_character_info(user.character),
        reply_markup=keyboard.as_markup(),
    )


@character_router.callback_query(
    CharacterData.filter(F.action == character_action.get)
)
@log_in_dev
async def character_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Коллбек получения персонажа."""
    user = await get_user(callback.from_user.id)
    if not user.character:
        inline_keyboard = await user_created_keyboard()
        await callback.message.edit_text(
            text=NOT_CREATED_CHARACTER_MESSAGE,
            reply_markup=inline_keyboard.as_markup(),
        )
        return
    keyboard = await character_get_keyboard(user.character)
    await callback.message.edit_text(
        text=get_character_info(user.character),
        reply_markup=keyboard.as_markup(),
    )


@character_router.callback_query(
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
        text=CREATE_CHARACTER_MESSAGE
        # TODO Возможно сделать клавиатуру отмены и редиректа куда-то
    )
    await state.set_state(CharacterState.enter_nickname)


@character_router.message(CharacterState.enter_nickname)
@log_in_dev
async def check_nickname_handler(message: types.Message, state: FSMContext):
    """Хендлер ввода никнейма персонажа."""
    nickname = message.text
    if await check_nickname_exist(nickname):
        await message.answer(text=NICKNAME_TAKEN_MESSAGE)
        await state.set_state(CharacterState.enter_nickname)
        return
    if not check_nickname_correct(nickname):
        await message.answer(text=NICKNAME_NOT_CORRECT_MESSAGE)
        await state.set_state(CharacterState.enter_nickname)
        return
    await state.update_data(name=nickname)
    keyboard = await confirm_nickname_keyboard()
    await message.answer(
        text=NICKNAME_CONFIRM_MESSAGE.format(nickname),
        reply_markup=keyboard.as_markup(),
    )


@character_router.callback_query(
    CharacterData.filter(F.action == character_action.class_list)
)
@log_in_dev
async def class_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер получения всех профессий."""
    keyboard = await choose_class_keyboard()
    await callback.message.edit_text(
        text=CHOOSE_CLASS_MESSAGE, reply_markup=keyboard.as_markup()
    )


@character_router.callback_query(
    CharacterData.filter(F.action == character_action.class_get)
)
@log_in_dev
async def class_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер получения класса."""
    character_class = await CharacterClass.objects.aget(pk=callback_data.id)
    keyboard = await class_get_keyboard(callback_data)
    await callback.message.edit_text(
        text=CLASS_GET_MESSAGE.format(
            character_class.name,
            character_class.description,
            character_class.attack,
            character_class.defence,
            character_class.get_armor_type_display(),
            character_class.get_weapon_type_display(),
        ),
        reply_markup=keyboard.as_markup(),
    )


@character_router.callback_query(
    CharacterData.filter(F.action == character_action.create)
)
@log_in_dev
async def create_character_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер получения класса."""
    data = await state.get_data()
    user = await get_user(callback.from_user.id)
    nickname = data["name"]
    character_class = await CharacterClass.objects.aget(pk=callback_data.id)
    character = await create_character(user, nickname, character_class)
    keyboard = await character_get_keyboard(user.character)
    await callback.message.edit_text(
        text=get_character_info(character), reply_markup=keyboard.as_markup()
    )
