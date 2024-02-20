from aiogram import Router, types
from aiogram.filters import KICKED, ChatMemberUpdatedFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ChatMemberUpdated

from bot.constants import commands
from bot.models import User
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

router = Router()


@router.message(Command(commands.START_COMMAND))
@log_in_dev
async def start_handler(message: types.Message, state: FSMContext):
    """Хендлер при нажатии кнопки start."""
    await state.clear()
    user, created = await User.objects.aget_or_create(
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
    await message.answer(text="START_MESSAGE")


@router.message(Command(commands.HELP_COMMAND))
@log_in_dev
async def help_handler(message: types.Message, state: FSMContext):
    """Хендлер команды help."""
    await message.answer(text="HELP_MESSAGE")


@router.message(Command(commands.SUPPORT_COMMAND))
@log_in_dev
async def support_handler(message: types.Message, state: FSMContext):
    """Хендлер команды rules."""
    await message.answer(text="SUPPORT_MESSAGE")


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
@log_in_dev
async def block_handler(event: ChatMemberUpdated, state: FSMContext):
    """Хендлер при блокировке бота."""
    await state.clear()
    user = await get_user(event.from_user.id)
    user.is_active = False
    await user.asave(update_fields=("is_active",))
