from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import CharacterClass
from item.models import EffectProperty

from bot.character.keyboards import (
    about_keyboard,
    character_get_keyboard,
    choose_class_keyboard,
    class_get_keyboard,
    confirm_nickname_keyboard,
)
from bot.character.messages import (
    CHOOSE_CLASS_MESSAGE,
    CLASS_GET_MESSAGE,
    CREATE_CHARACTER_MESSAGE,
    ERROR_CREATING_CHARACTER,
    NICKNAME_CONFIRM_MESSAGE,
    NICKNAME_NOT_CORRECT_MESSAGE,
    NICKNAME_TAKEN_MESSAGE,
    SUCCESS_CREATING_CHARACTER,
)
from bot.character.utils import (
    check_nickname_correct,
    check_nickname_exist,
    create_character,
    get_character_about,
    get_character_info,
)
from bot.command.buttons import CHARACTER_BUTTON
from bot.command.keyboards import start_keyboard, user_created_keyboard
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
    await state.clear()
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
        text=await get_character_info(user.character),
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
        text=await get_character_info(user.character),
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
    await callback.message.edit_text(text=CREATE_CHARACTER_MESSAGE)
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
            character_class.emoji_name,
            character_class.description,
            character_class.attack,
            character_class.defence,
            ", ".join(
                [
                    x.get_type_display()
                    async for x in character_class.equip.all()
                ]
            ),
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
    """Хендлер создания персонажа."""
    data = await state.get_data()
    await state.clear()
    user = await get_user(callback.from_user.id)
    if "name" not in data:
        await callback.message.edit_text(
            text=ERROR_CREATING_CHARACTER,
        )
        return
    nickname = data["name"]
    character_class = await CharacterClass.objects.aget(pk=callback_data.id)
    character = await create_character(user, nickname, character_class)
    keyboard = await start_keyboard()
    await callback.message.answer(
        text=SUCCESS_CREATING_CHARACTER,
        reply_markup=keyboard.as_markup(resize_keyboard=True),
    )
    keyboard = await character_get_keyboard(user.character)
    await callback.message.edit_text(
        text=await get_character_info(character),
        reply_markup=keyboard.as_markup(),
    )


@character_router.callback_query(
    CharacterData.filter(F.action == character_action.about)
)
@log_in_dev
async def about_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер информации о персонаже."""
    user = await get_user(callback.from_user.id)
    keyboard = await about_keyboard(user.character)
    await callback.message.edit_text(
        text=await get_character_about(user.character),
        reply_markup=keyboard.as_markup(),
    )


@character_router.callback_query(
    CharacterData.filter(F.action == character_action.auto_use)
)
@log_in_dev
async def auto_use_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер переключения автоиспользования."""
    user = await get_user(callback.from_user.id)
    if callback_data.type == EffectProperty.HEALTH:
        user.character.auto_use_hp_potion = (
            not user.character.auto_use_hp_potion
        )
        await user.character.asave(update_fields=("auto_use_hp_potion",))
    elif callback_data.type == EffectProperty.MANA:
        user.character.auto_use_mp_potion = (
            not user.character.auto_use_mp_potion
        )
        await user.character.asave(update_fields=("auto_use_mp_potion",))
    keyboard = await about_keyboard(user.character)
    await callback.message.edit_text(
        text=await get_character_about(user.character),
        reply_markup=keyboard.as_markup(),
    )
