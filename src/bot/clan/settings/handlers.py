from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from clan.models import Clan

from bot.clan.settings.keyboards import (
    settings_emoji_keyboard,
    settings_list_keyboard,
    to_settings_keyboard,
)
from bot.clan.settings.messages import (
    EMOJI_SET_MESSAGE,
    SETTINGS_EMOJI_MESSAGE,
    SETTINGS_LIST_MESSAGE,
)
from bot.constants.actions import clan_action
from bot.constants.callback_data import ClanData
from core.config.logging import log_in_dev

clan_settings_router = Router()


@clan_settings_router.callback_query(
    ClanData.filter(F.action == clan_action.settings)
)
@log_in_dev
async def settings_list_callback(
        callback: types.CallbackQuery,
        state: FSMContext,
        callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    keyboard = await settings_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=SETTINGS_LIST_MESSAGE, reply_markup=keyboard.as_markup()
    )


@clan_settings_router.callback_query(
    ClanData.filter(F.action == clan_action.settings_emoji)
)
@log_in_dev
async def settings_emoji_callback(
        callback: types.CallbackQuery,
        state: FSMContext,
        callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    paginator = await settings_emoji_keyboard(callback_data)
    clan = await Clan.objects.aget(pk=callback_data.id)
    emoji = "Нет"
    if clan.emoji:
        emoji = clan.emoji
    await callback.message.edit_text(
        text=SETTINGS_EMOJI_MESSAGE.format(emoji), reply_markup=paginator
    )


@clan_settings_router.callback_query(
    ClanData.filter(F.action == clan_action.settings_emoji_set)
)
@log_in_dev
async def settings_emoji_set_callback(
        callback: types.CallbackQuery,
        state: FSMContext,
        callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    keyboard = await to_settings_keyboard(callback_data)
    clan = await Clan.objects.aget(pk=callback_data.id)
    clan.emoji = callback_data.settings_value
    await clan.asave(update_fields=('emoji',))
    await callback.message.edit_text(
        text=EMOJI_SET_MESSAGE.format(callback_data.settings_value),
        reply_markup=keyboard.as_markup()
    )
