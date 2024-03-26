from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import Character
from clan.models import Clan

from bot.character.utils import get_character_about
from bot.clan.keyboards import (
    clan_create_request_confirm_keyboard,
    clan_create_request_keyboard,
    clan_enter_confirm_keyboard,
    clan_exit_confirm_keyboard,
    clan_get_keyboard,
    clan_guest_get_keyboard,
    clan_list_keyboard,
    clan_request_get_keyboard,
    clan_request_list_keyboard,
    clan_search_keyboard,
    confirm_clan_name_keyboard,
    members_list_keyboard,
    no_clan_preview_keyboard,
    search_clan_list_keyboard,
    to_preview_keyboard,
)
from bot.clan.messages import (
    CLAN_ENTER_CONFIRM_MESSAGE,
    CLAN_EXIT_CONFIRM_MESSAGE,
    CLAN_EXIT_MESSAGE,
    CLAN_LIST_MESSAGE,
    CLAN_NAME_CONFIRM_MESSAGE,
    CLAN_NAME_NOT_CORRECT_MESSAGE,
    CLAN_SEARCH_AMOUNT_MESSAGE,
    CLAN_SEARCH_MESSAGE,
    CLAN_TAKEN_MESSAGE,
    CREATE_PREVIEW_MESSAGE,
    CREATE_REQUEST_CONFIRM_MESSAGE,
    ERROR_CREATING_CLAN_MESSAGE,
    MEMBERS_LIST_MESSAGE,
    NO_CLAN_MESSAGE,
    REQUEST_LIST_MESSAGE,
    SEARCH_CLAN_LIST_MESSAGE,
    SUCCESS_CREATING_CLAN_MESSAGE,
)
from bot.clan.utils import (
    accept_request,
    check_clan_name_correct,
    check_clan_name_exist,
    create_request,
    decline_request,
    enter_clan,
    get_clan_info,
)
from bot.command.buttons import CLAN_BUTTON
from bot.command.keyboards import start_keyboard, user_created_keyboard
from bot.command.messages import NOT_CREATED_CHARACTER_MESSAGE
from bot.constants.actions import clan_action
from bot.constants.callback_data import ClanData
from bot.constants.states import ClanState
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

clan_router = Router()


@clan_router.message(F.text == CLAN_BUTTON)
@log_in_dev
async def clan_preview_handler(message: types.Message, state: FSMContext):
    """Хендлер меню Клана."""
    await state.clear()
    user = await get_user(message.from_user.id)
    if not user.character:
        inline_keyboard = await user_created_keyboard()
        await message.answer(
            text=NOT_CREATED_CHARACTER_MESSAGE,
            reply_markup=inline_keyboard.as_markup(),
        )
        return
    if not user.character.clan:
        keyboard = await no_clan_preview_keyboard()
        await message.answer(
            text=NO_CLAN_MESSAGE,
            reply_markup=keyboard.as_markup(),
        )
        return
    keyboard = await clan_get_keyboard(user.character)
    await message.answer(
        text=await get_clan_info(user.character.clan),
        reply_markup=keyboard.as_markup(),
    )


@clan_router.callback_query(ClanData.filter(F.action == clan_action.preview))
@log_in_dev
async def clan_preview_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек меню Клана."""
    await state.clear()
    user = await get_user(callback.from_user.id)
    if not user.character:
        inline_keyboard = await user_created_keyboard()
        await callback.message.edit_text(
            text=NOT_CREATED_CHARACTER_MESSAGE,
            reply_markup=inline_keyboard.as_markup(),
        )
        return
    if not user.character.clan:
        keyboard = await no_clan_preview_keyboard()
        await callback.message.edit_text(
            text=NO_CLAN_MESSAGE,
            reply_markup=keyboard.as_markup(),
        )
        return
    keyboard = await clan_get_keyboard(user.character)
    await callback.message.edit_text(
        text=await get_clan_info(user.character.clan),
        reply_markup=keyboard.as_markup(),
    )


@clan_router.callback_query(
    ClanData.filter(F.action == clan_action.create_preview)
)
@log_in_dev
async def clan_create_preview_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек меню Клана."""
    keyboard = await to_preview_keyboard()
    await callback.message.edit_text(
        text=CREATE_PREVIEW_MESSAGE, reply_markup=keyboard.as_markup()
    )
    await state.set_state(ClanState.enter_name)


@clan_router.message(ClanState.enter_name)
@log_in_dev
async def check_clan_name_handler(message: types.Message, state: FSMContext):
    """Хендлер ввода названия Клана."""
    name = message.text
    if await check_clan_name_exist(name):
        await message.answer(text=CLAN_TAKEN_MESSAGE)
        await state.set_state(ClanState.enter_name)
        return
    if not check_clan_name_correct(name):
        await message.answer(text=CLAN_NAME_NOT_CORRECT_MESSAGE)
        await state.set_state(ClanState.enter_name)
        return
    await state.update_data(name=name)
    keyboard = await confirm_clan_name_keyboard()
    await message.answer(
        text=CLAN_NAME_CONFIRM_MESSAGE.format(name),
        reply_markup=keyboard.as_markup(),
    )


@clan_router.callback_query(ClanData.filter(F.action == clan_action.create))
@log_in_dev
async def create_clan_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Хендлер создания Клана."""
    data = await state.get_data()
    await state.clear()
    user = await get_user(callback.from_user.id)
    if "name" not in data:
        await callback.message.edit_text(
            text=ERROR_CREATING_CLAN_MESSAGE,
        )
        return
    name = data["name"]
    clan = await Clan.objects.acreate(name=name, leader=user.character)
    user.character.clan = clan
    await user.character.asave(update_fields=("clan",))
    keyboard = await start_keyboard()
    await callback.message.answer(
        text=SUCCESS_CREATING_CLAN_MESSAGE,
        reply_markup=keyboard.as_markup(resize_keyboard=True),
    )
    callback_data.id = clan.id
    keyboard = await clan_get_keyboard(user.character)
    await callback.message.edit_text(
        text=await get_clan_info(clan),
        reply_markup=keyboard.as_markup(),
    )


@clan_router.callback_query(ClanData.filter(F.action == clan_action.list))
@log_in_dev
async def clan_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Хендлер списка Кланов."""
    paginator = await clan_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=CLAN_LIST_MESSAGE, reply_markup=paginator
    )


@clan_router.callback_query(
    ClanData.filter(F.action == clan_action.search_clan)
)
@log_in_dev
async def clan_search_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Хендлер поиска Кланов."""
    keyboard = await to_preview_keyboard()
    await callback.message.edit_text(
        text=CLAN_SEARCH_MESSAGE, reply_markup=keyboard.as_markup()
    )
    await state.set_state(ClanState.clan_search)


@clan_router.message(ClanState.clan_search)
@log_in_dev
async def clan_search_state(message: types.Message, state: FSMContext):
    """Хендлер обработки поиска клана."""
    name_contains = message.text
    items_amount = await Clan.objects.filter(
        name__contains=name_contains,
    ).acount()
    keyboard = await clan_search_keyboard(name_contains)
    await message.answer(
        text=CLAN_SEARCH_AMOUNT_MESSAGE.format(items_amount, name_contains),
        reply_markup=keyboard.as_markup(),
    )


@clan_router.callback_query(
    ClanData.filter(F.action == clan_action.search_list)
)
@log_in_dev
async def search_clan_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    await state.clear()
    paginator = await search_clan_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=SEARCH_CLAN_LIST_MESSAGE, reply_markup=paginator
    )


@clan_router.callback_query(ClanData.filter(F.action == clan_action.get))
@log_in_dev
async def clan_guest_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    clan = await Clan.objects.select_related(
        "leader", "leader__character_class"
    ).aget(pk=callback_data.id)
    keyboard = await clan_guest_get_keyboard(clan)
    await callback.message.edit_text(
        text=await get_clan_info(clan), reply_markup=keyboard.as_markup()
    )


@clan_router.callback_query(
    ClanData.filter(F.action == clan_action.create_request_confirm)
)
@log_in_dev
async def clan_create_request_confirm_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    keyboard = await clan_create_request_confirm_keyboard(callback_data)
    await callback.message.edit_text(
        text=CREATE_REQUEST_CONFIRM_MESSAGE, reply_markup=keyboard.as_markup()
    )


@clan_router.callback_query(
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
    keyboard = await clan_create_request_keyboard(callback_data)
    await callback.message.edit_text(
        text=text, reply_markup=keyboard.as_markup()
    )


@clan_router.callback_query(
    ClanData.filter(F.action == clan_action.request_list)
)
@log_in_dev
async def clan_request_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    paginator = await clan_request_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=REQUEST_LIST_MESSAGE, reply_markup=paginator
    )


@clan_router.callback_query(
    ClanData.filter(F.action == clan_action.request_get)
)
@log_in_dev
async def clan_request_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    character = await Character.objects.select_related("character_class").aget(
        pk=callback_data.character_id
    )
    keyboard = await clan_request_get_keyboard(callback_data)
    await callback.message.edit_text(
        text=await get_character_about(character),
        reply_markup=keyboard.as_markup(),
    )


@clan_router.callback_query(
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
    paginator = await clan_request_list_keyboard(callback_data)
    await callback.message.answer(
        text=REQUEST_LIST_MESSAGE, reply_markup=paginator
    )


@clan_router.callback_query(
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
    paginator = await clan_request_list_keyboard(callback_data)
    await callback.message.answer(
        text=REQUEST_LIST_MESSAGE, reply_markup=paginator
    )


@clan_router.callback_query(
    ClanData.filter(F.action == clan_action.enter_clan_confirm)
)
@log_in_dev
async def clan_enter_confirm_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    keyboard = await clan_enter_confirm_keyboard(callback_data)
    await callback.message.edit_text(
        text=CLAN_ENTER_CONFIRM_MESSAGE, reply_markup=keyboard.as_markup()
    )


@clan_router.callback_query(
    ClanData.filter(F.action == clan_action.enter_clan)
)
@log_in_dev
async def clan_enter_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    user = await get_user(callback.from_user.id)
    clan = await Clan.objects.aget(id=callback_data.id)
    success, text = await enter_clan(user.character, clan)
    await callback.message.edit_text(text=text)


@clan_router.callback_query(
    ClanData.filter(F.action == clan_action.exit_confirm)
)
@log_in_dev
async def clan_exit_confirm_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    keyboard = await clan_exit_confirm_keyboard(callback_data)
    await callback.message.edit_text(
        text=CLAN_EXIT_CONFIRM_MESSAGE, reply_markup=keyboard.as_markup()
    )


@clan_router.callback_query(ClanData.filter(F.action == clan_action.exit))
@log_in_dev
async def clan_exit_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanData,
):
    """Коллбек получения предмета в инвентаре."""
    user = await get_user(callback.from_user.id)
    user.character.clan = None
    await user.character.asave(update_fields=("clan",))
    await callback.message.edit_text(text=CLAN_EXIT_MESSAGE)


@clan_router.callback_query(ClanData.filter(F.action == clan_action.members))
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
