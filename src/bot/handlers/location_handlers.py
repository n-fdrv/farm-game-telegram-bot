from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from game.models import Location
from game.utils.location import get_location_info

from bot.constants.actions import location_action
from bot.constants.callback_data import LocationData
from bot.constants.messages import location_messages
from bot.keyboards import location_keyboards
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

router = Router()


@router.callback_query(LocationData.filter(F.action == location_action.list))
@log_in_dev
async def location_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: LocationData,
):
    """Коллбек получения локаций."""
    paginator = await location_keyboards.location_list(callback_data)
    await callback.message.edit_text(
        text=location_messages.LOCATION_LIST_MESSAGE, reply_markup=paginator
    )


@router.callback_query(LocationData.filter(F.action == location_action.get))
@log_in_dev
async def location_get(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: LocationData,
):
    """Коллбек получения локации."""
    user = await get_user(callback.from_user.id)
    keyboard = await location_keyboards.location_get(callback_data)
    location = await Location.objects.aget(pk=callback_data.id)
    await callback.message.edit_text(
        text=await get_location_info(user.character, location),
        reply_markup=keyboard.as_markup(),
    )
