from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import CharacterItem

from bot.command.buttons import MARKET_BUTTON
from bot.constants.actions import marketplace_action
from bot.constants.callback_data import MarketplaceData
from bot.constants.states import MarketplaceState
from bot.marketplace.keyboards import (
    add_preview_keyboard,
    marketplace_preview_keyboard,
    sell_confirm_keyboard,
    sell_get_keyboard,
    sell_list_keyboard,
    sell_preview_keyboard,
    to_sell_preview_keyboard,
)
from bot.marketplace.messages import (
    ADD_PREVIEW_MESSAGE,
    ADD_PRICE_MESSAGE,
    CONFIRM_LOT_MESSAGE,
    CORRECT_PRICE_MESSAGE,
    MARKETPLACE_PREVIEW_MESSAGE,
    NO_CHARACTER_MESSAGE,
    NOT_CORRECT_PRICE_MESSAGE,
    NOT_SUCCESS_LOT_MESSAGE,
    SELL_LIST_MESSAGE,
    SELL_PREVIEW_MESSAGE,
    SUCCESS_LOT_MESSAGE,
)
from bot.marketplace.utils import (
    add_item_on_marketplace,
    get_character_item_marketplace_text,
)
from bot.shop.messages import NOT_CORRECT_AMOUNT_MESSAGE
from bot.shop.utils import check_correct_amount
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

marketplace_router = Router()


@marketplace_router.message(F.text == MARKET_BUTTON)
@log_in_dev
async def marketplace_preview_handler(
    message: types.Message, state: FSMContext
):
    """Хендлер получения торговой площадки."""
    await state.clear()
    user = await get_user(message.from_user.id)
    if not user.character:
        await message.answer(text=NO_CHARACTER_MESSAGE)
        return
    keyboard = await marketplace_preview_keyboard()
    await message.answer(
        text=MARKETPLACE_PREVIEW_MESSAGE, reply_markup=keyboard.as_markup()
    )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.preview)
)
@log_in_dev
async def marketplace_preview_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения персонажа."""
    await state.clear()
    user = await get_user(callback.from_user.id)
    if not user.character:
        await callback.message.edit_text(text=NO_CHARACTER_MESSAGE)
        return
    keyboard = await marketplace_preview_keyboard()
    await callback.message.edit_text(
        text=MARKETPLACE_PREVIEW_MESSAGE, reply_markup=keyboard.as_markup()
    )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.sell_preview)
)
@log_in_dev
async def marketplace_sell_preview_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения персонажа."""
    await state.clear()
    user = await get_user(callback.from_user.id)
    keyboard = await sell_preview_keyboard(user.character)
    await callback.message.edit_text(
        text=SELL_PREVIEW_MESSAGE, reply_markup=keyboard.as_markup()
    )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.sell_list)
)
@log_in_dev
async def marketplace_sell_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения персонажа."""
    await state.clear()
    user = await get_user(callback.from_user.id)
    paginator = await sell_list_keyboard(user, callback_data)
    await callback.message.edit_text(
        text=SELL_LIST_MESSAGE, reply_markup=paginator
    )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.sell_get)
)
@log_in_dev
async def sell_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения предмета в инвентаре."""
    await state.clear()
    keyboard = await sell_get_keyboard(callback_data)
    character_item = await CharacterItem.objects.select_related("item").aget(
        id=callback_data.id
    )
    await callback.message.edit_text(
        text=await get_character_item_marketplace_text(character_item),
        reply_markup=keyboard.as_markup(),
    )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.add_preview)
)
@log_in_dev
async def add_preview_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения предмета в инвентаре."""
    await state.clear()
    keyboard = await add_preview_keyboard()
    await callback.message.edit_text(
        text=ADD_PREVIEW_MESSAGE,
        reply_markup=keyboard.as_markup(),
    )
    await state.update_data(character_item_id=callback_data.id)


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.choose_currency)
)
@log_in_dev
async def choose_currency_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения предмета в инвентаре."""
    keyboard = await to_sell_preview_keyboard()
    await callback.message.edit_text(
        text=ADD_PRICE_MESSAGE,
        reply_markup=keyboard.as_markup(),
    )
    await state.update_data(currency=callback_data.currency)
    await state.set_state(MarketplaceState.item_price)


@marketplace_router.message(MarketplaceState.item_price)
@log_in_dev
async def marketplace_price_state(message: types.Message, state: FSMContext):
    """Хендлер обработки количества товаров."""
    price = message.text
    is_correct = await check_correct_amount(price)
    keyboard = await to_sell_preview_keyboard()
    if not is_correct:
        await message.answer(
            text=NOT_CORRECT_PRICE_MESSAGE, reply_markup=keyboard.as_markup()
        )
        await state.set_state(MarketplaceState.item_price)
        return
    await state.update_data(price=price)
    await state.set_state(MarketplaceState.item_amount)
    await message.answer(
        text=CORRECT_PRICE_MESSAGE, reply_markup=keyboard.as_markup()
    )


@marketplace_router.message(MarketplaceState.item_amount)
@log_in_dev
async def marketplace_sell_amount_state(
    message: types.Message, state: FSMContext
):
    """Хендлер обработки количества товаров."""
    amount = message.text
    is_correct = await check_correct_amount(amount)
    keyboard = await to_sell_preview_keyboard()
    if not is_correct:
        await message.answer(
            text=NOT_CORRECT_AMOUNT_MESSAGE, reply_markup=keyboard.as_markup()
        )
        await state.set_state(MarketplaceState.item_amount)
    amount = int(amount)

    data = await state.get_data()
    character_item = await CharacterItem.objects.select_related("item").aget(
        pk=data["character_item_id"]
    )
    if character_item.amount < amount:
        amount = character_item.amount
    keyboard = await sell_confirm_keyboard()
    await state.update_data(amount=amount)
    await message.answer(
        CONFIRM_LOT_MESSAGE.format(
            character_item.name_with_enhance,
            amount,
            data["price"],
            data["currency"],
        ),
        reply_markup=keyboard.as_markup(),
    )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.add)
)
@log_in_dev
async def add_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения предмета в инвентаре."""
    data = await state.get_data()
    if ("character_item_id", "amount", "currency", "price") - data.keys():
        await callback.message.edit_text(text=NOT_SUCCESS_LOT_MESSAGE)
        return
    keyboard = await marketplace_preview_keyboard()
    character_item = await CharacterItem.objects.select_related(
        "character", "item"
    ).aget(pk=data["character_item_id"])
    await add_item_on_marketplace(
        character_item, data["price"], data["amount"], data["currency"]
    )
    await callback.message.edit_text(
        text=SUCCESS_LOT_MESSAGE,
        reply_markup=keyboard.as_markup(),
    )
