from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from item.models import Item

from bot.constants.actions import craft_action
from bot.constants.callback_data import CraftData
from bot.craft.keyboards import craft_get_keyboard, craft_list_keyboard
from bot.craft.messages import CRAFTING_LIST_MESSAGE
from bot.craft.utils import get_crafting_item_text
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
    craft_skill = await user.character.skills.aget(name="Мастер Создания")
    keyboard = await craft_list_keyboard(craft_skill)
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
    item = await Item.objects.aget(id=callback_data.id)
    keyboard = await craft_get_keyboard(item)
    await callback.message.edit_text(
        text=await get_crafting_item_text(item),
        reply_markup=keyboard.as_markup(),
    )
