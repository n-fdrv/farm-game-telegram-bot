from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from game.models import CharacterItem

from bot.constants.actions import backpack_action
from bot.constants.callback_data import BackpackData
from bot.constants.messages import backpack_messages
from bot.keyboards import backpack_keyboards
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

router = Router()


@router.callback_query(BackpackData.filter(F.action == backpack_action.list))
@log_in_dev
async def backpack_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: BackpackData,
):
    """Коллбек получения инвентаря."""
    user = await get_user(callback.from_user.id)
    paginator = await backpack_keyboards.backpack_list(user, callback_data)
    await callback.message.edit_text(
        text=backpack_messages.ITEM_LIST_MESSAGE, reply_markup=paginator
    )


@router.callback_query(BackpackData.filter(F.action == backpack_action.get))
@log_in_dev
async def backpack_get(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: BackpackData,
):
    """Коллбек получения предмета в инвентаре."""
    # TODO Изображение всех предметов
    # TODO 🔴🟠🟡🟢🔵🟣⚫️⚪️🟤 Ранги предметов
    keyboard = await backpack_keyboards.item_get(callback_data)
    character_item = await CharacterItem.objects.select_related("item").aget(
        id=callback_data.id
    )
    await callback.message.edit_text(
        text=backpack_messages.ITEM_GET_MESSAGE.format(
            character_item.item.name,
            character_item.amount,
            character_item.item.description,
            character_item.item.sell_price,
            character_item.item.buy_price,
        ),
        reply_markup=keyboard.as_markup(),
    )
