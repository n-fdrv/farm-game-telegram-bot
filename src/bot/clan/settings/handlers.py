from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from clan.models import Clan

from bot.clan.settings.keyboards import (
    settings_access_confirm_keyboard,
    settings_emoji_keyboard,
    settings_list_keyboard,
    settings_remove_confirm_keyboard,
    to_settings_keyboard,
)
from bot.clan.settings.messages import (
    BY_REQUEST_CLAN_DESCRIPTION,
    EMOJI_SET_MESSAGE,
    ERROR_IN_DESCRIPTION_CHANGE_MESSAGE,
    NO_CORRECT_DESCRIPTION_MESSAGE,
    OPEN_CLAN_DESCRIPTION,
    SETTINGS_ACCESS_CONFIRM_MESSAGE,
    SETTINGS_DESCRIPTION_MESSAGE,
    SETTINGS_EMOJI_MESSAGE,
    SETTINGS_LIST_MESSAGE,
    SETTINGS_REMOVE_CONFIRM_MESSAGE,
    SUCCESS_ACCESS_CHANGE_MESSAGE,
    SUCCESS_DESCRIPTION_CHANGE_MESSAGE,
)
from bot.clan.settings.utils import remove_clan
from bot.constants.actions import clan_action
from bot.constants.callback_data import ClanData
from bot.constants.states import ClanState
from bot.utils.user_helpers import get_user
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
    await state.clear()
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


@clan_settings_router.callback_query(
    ClanData.filter(F.action == clan_action.settings_description)
)
@log_in_dev
async def settings_description_callback(
        callback: types.CallbackQuery,
        state: FSMContext,
        callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    keyboard = await to_settings_keyboard(callback_data)
    clan = await Clan.objects.aget(pk=callback_data.id)
    await callback.message.edit_text(
        text=SETTINGS_DESCRIPTION_MESSAGE.format(
            clan.description
        ), reply_markup=keyboard.as_markup()
    )
    await state.update_data(clan=clan)
    await state.set_state(ClanState.settings_description)


@clan_settings_router.message(ClanState.settings_description)
@log_in_dev
async def enter_description_handler(message: types.Message, state: FSMContext):
    """Хендлер ввода названия Клана."""
    description = message.text
    data = await state.get_data()
    if 'clan' not in data:
        await message.answer(text=ERROR_IN_DESCRIPTION_CHANGE_MESSAGE)
        await state.set_state(ClanState.settings_description)
        return
    max_description_length = 128
    if len(description) > max_description_length:
        await message.answer(text=NO_CORRECT_DESCRIPTION_MESSAGE)
        await state.set_state(ClanState.settings_description)
        return
    data['clan'].description = description
    await data['clan'].asave(update_fields=('description',))
    await message.answer(
        text=SUCCESS_DESCRIPTION_CHANGE_MESSAGE
    )
    await state.clear()


@clan_settings_router.callback_query(
    ClanData.filter(F.action == clan_action.settings_access_confirm)
)
@log_in_dev
async def settings_access_confirm_callback(
        callback: types.CallbackQuery,
        state: FSMContext,
        callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    keyboard = await settings_access_confirm_keyboard(callback_data)
    clan = await Clan.objects.aget(pk=callback_data.id)
    access = "🔒По заявке"
    access_description = BY_REQUEST_CLAN_DESCRIPTION
    if clan.by_request:
        access = "🔓Открытый"
        access_description = OPEN_CLAN_DESCRIPTION
    await callback.message.edit_text(
        text=SETTINGS_ACCESS_CONFIRM_MESSAGE.format(
            access,
            access_description
        ), reply_markup=keyboard.as_markup()
    )


@clan_settings_router.callback_query(
    ClanData.filter(F.action == clan_action.settings_access)
)
@log_in_dev
async def settings_access_callback(
        callback: types.CallbackQuery,
        state: FSMContext,
        callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    keyboard = await to_settings_keyboard(callback_data)
    clan = await Clan.objects.aget(pk=callback_data.id)
    clan.by_request = not clan.by_request
    await clan.asave(update_fields=('by_request',))
    await callback.message.edit_text(
        text=SUCCESS_ACCESS_CHANGE_MESSAGE,
        reply_markup=keyboard.as_markup()
    )


@clan_settings_router.callback_query(
    ClanData.filter(F.action == clan_action.settings_remove)
)
@log_in_dev
async def settings_remove_confirm_callback(
        callback: types.CallbackQuery,
        state: FSMContext,
        callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    keyboard = await settings_remove_confirm_keyboard(callback_data)
    await callback.message.edit_text(
        text=SETTINGS_REMOVE_CONFIRM_MESSAGE,
        reply_markup=keyboard.as_markup()
    )


@clan_settings_router.callback_query(
    ClanData.filter(F.action == clan_action.remove)
)
@log_in_dev
async def settings_remove_clan_callback(
        callback: types.CallbackQuery,
        state: FSMContext,
        callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    keyboard = await to_settings_keyboard(callback_data)
    user = await get_user(callback.from_user.id)
    clan = await Clan.objects.select_related(
        "leader"
    ).aget(pk=callback_data.id)
    success, text = await remove_clan(user.character, clan)
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup()
    )
