from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from item.models import Recipe

from bot.constants.actions import craft_action
from bot.constants.callback_data import CraftData
from bot.craft.keyboards import (
    craft_create_keyboard,
    craft_get_keyboard,
    craft_list_keyboard,
)
from bot.craft.messages import (
    CRAFTING_LIST_MESSAGE,
    NOT_ENOUGH_ITEMS_MESSAGE,
    NOT_SUCCESS_CRAFT_MESSAGE,
    SUCCESS_CRAFT_MESSAGE,
)
from bot.craft.utils import (
    check_crafting_items,
    craft_item,
    get_crafting_item_text,
)
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

craft_router = Router()


@craft_router.callback_query(CraftData.filter(F.action == craft_action.list))
@log_in_dev
async def craft_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CraftData,
):
    """Коллбек получения списка создания."""
    user = await get_user(callback.from_user.id)
    keyboard = await craft_list_keyboard(user.character)
    await callback.message.edit_text(
        text=CRAFTING_LIST_MESSAGE, reply_markup=keyboard.as_markup()
    )


@craft_router.callback_query(CraftData.filter(F.action == craft_action.get))
@log_in_dev
async def craft_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CraftData,
):
    """Коллбек получения предмета создания."""
    recipe = await Recipe.objects.select_related("create").aget(
        id=callback_data.id
    )
    keyboard = await craft_get_keyboard(recipe)
    await callback.message.edit_text(
        text=await get_crafting_item_text(recipe),
        reply_markup=keyboard.as_markup(),
    )


@craft_router.callback_query(CraftData.filter(F.action == craft_action.create))
@log_in_dev
async def craft_create_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CraftData,
):
    """Коллбек создания предмета."""
    user = await get_user(callback.from_user.id)
    recipe = await Recipe.objects.select_related("create").aget(
        id=callback_data.id
    )
    enough_items = await check_crafting_items(user.character, recipe)
    keyboard = await craft_create_keyboard(callback_data)
    if not enough_items:
        await callback.message.edit_text(
            text=NOT_ENOUGH_ITEMS_MESSAGE, reply_markup=keyboard.as_markup()
        )
        return
    success = await craft_item(user.character, recipe)
    if success:
        await callback.message.edit_text(
            text=SUCCESS_CRAFT_MESSAGE.format(recipe.create.name_with_grade),
            reply_markup=keyboard.as_markup(),
        )
        return
    await callback.message.edit_text(
        text=NOT_SUCCESS_CRAFT_MESSAGE.format(recipe.create.name_with_grade),
        reply_markup=keyboard.as_markup(),
    )
