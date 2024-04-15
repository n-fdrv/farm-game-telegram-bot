from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import CharacterItem
from item.models import Item

from bot.character.shop.keyboards import (
    buy_get_keyboard,
    buy_keyboard,
    buy_list_keyboard,
    buy_preview_keyboard,
    in_sell_keyboard,
    in_shop_keyboard,
    sell_amount_confirm_keyboard,
    sell_get_keyboard,
    sell_keyboard,
    sell_list_keyboard,
    sell_preview_keyboard,
    shop_get_keyboard,
)
from bot.character.shop.messages import (
    CONFIRM_AMOUNT_MESSAGE,
    LIST_MESSAGE,
    PREVIEW_MESSAGE,
    SELL_AMOUNT_MESSAGE,
    SHOP_GET_MESSAGE,
)
from bot.character.shop.utils import (
    buy_item,
    sell_item,
)
from bot.constants.actions import shop_action
from bot.constants.callback_data import ShopData
from bot.constants.states import ShopState
from bot.utils.game_utils import check_correct_amount, get_item_info_text
from bot.utils.messages import NOT_CORRECT_AMOUNT_MESSAGE
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

shop_router = Router()


@shop_router.callback_query(ShopData.filter(F.action == shop_action.get))
@log_in_dev
async def shop_get(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Коллбек перехода в магазин."""
    user = await get_user(callback.from_user.id)
    if user.character.current_location:
        await callback.message.delete()
        return
    keyboard = await shop_get_keyboard()
    await callback.message.edit_text(
        text=SHOP_GET_MESSAGE, reply_markup=keyboard.as_markup()
    )


@shop_router.callback_query(
    ShopData.filter(F.action == shop_action.buy_preview)
)
@log_in_dev
async def shop_buy_preview(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Коллбек перехода в магазин."""
    user = await get_user(callback.from_user.id)
    if user.character.current_location:
        await callback.message.delete()
        return
    keyboard = await buy_preview_keyboard()
    await callback.message.edit_text(
        text=PREVIEW_MESSAGE, reply_markup=keyboard.as_markup()
    )


@shop_router.callback_query(ShopData.filter(F.action == shop_action.buy_list))
@log_in_dev
async def shop_buy_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Коллбек перехода в список товаров для покупки."""
    user = await get_user(callback.from_user.id)
    if user.character.current_location:
        await callback.message.delete()
        return
    paginator = await buy_list_keyboard(callback_data)
    await callback.message.edit_text(text=LIST_MESSAGE, reply_markup=paginator)


@shop_router.callback_query(ShopData.filter(F.action == shop_action.buy_get))
@log_in_dev
async def shop_buy_get_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Хендлер товара для покупки."""
    user = await get_user(callback.from_user.id)
    if user.character.current_location:
        await callback.message.delete()
        return
    item = await Item.objects.aget(pk=callback_data.id)
    keyboard = await buy_get_keyboard(callback_data)
    await callback.message.edit_text(
        text=await get_item_info_text(item),
        reply_markup=keyboard.as_markup(),
    )


@shop_router.callback_query(ShopData.filter(F.action == shop_action.buy))
@log_in_dev
async def shop_buy_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Хендлер покупки товара."""
    user = await get_user(callback.from_user.id)
    if user.character.current_location:
        await callback.message.delete()
        return
    item = await Item.objects.aget(pk=callback_data.id)
    keyboard = await buy_keyboard(callback_data)
    success, text = await buy_item(user.character, item)
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup(),
    )


@shop_router.callback_query(
    ShopData.filter(F.action == shop_action.sell_preview)
)
@log_in_dev
async def shop_sell_preview(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Коллбек перехода в превью продаж."""
    user = await get_user(callback.from_user.id)
    if user.character.current_location:
        await callback.message.delete()
        return
    keyboard = await sell_preview_keyboard(user.character)
    await callback.message.edit_text(
        text=PREVIEW_MESSAGE, reply_markup=keyboard.as_markup()
    )


@shop_router.callback_query(ShopData.filter(F.action == shop_action.sell_list))
@log_in_dev
async def shop_sell_list(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Коллбек перехода в продажи."""
    user = await get_user(callback.from_user.id)
    if user.character.current_location:
        await callback.message.delete()
        return
    paginator = await sell_list_keyboard(user, callback_data)
    await callback.message.edit_text(text=LIST_MESSAGE, reply_markup=paginator)


@shop_router.callback_query(ShopData.filter(F.action == shop_action.sell_get))
@log_in_dev
async def shop_sell_get_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Хендлер товара для продажи."""
    user = await get_user(callback.from_user.id)
    if user.character.current_location:
        await callback.message.delete()
        return
    character_item = await CharacterItem.objects.select_related("item").aget(
        pk=callback_data.id
    )
    callback_data.amount = character_item.amount
    keyboard = await sell_get_keyboard(callback_data)
    await callback.message.edit_text(
        text=await get_item_info_text(character_item),
        reply_markup=keyboard.as_markup(),
    )


@shop_router.callback_query(
    ShopData.filter(F.action == shop_action.sell_amount)
)
@log_in_dev
async def shop_sell_amount_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Хендлер ввода количества товаров."""
    user = await get_user(callback.from_user.id)
    if user.character.current_location:
        await callback.message.delete()
        return
    keyboard = await sell_keyboard(callback_data)
    await callback.message.edit_text(
        text=SELL_AMOUNT_MESSAGE, reply_markup=keyboard.as_markup()
    )
    await state.update_data(character_item_id=callback_data.id)
    await state.set_state(ShopState.item_amount)


@shop_router.message(ShopState.item_amount)
@log_in_dev
async def shop_sell_amount_state(message: types.Message, state: FSMContext):
    """Хендлер обработки количества товаров."""
    user = await get_user(message.from_user.id)
    if user.character.current_location:
        await message.message.delete()
        return
    amount = message.text
    is_correct = await check_correct_amount(amount)
    keyboard = await in_shop_keyboard()
    if not is_correct:
        await message.answer(
            text=NOT_CORRECT_AMOUNT_MESSAGE, reply_markup=keyboard.as_markup()
        )
        await state.set_state(ShopState.item_amount)
        return
    data = await state.get_data()
    item = await CharacterItem.objects.select_related("item").aget(
        pk=data["character_item_id"]
    )
    keyboard = await sell_amount_confirm_keyboard(item.id, int(amount))
    await message.answer(
        text=CONFIRM_AMOUNT_MESSAGE.format(item.name_with_enhance, amount),
        reply_markup=keyboard.as_markup(),
    )


@shop_router.callback_query(ShopData.filter(F.action == shop_action.sell))
@log_in_dev
async def shop_sell_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ShopData,
):
    """Хендлер продажи товара."""
    await state.clear()

    character_item = await CharacterItem.objects.select_related(
        "item", "character", "character__current_location"
    ).aget(pk=callback_data.id)
    keyboard = await in_sell_keyboard(character_item.item.type)
    success, text = await sell_item(character_item, callback_data.amount)
    await callback.message.edit_text(
        text=text, reply_markup=keyboard.as_markup()
    )
