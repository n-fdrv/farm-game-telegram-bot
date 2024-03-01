from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import CharacterItem

from bot.backpack.keyboards import (
    backpack_list_keyboard,
    backpack_preview_keyboard,
    item_get_keyboard,
)
from bot.backpack.messages import (
    ITEM_LIST_MESSAGE,
    ITEM_PREVIEW_MESSAGE,
)
from bot.backpack.utils import equip_item, get_character_item_info_text
from bot.constants.actions import backpack_action
from bot.constants.callback_data import BackpackData
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

backpack_router = Router()


@backpack_router.callback_query(
    BackpackData.filter(F.action == backpack_action.preview)
)
@log_in_dev
async def backpack_preview(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: BackpackData,
):
    """Коллбек получения инвентаря."""
    user = await get_user(callback.from_user.id)
    gold = await CharacterItem.objects.aget(
        character=user.character, item__name="Золото"
    )
    keyboard = await backpack_preview_keyboard()
    await callback.message.edit_text(
        text=ITEM_PREVIEW_MESSAGE.format(gold.amount),
        reply_markup=keyboard.as_markup(),
    )


@backpack_router.callback_query(
    BackpackData.filter(F.action == backpack_action.list)
)
@log_in_dev
async def backpack_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: BackpackData,
):
    """Коллбек получения инвентаря."""
    user = await get_user(callback.from_user.id)
    paginator = await backpack_list_keyboard(user, callback_data)
    await callback.message.edit_text(
        text=ITEM_LIST_MESSAGE, reply_markup=paginator
    )


@backpack_router.callback_query(
    BackpackData.filter(F.action == backpack_action.get)
)
@log_in_dev
async def backpack_get(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: BackpackData,
):
    """Коллбек получения предмета в инвентаре."""
    # TODO Изображение всех предметов
    keyboard = await item_get_keyboard(callback_data)
    character_item = await CharacterItem.objects.select_related("item").aget(
        id=callback_data.id
    )
    await callback.message.edit_text(
        text=await get_character_item_info_text(character_item),
        reply_markup=keyboard.as_markup(),
    )


@backpack_router.callback_query(
    BackpackData.filter(F.action == backpack_action.equip)
)
@log_in_dev
async def backpack_equip_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: BackpackData,
):
    """Коллбек надевания/снятия предмета."""
    character_item = await CharacterItem.objects.select_related(
        "character", "item"
    ).aget(id=callback_data.id)
    await equip_item(character_item)
    keyboard = await item_get_keyboard(callback_data)
    character_item = await CharacterItem.objects.select_related("item").aget(
        id=callback_data.id
    )
    await callback.message.edit_text(
        text=await get_character_item_info_text(character_item),
        reply_markup=keyboard.as_markup(),
    )
