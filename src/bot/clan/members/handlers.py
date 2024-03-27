from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import Character
from clan.models import Clan

from bot.character.utils import get_character_about
from bot.clan.members.keyboards import (
    member_kick_confirm_keyboard,
    member_kick_keyboard,
    members_get_keyboard,
    members_list_keyboard,
)
from bot.clan.members.messages import (
    MEMBER_KICK_CONFIRM_MESSAGE,
    MEMBERS_LIST_MESSAGE,
)
from bot.clan.members.utils import (
    kick_member,
)
from bot.constants.actions import clan_action
from bot.constants.callback_data import ClanData
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

clan_members_router = Router()


@clan_members_router.callback_query(
    ClanData.filter(F.action == clan_action.members)
)
@log_in_dev
async def members_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    paginator = await members_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=MEMBERS_LIST_MESSAGE, reply_markup=paginator
    )


@clan_members_router.callback_query(
    ClanData.filter(F.action == clan_action.members_get)
)
@log_in_dev
async def members_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    character = await Character.objects.select_related(
        "character_class", "clan"
    ).aget(pk=callback_data.character_id)
    user = await get_user(callback.from_user.id)
    keyboard = await members_get_keyboard(callback_data, user.character)
    await callback.message.edit_text(
        text=await get_character_about(character),
        reply_markup=keyboard.as_markup(),
    )


@clan_members_router.callback_query(
    ClanData.filter(F.action == clan_action.member_kick_confirm)
)
@log_in_dev
async def clan_member_kick_confirm_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    keyboard = await member_kick_confirm_keyboard(callback_data)
    await callback.message.edit_text(
        text=MEMBER_KICK_CONFIRM_MESSAGE, reply_markup=keyboard.as_markup()
    )


@clan_members_router.callback_query(
    ClanData.filter(F.action == clan_action.member_kick)
)
@log_in_dev
async def clan_member_kick_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    character = await Character.objects.select_related(
        "character_class", "clan"
    ).aget(pk=callback_data.character_id)
    clan = await Clan.objects.select_related("leader").aget(
        id=callback_data.id
    )
    success, text = await kick_member(character, clan)
    keyboard = await member_kick_keyboard(callback_data)
    await callback.message.edit_text(
        text=text, reply_markup=keyboard.as_markup()
    )
