from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import Character
from clan.models import ClanWarehouse

from bot.clan.warehouse.keyboards import (
    clan_warehouse_get_keyboard,
    clan_warehouse_list_keyboard,
    clan_warehouse_look_keyboard,
    clan_warehouse_send_list_keyboard,
    enter_amount_keyboard,
    enter_confirm_keyboard,
    not_correct_amount_keyboard,
    send_item_keyboard,
)
from bot.clan.warehouse.messages import (
    ENTER_AMOUNT_MESSAGE,
    LOOK_WAREHOUSE_MESSAGE,
    SEND_CONFIRM_MESSAGE,
    SEND_LIST_MESSAGE,
)
from bot.clan.warehouse.utils import send_item_from_warehouse
from bot.constants.actions import clan_warehouse_action
from bot.constants.callback_data import ClanWarehouseData
from bot.constants.states import ClanState
from bot.utils.game_utils import check_correct_amount, get_item_info_text
from bot.utils.messages import NOT_CORRECT_AMOUNT_MESSAGE
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

clan_warehouse_router = Router()


@clan_warehouse_router.callback_query(
    ClanWarehouseData.filter(F.action == clan_warehouse_action.look)
)
@log_in_dev
async def clan_warehouse_look_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanWarehouseData,
):
    """Коллбек просмотра хранилища."""
    keyboard = await clan_warehouse_look_keyboard(callback_data)
    await callback.message.edit_text(
        text=LOOK_WAREHOUSE_MESSAGE,
        reply_markup=keyboard.as_markup(),
    )


@clan_warehouse_router.callback_query(
    ClanWarehouseData.filter(F.action == clan_warehouse_action.list)
)
@log_in_dev
async def clan_warehouse_list_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanWarehouseData,
):
    """Коллбек просмотра типа предметов в хранилище."""
    paginator = await clan_warehouse_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=LOOK_WAREHOUSE_MESSAGE,
        reply_markup=paginator,
    )


@clan_warehouse_router.callback_query(
    ClanWarehouseData.filter(F.action == clan_warehouse_action.get)
)
@log_in_dev
async def clan_warehouse_get_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanWarehouseData,
):
    """Коллбек просмотра предмета в хранилище."""
    user = await get_user(callback.from_user.id)
    keyboard = await clan_warehouse_get_keyboard(user.character, callback_data)
    item = await ClanWarehouse.objects.select_related("item").aget(
        pk=callback_data.item_id
    )
    await callback.message.edit_text(
        text=await get_item_info_text(item),
        reply_markup=keyboard.as_markup(),
    )


@clan_warehouse_router.callback_query(
    ClanWarehouseData.filter(F.action == clan_warehouse_action.send_list)
)
@log_in_dev
async def clan_warehouse_send_list_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanWarehouseData,
):
    """Коллбек выбора персонажа для отправки предмета."""
    await state.clear()
    paginator = await clan_warehouse_send_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=SEND_LIST_MESSAGE,
        reply_markup=paginator,
    )


@clan_warehouse_router.callback_query(
    ClanWarehouseData.filter(F.action == clan_warehouse_action.send_amount)
)
@log_in_dev
async def clan_warehouse_send_amount_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanWarehouseData,
):
    """Коллбек ввода количества предметов."""
    item = await ClanWarehouse.objects.select_related("item").aget(
        pk=callback_data.item_id
    )
    character = await Character.objects.select_related("character_class").aget(
        pk=callback_data.character_id
    )
    if callback_data.amount > 1:
        keyboard = await enter_amount_keyboard(callback_data)
        await callback.message.edit_text(
            text=ENTER_AMOUNT_MESSAGE.format(
                item.name_with_enhance, character.name_with_class, item.amount
            ),
            reply_markup=keyboard.as_markup(),
        )
        await state.update_data(
            action=callback_data.action,
            id=callback_data.id,
            item_id=callback_data.item_id,
            character_id=callback_data.character_id,
            type=callback_data.type,
            page=callback_data.page,
            amount=callback_data.amount,
        )
        await state.set_state(ClanState.send_amount)
        return
    keyboard = await enter_confirm_keyboard(callback_data)
    await callback.message.edit_text(
        text=SEND_CONFIRM_MESSAGE.format(
            item.name_with_enhance, item.amount, character.name_with_class
        ),
        reply_markup=keyboard.as_markup(),
    )


@clan_warehouse_router.message(ClanState.send_amount)
@log_in_dev
async def send_item_amount_enter_handler(
    message: types.Message, state: FSMContext
):
    """Хендлер ввода количества."""
    amount = message.text
    data = await state.get_data()
    is_correct = await check_correct_amount(amount)
    callback_data = ClanWarehouseData(
        action=data["action"],
        id=data["id"],
        item_id=data["item_id"],
        character_id=data["character_id"],
        type=data["type"],
        page=data["page"],
        amount=data["amount"],
    )
    if not is_correct:
        keyboard = await not_correct_amount_keyboard(callback_data)
        await message.answer(
            text=NOT_CORRECT_AMOUNT_MESSAGE, reply_markup=keyboard.as_markup()
        )
        await state.set_state(ClanState.send_amount)
        return
    callback_data.amount = amount
    item = await ClanWarehouse.objects.select_related("item").aget(
        pk=callback_data.item_id
    )
    character = await Character.objects.select_related("character_class").aget(
        pk=callback_data.character_id
    )
    keyboard = await enter_confirm_keyboard(callback_data)
    await message.answer(
        text=SEND_CONFIRM_MESSAGE.format(
            item.name_with_enhance, amount, character.name_with_class
        ),
        reply_markup=keyboard.as_markup(),
    )


@clan_warehouse_router.callback_query(
    ClanWarehouseData.filter(F.action == clan_warehouse_action.send)
)
@log_in_dev
async def clan_warehouse_send_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ClanWarehouseData,
):
    """Коллбек отправки предмета персонажу."""
    item = await ClanWarehouse.objects.select_related("item").aget(
        pk=callback_data.item_id
    )
    character = await Character.objects.select_related("character_class").aget(
        pk=callback_data.character_id
    )
    success, text = await send_item_from_warehouse(
        item, character, callback.bot, callback_data.amount
    )
    keyboard = await send_item_keyboard(callback_data)
    await callback.message.edit_text(
        text=text, reply_markup=keyboard.as_markup()
    )
