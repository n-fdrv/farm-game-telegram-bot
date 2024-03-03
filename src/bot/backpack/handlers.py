from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import CharacterItem

from bot.backpack.keyboards import (
    backpack_list_keyboard,
    backpack_preview_keyboard,
    item_get_keyboard,
    not_success_equip_keyboard,
    use_potion_keyboard,
)
from bot.backpack.messages import (
    ITEM_LIST_MESSAGE,
    ITEM_PREVIEW_MESSAGE,
    NOT_SUCCESS_EQUIP_MESSAGE,
    SUCCESS_USE_POTION_MESSAGE,
)
from bot.backpack.utils import (
    equip_item,
    get_character_item_info_text,
    get_gold_amount,
    use_potion,
)
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
    gold = await get_gold_amount(user.character)
    keyboard = await backpack_preview_keyboard()
    await callback.message.edit_text(
        text=ITEM_PREVIEW_MESSAGE.format(gold),
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
        "character",
        "character__character_class",
        "item",
    ).aget(id=callback_data.id)
    success = await equip_item(character_item)
    if not success:
        keyboard = await not_success_equip_keyboard(callback_data)
        await callback.message.edit_text(
            text=NOT_SUCCESS_EQUIP_MESSAGE,
            reply_markup=keyboard.as_markup(),
        )
        return
    keyboard = await item_get_keyboard(callback_data)
    character_item = await CharacterItem.objects.select_related("item").aget(
        id=callback_data.id
    )
    await callback.message.edit_text(
        text=await get_character_item_info_text(character_item),
        reply_markup=keyboard.as_markup(),
    )


@backpack_router.callback_query(
    BackpackData.filter(F.action == backpack_action.use)
)
@log_in_dev
async def backpack_use_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: BackpackData,
):
    """Коллбек использования предмета."""
    character_item = await CharacterItem.objects.select_related(
        "character",
        "item",
    ).aget(id=callback_data.id)
    await use_potion(character_item.character, character_item.item)
    keyboard = await use_potion_keyboard()
    await callback.message.edit_text(
        text=SUCCESS_USE_POTION_MESSAGE.format(
            character_item.item.name_with_type
        ),
        reply_markup=keyboard.as_markup(),
    )
