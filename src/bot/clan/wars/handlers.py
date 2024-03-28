from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from clan.models import Clan, ClanWar

from bot.clan.utils import get_clan_info
from bot.clan.wars.keyboards import (
    wars_accept_confirm_keyboard,
    wars_declare_confirm_keyboard,
    wars_declare_keyboard,
    wars_end_confirm_keyboard,
    wars_get_keyboard,
    wars_list_keyboard,
)
from bot.clan.wars.messages import (
    ACCEPT_WAR_CONFIRM_MESSAGE,
    DECLARE_WAR_CONFIRM_MESSAGE,
    END_WAR_CONFIRM_MESSAGE,
    ERROR_IN_CREATING_WAR_MESSAGE,
    NOT_FOUND_CLAN_MESSAGE,
    SUCCESS_ACCEPTING_WAR_MESSAGE,
    WAR_DECLARE_MESSAGE,
    WARS_LIST_MESSAGE,
)
from bot.clan.wars.utils import accept_war, declare_war, end_war
from bot.constants.actions import clan_action
from bot.constants.callback_data import ClanData
from bot.constants.states import ClanState
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

clan_wars_router = Router()


@clan_wars_router.callback_query(ClanData.filter(F.action == clan_action.wars))
@log_in_dev
async def wars_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    await state.clear()
    paginator = await wars_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=WARS_LIST_MESSAGE, reply_markup=paginator
    )


@clan_wars_router.callback_query(
    ClanData.filter(F.action == clan_action.wars_get)
)
@log_in_dev
async def wars_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    clan_war = await ClanWar.objects.select_related(
        "clan", "clan__leader", "enemy", "enemy__leader"
    ).aget(pk=callback_data.war_id)
    keyboard = await wars_get_keyboard(callback_data, clan_war)
    if callback_data.id == clan_war.clan.id:
        text = await get_clan_info(clan_war.enemy)
    else:
        text = await get_clan_info(clan_war.clan)
    await callback.message.edit_text(
        text=text, reply_markup=keyboard.as_markup()
    )


@clan_wars_router.callback_query(
    ClanData.filter(F.action == clan_action.wars_accept_confirm)
)
@log_in_dev
async def wars_accept_confirm_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    keyboard = await wars_accept_confirm_keyboard(callback_data)

    await callback.message.edit_text(
        text=ACCEPT_WAR_CONFIRM_MESSAGE, reply_markup=keyboard.as_markup()
    )


@clan_wars_router.callback_query(
    ClanData.filter(F.action == clan_action.wars_accept)
)
@log_in_dev
async def wars_accept_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    clan_war = await ClanWar.objects.select_related("clan", "enemy").aget(
        pk=callback_data.war_id
    )
    await accept_war(clan_war)
    paginator = await wars_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=SUCCESS_ACCEPTING_WAR_MESSAGE.format(clan_war.clan),
        reply_markup=paginator,
    )


@clan_wars_router.callback_query(
    ClanData.filter(F.action == clan_action.wars_end_confirm)
)
@log_in_dev
async def wars_end_confirm_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    keyboard = await wars_end_confirm_keyboard(callback_data)

    await callback.message.edit_text(
        text=END_WAR_CONFIRM_MESSAGE, reply_markup=keyboard.as_markup()
    )


@clan_wars_router.callback_query(
    ClanData.filter(F.action == clan_action.wars_end)
)
@log_in_dev
async def wars_end_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    clan_war = await ClanWar.objects.select_related("clan", "enemy").aget(
        pk=callback_data.war_id
    )
    user = await get_user(callback.from_user.id)
    success, text = await end_war(user.character.clan, clan_war)
    paginator = await wars_list_keyboard(callback_data)
    await callback.message.edit_text(text=text, reply_markup=paginator)


@clan_wars_router.callback_query(
    ClanData.filter(F.action == clan_action.wars_declare)
)
@log_in_dev
async def wars_declare_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    keyboard = await wars_declare_keyboard(callback_data)
    await state.set_state(ClanState.declare_war)
    await callback.message.edit_text(
        text=WAR_DECLARE_MESSAGE, reply_markup=keyboard.as_markup()
    )


@clan_wars_router.message(ClanState.declare_war)
@log_in_dev
async def wars_declare_name_handler(message: types.Message, state: FSMContext):
    """Хендлер ввода названия Клана."""
    name = message.text
    clan_exist = await Clan.objects.filter(name=name).aexists()
    if not clan_exist:
        await message.answer(text=NOT_FOUND_CLAN_MESSAGE.format(name))
        await state.set_state(ClanState.declare_war)
        return
    await state.update_data(name=name)
    user = await get_user(message.from_user.id)
    keyboard = await wars_declare_confirm_keyboard(user.character.clan.pk)
    await message.answer(
        text=DECLARE_WAR_CONFIRM_MESSAGE.format(name),
        reply_markup=keyboard.as_markup(),
    )


@clan_wars_router.callback_query(
    ClanData.filter(F.action == clan_action.wars_declare_set)
)
@log_in_dev
async def wars_declare_set_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    data = await state.get_data()
    if "name" not in data:
        await callback.message.edit_text(text=ERROR_IN_CREATING_WAR_MESSAGE)
        return
    clan = await Clan.objects.aget(pk=callback_data.id)
    enemy = await Clan.objects.aget(name=data["name"])
    success, text = await declare_war(clan, enemy)
    await callback.message.edit_text(text=text)
    await state.clear()
