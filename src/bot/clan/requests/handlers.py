from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import Character
from clan.models import Clan

from bot.character.utils import get_character_about
from bot.clan.requests.keyboards import (
    create_request_confirm_keyboard,
    create_request_keyboard,
    request_get_keyboard,
    request_list_keyboard,
)
from bot.clan.requests.messages import (
    CREATE_REQUEST_CONFIRM_MESSAGE,
    REQUEST_LIST_MESSAGE,
)
from bot.clan.requests.utils import (
    accept_request,
    create_request,
    decline_request,
)
from bot.constants.actions import clan_action
from bot.constants.callback_data import ClanData
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

clan_request_router = Router()


@clan_request_router.callback_query(
    ClanData.filter(F.action == clan_action.create_request_confirm)
)
@log_in_dev
async def clan_create_request_confirm_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    keyboard = await create_request_confirm_keyboard(callback_data)
    await callback.message.edit_text(
        text=CREATE_REQUEST_CONFIRM_MESSAGE, reply_markup=keyboard.as_markup()
    )


@clan_request_router.callback_query(
    ClanData.filter(F.action == clan_action.create_request)
)
@log_in_dev
async def clan_create_request_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    user = await get_user(callback.from_user.id)
    clan = await Clan.objects.select_related("leader").aget(
        pk=callback_data.id
    )
    success, text = await create_request(user.character, clan)
    keyboard = await create_request_keyboard(callback_data)
    await callback.message.edit_text(
        text=text, reply_markup=keyboard.as_markup()
    )


@clan_request_router.callback_query(
    ClanData.filter(F.action == clan_action.request_list)
)
@log_in_dev
async def clan_request_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    paginator = await request_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=REQUEST_LIST_MESSAGE, reply_markup=paginator
    )


@clan_request_router.callback_query(
    ClanData.filter(F.action == clan_action.request_get)
)
@log_in_dev
async def clan_request_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    character = await Character.objects.select_related(
        "character_class", "clan"
    ).aget(pk=callback_data.character_id)
    keyboard = await request_get_keyboard(callback_data)
    await callback.message.edit_text(
        text=await get_character_about(character),
        reply_markup=keyboard.as_markup(),
    )


@clan_request_router.callback_query(
    ClanData.filter(F.action == clan_action.request_accept)
)
@log_in_dev
async def clan_request_accept_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    user = await get_user(callback.from_user.id)
    character = await Character.objects.select_related(
        "character_class", "clan"
    ).aget(pk=callback_data.character_id)
    success, text = await accept_request(character, user.character.clan)
    await callback.message.edit_text(text=text)
    paginator = await request_list_keyboard(callback_data)
    await callback.message.answer(
        text=REQUEST_LIST_MESSAGE, reply_markup=paginator
    )


@clan_request_router.callback_query(
    ClanData.filter(F.action == clan_action.request_decline)
)
@log_in_dev
async def clan_request_decline_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    user = await get_user(callback.from_user.id)
    character = await Character.objects.select_related(
        "character_class", "clan"
    ).aget(pk=callback_data.character_id)
    success, text = await decline_request(character, user.character.clan)
    await callback.message.edit_text(text=text)
    paginator = await request_list_keyboard(callback_data)
    await callback.message.answer(
        text=REQUEST_LIST_MESSAGE, reply_markup=paginator
    )
