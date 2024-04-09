from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from clan.models import ClanBoss

from bot.clan.bosses.keyboards import (
    clan_bosses_get_keyboard,
    clan_bosses_list_keyboard,
)
from bot.clan.bosses.messages import CLAN_BOSSES_LIST_MESSAGE
from bot.clan.bosses.utils import (
    accept_clan_boss_raid,
    accept_decline_clan_boss_hunting,
    alert_about_clan_boss_respawn,
    get_clan_boss_info,
)
from bot.constants.actions import clan_bosses_action
from bot.constants.callback_data import ClanBossesData
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

clan_bosses_router = Router()


@clan_bosses_router.callback_query(
    ClanBossesData.filter(F.action == clan_bosses_action.list)
)
@log_in_dev
async def clan_bosses_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanBossesData,
):
    """Коллбек списка клановых боссов."""
    await state.clear()
    paginator = await clan_bosses_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=CLAN_BOSSES_LIST_MESSAGE,
        reply_markup=paginator,
    )


@clan_bosses_router.callback_query(
    ClanBossesData.filter(F.action == clan_bosses_action.get)
)
@log_in_dev
async def clan_bosses_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanBossesData,
):
    """Коллбек списка клановых боссов."""
    user = await get_user(callback.from_user.id)
    boss = await ClanBoss.objects.aget(pk=callback_data.id)
    keyboard = await clan_bosses_get_keyboard(user.character, boss)
    await callback.message.edit_text(
        text=await get_clan_boss_info(boss, user.character.clan),
        reply_markup=keyboard.as_markup(),
    )


@clan_bosses_router.callback_query(
    ClanBossesData.filter(F.action == clan_bosses_action.create)
)
@log_in_dev
async def clan_bosses_create_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanBossesData,
):
    """Коллбек списка клановых боссов."""
    user = await get_user(callback.from_user.id)
    boss = await ClanBoss.objects.aget(pk=callback_data.id)
    await accept_decline_clan_boss_hunting(boss, user.character.clan)
    keyboard = await clan_bosses_get_keyboard(user.character, boss)
    await callback.message.edit_text(
        text=await get_clan_boss_info(boss, user.character.clan),
        reply_markup=keyboard.as_markup(),
    )
    await alert_about_clan_boss_respawn(boss, callback.bot)


@clan_bosses_router.callback_query(
    ClanBossesData.filter(F.action == clan_bosses_action.accept_raid)
)
@log_in_dev
async def clan_bosses_accept_raid_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanBossesData,
):
    """Коллбек списка клановых боссов."""
    user = await get_user(callback.from_user.id)
    boss = await ClanBoss.objects.aget(pk=callback_data.id)
    success, text = await accept_clan_boss_raid(boss, user.character)
    await callback.message.edit_text(
        text=text,
    )
