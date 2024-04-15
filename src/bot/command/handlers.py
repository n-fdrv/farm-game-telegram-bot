from aiogram import Router, types
from aiogram.filters import KICKED, ChatMemberUpdatedFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ChatMemberUpdated

from bot.character.keyboards import character_get_keyboard
from bot.character.utils import get_character_info
from bot.command.keyboards import start_keyboard, user_created_keyboard
from bot.command.messages import (
    BOT_IN_GROUP_MESSAGE,
    NOT_CREATED_CHARACTER_MESSAGE,
    START_MESSAGE,
)
from bot.constants import commands
from bot.models import User
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

command_router = Router()


@command_router.message(Command(commands.START_COMMAND))
@log_in_dev
async def start_handler(message: types.Message, state: FSMContext):
    """Хендлер при нажатии кнопки start."""
    await state.clear()
    if message.chat.type != "private":
        await message.answer(text=BOT_IN_GROUP_MESSAGE)
        await message.bot.leave_chat(chat_id=message.chat.id)
        return
    user, created = await User.objects.select_related(
        "character",
        "character__character_class",
        "character__clan",
        "character__current_location",
    ).aget_or_create(
        telegram_id=message.from_user.id,
    )
    user.first_name = message.from_user.first_name
    user.last_name = message.from_user.last_name
    user.telegram_username = message.from_user.username
    if not user.is_active:
        user.is_active = True
        await user.asave(update_fields=("is_active",))
    await user.asave(
        update_fields=("first_name", "last_name", "telegram_username")
    )
    keyboard = await start_keyboard()
    if not user.character:
        await message.answer(
            text=START_MESSAGE,
            reply_markup=keyboard.as_markup(resize_keyboard=True),
        )
        inline_keyboard = await user_created_keyboard()
        await message.answer(
            text=NOT_CREATED_CHARACTER_MESSAGE,
            reply_markup=inline_keyboard.as_markup(),
        )
        return
    await message.answer(
        text=START_MESSAGE,
        reply_markup=keyboard.as_markup(resize_keyboard=True),
    )
    keyboard = await character_get_keyboard(user.character)
    await message.answer(
        text=await get_character_info(user.character),
        reply_markup=keyboard.as_markup(),
    )


@command_router.message(Command(commands.HELP_COMMAND))
@log_in_dev
async def help_handler(message: types.Message, state: FSMContext):
    """Хендлер команды help."""
    await message.answer(text="HELP_MESSAGE")


@command_router.message(Command(commands.SUPPORT_COMMAND))
@log_in_dev
async def support_handler(message: types.Message, state: FSMContext):
    """Хендлер команды rules."""
    await message.answer(text="SUPPORT_MESSAGE")


@command_router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
@log_in_dev
async def block_handler(event: ChatMemberUpdated, state: FSMContext):
    """Хендлер при блокировке бота."""
    await state.clear()
    user = await get_user(event.from_user.id)
    user.is_active = False
    await user.asave(update_fields=("is_active",))
