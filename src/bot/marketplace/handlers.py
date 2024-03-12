from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import CharacterItem, MarketplaceItem

from bot.command.buttons import MARKET_BUTTON
from bot.constants.actions import marketplace_action
from bot.constants.callback_data import MarketplaceData
from bot.constants.states import MarketplaceState
from bot.marketplace.keyboards import (
    add_preview_keyboard,
    buy_confirm_keyboard,
    buy_get_keyboard,
    buy_list_keyboard,
    buy_preview_keyboard,
    choose_buy_currency_keyboard,
    item_get_keyboard,
    item_search_keyboard,
    items_list_keyboard,
    lot_item_list_keyboard,
    marketplace_preview_keyboard,
    remove_preview_keyboard,
    sell_confirm_keyboard,
    sell_get_keyboard,
    sell_list_keyboard,
    sell_preview_keyboard,
    to_buy_preview_keyboard,
    to_sell_preview_keyboard,
)
from bot.marketplace.messages import (
    ADD_PREVIEW_MESSAGE,
    ADD_PRICE_MESSAGE,
    BUY_CONFIRM_MESSAGE,
    CHOOSE_BUY_CURRENCY_MESSAGE,
    CONFIRM_LOT_MESSAGE,
    CORRECT_PRICE_MESSAGE,
    ITEM_LIST_MESSAGE,
    ITEM_SEARCH_AMOUNT_MESSAGE,
    ITEM_SEARCH_MESSAGE,
    MARKETPLACE_PREVIEW_MESSAGE,
    NO_CHARACTER_MESSAGE,
    NO_MARKETPLACE_ITEM_MESSAGE,
    NOT_CORRECT_PRICE_MESSAGE,
    NOT_SUCCESS_LOT_MESSAGE,
    PREVIEW_MESSAGE,
    REMOVE_CONFIRM_MESSAGE,
    SEARCH_ITEM_LIST_MESSAGE,
    SELL_LIST_MESSAGE,
    SUCCESS_SELL_MESSAGE,
)
from bot.marketplace.utils import (
    add_item_on_marketplace,
    buy_item,
    get_character_item_marketplace_text,
    get_lot_text,
    get_marketplace_item,
    remove_lot,
)
from bot.models import User
from bot.shop.messages import NOT_CORRECT_AMOUNT_MESSAGE
from bot.shop.utils import check_correct_amount
from bot.utils.schedulers import send_message_to_user
from bot.utils.user_helpers import get_user
from core.config import game_config
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
        text=PREVIEW_MESSAGE, reply_markup=keyboard.as_markup()
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
        return
    amount = int(amount)
    data = await state.get_data()
    price = int(data["price"])
    price_with_tax = int(price - price / game_config.MARKETPLACE_TAX)
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
            price,
            data["currency"],
            price_with_tax,
            data["currency"],
            game_config.MARKETPLACE_TAX,
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
    success, text = await add_item_on_marketplace(
        character_item, data["price"], data["amount"], data["currency"]
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup(),
    )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.buy_currency)
)
@log_in_dev
async def marketplace_choose_buy_currency_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения персонажа."""
    await state.clear()
    keyboard = await choose_buy_currency_keyboard()
    await callback.message.edit_text(
        text=CHOOSE_BUY_CURRENCY_MESSAGE, reply_markup=keyboard.as_markup()
    )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.buy_preview)
)
@log_in_dev
async def marketplace_buy_preview_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения персонажа."""
    await state.clear()
    keyboard = await buy_preview_keyboard(callback_data)
    await callback.message.edit_text(
        text=PREVIEW_MESSAGE, reply_markup=keyboard.as_markup()
    )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.buy_list)
)
@log_in_dev
async def marketplace_buy_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения персонажа."""
    await state.clear()
    paginator = await buy_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=SELL_LIST_MESSAGE, reply_markup=paginator
    )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.buy_get)
)
@log_in_dev
async def buy_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения предмета в инвентаре."""
    await state.clear()
    keyboard = await buy_get_keyboard(callback_data)
    marketplace_item = await get_marketplace_item(callback_data.id)
    if not marketplace_item:
        await callback.message.edit_text(
            text=NO_MARKETPLACE_ITEM_MESSAGE, reply_markup=keyboard.as_markup()
        )
        return
    await callback.message.edit_text(
        text=await get_lot_text(marketplace_item),
        reply_markup=keyboard.as_markup(),
    )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.buy_confirm)
)
@log_in_dev
async def buy_confirm_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения предмета в инвентаре."""
    await state.clear()
    keyboard = await buy_confirm_keyboard(callback_data)
    marketplace_item = await get_marketplace_item(callback_data.id)
    if not marketplace_item:
        await callback.message.edit_text(
            text=NO_MARKETPLACE_ITEM_MESSAGE, reply_markup=keyboard.as_markup()
        )
        return
    await callback.message.edit_text(
        text=BUY_CONFIRM_MESSAGE.format(
            marketplace_item.name_with_enhance,
            marketplace_item.amount,
            f"{marketplace_item.price}{marketplace_item.sell_currency.emoji}",
        ),
        reply_markup=keyboard.as_markup(),
    )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.buy)
)
@log_in_dev
async def buy_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения предмета в инвентаре."""
    await state.clear()
    user = await get_user(callback.from_user.id)
    keyboard = await to_buy_preview_keyboard()
    marketplace_item = await get_marketplace_item(callback_data.id)
    if not marketplace_item:
        await callback.message.edit_text(
            text=NO_MARKETPLACE_ITEM_MESSAGE, reply_markup=keyboard.as_markup()
        )
        return
    success, text = await buy_item(marketplace_item, user.character)
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup(),
    )
    if success:
        price_after_tax = int(
            marketplace_item.price
            - marketplace_item.price / game_config.MARKETPLACE_TAX
        )
        seller = await User.objects.aget(character=marketplace_item.seller)
        await send_message_to_user(
            seller.telegram_id,
            SUCCESS_SELL_MESSAGE.format(
                marketplace_item.name_with_enhance,
                marketplace_item.amount,
                f"{price_after_tax}{marketplace_item.sell_currency.emoji}",
            ),
        )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.items_list)
)
@log_in_dev
async def items_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения предмета в инвентаре."""
    await state.clear()
    user = await get_user(callback.from_user.id)
    keyboard = await items_list_keyboard(user.character)
    lots_amount = await MarketplaceItem.objects.filter(
        seller=user.character
    ).acount()
    await callback.message.edit_text(
        text=ITEM_LIST_MESSAGE.format(lots_amount, game_config.MAX_LOT_AMOUNT),
        reply_markup=keyboard.as_markup(),
    )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.item_get)
)
@log_in_dev
async def item_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения предмета в инвентаре."""
    await state.clear()
    marketplace_item = await get_marketplace_item(callback_data.id)
    keyboard = await item_get_keyboard(callback_data)
    await callback.message.edit_text(
        text=await get_lot_text(marketplace_item),
        reply_markup=keyboard.as_markup(),
    )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.remove_preview)
)
@log_in_dev
async def remove_preview_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения предмета в инвентаре."""
    await state.clear()
    keyboard = await remove_preview_keyboard(callback_data)
    await callback.message.edit_text(
        text=REMOVE_CONFIRM_MESSAGE, reply_markup=keyboard.as_markup()
    )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.remove)
)
@log_in_dev
async def remove_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения предмета в инвентаре."""
    await state.clear()
    keyboard = await marketplace_preview_keyboard()
    marketplace_item = await get_marketplace_item(callback_data.id)
    if not marketplace_item:
        await callback.message.edit_text(
            text=NO_MARKETPLACE_ITEM_MESSAGE, reply_markup=keyboard.as_markup()
        )
        return
    success, text = await remove_lot(marketplace_item)
    await callback.message.edit_text(
        text=text, reply_markup=keyboard.as_markup()
    )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.item_search)
)
@log_in_dev
async def item_search_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения предмета в инвентаре."""
    await state.clear()
    keyboard = await to_buy_preview_keyboard()
    await callback.message.edit_text(
        text=ITEM_SEARCH_MESSAGE, reply_markup=keyboard.as_markup()
    )
    await state.update_data(currency=callback_data.currency)
    await state.set_state(MarketplaceState.item_search)


@marketplace_router.message(MarketplaceState.item_search)
@log_in_dev
async def item_search_state(message: types.Message, state: FSMContext):
    """Хендлер обработки количества товаров."""
    data = await state.get_data()
    currency = data["currency"]
    name_contains = message.text
    items_amount = await MarketplaceItem.objects.filter(
        item__name__contains=name_contains,
        sell_currency__name=currency,
    ).acount()
    keyboard = await item_search_keyboard(currency, name_contains)
    await message.answer(
        text=ITEM_SEARCH_AMOUNT_MESSAGE.format(items_amount, name_contains),
        reply_markup=keyboard.as_markup(),
    )


@marketplace_router.callback_query(
    MarketplaceData.filter(F.action == marketplace_action.search_lot_list)
)
@log_in_dev
async def search_lot_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MarketplaceData,
):
    """Коллбек получения предмета в инвентаре."""
    await state.clear()
    paginator = await lot_item_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=SEARCH_ITEM_LIST_MESSAGE, reply_markup=paginator
    )
