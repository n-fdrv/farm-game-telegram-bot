from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import CharacterItem
from django.conf import settings
from item.models import ItemType

from bot.character.backpack.keyboards import (
    after_use_scroll_keyboard,
    backpack_list_keyboard,
    backpack_preview_keyboard,
    enhance_get_keyboard,
    enter_put_amount_keyboard,
    item_get_keyboard,
    not_correct_amount_keyboard,
    not_success_equip_keyboard,
    open_more_keyboard,
    put_clan_confirm_keyboard,
    put_item_keyboard,
    use_item_keyboard,
    use_scroll_keyboard,
)
from bot.character.backpack.messages import (
    ENTER_AMOUNT_TO_CLAN_MESSAGE,
    ITEM_LIST_MESSAGE,
    ITEM_PREVIEW_MESSAGE,
    PUT_CONFIRM_MESSAGE,
    SCROLL_LIST_MESSAGE,
    SUCCESS_OPEN_BAG_MESSAGE,
)
from bot.character.backpack.utils import (
    equip_item,
    equip_talisman,
    get_character_item_enhance_text,
    open_bag,
    send_item_to_clan_warehouse,
    use_book,
    use_potion,
    use_recipe,
    use_scroll,
)
from bot.constants.actions import backpack_action
from bot.constants.callback_data import BackpackData
from bot.constants.states import BackpackState
from bot.utils.game_utils import (
    check_correct_amount,
    get_item_amount,
    get_item_info_text,
)
from bot.utils.messages import NOT_CORRECT_AMOUNT_MESSAGE
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
    keyboard = await backpack_preview_keyboard(user.character)
    await callback.message.edit_text(
        text=ITEM_PREVIEW_MESSAGE.format(
            await get_item_amount(user.character, settings.GOLD_NAME),
            await get_item_amount(user.character, settings.DIAMOND_NAME),
        ),
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
    await state.clear()
    if not await CharacterItem.objects.filter(id=callback_data.id).aexists():
        await callback.message.delete()
        return
    character_item = await CharacterItem.objects.select_related(
        "character", "character__clan", "item"
    ).aget(id=callback_data.id)
    keyboard = await item_get_keyboard(character_item.character, callback_data)
    await callback.message.edit_text(
        text=await get_item_info_text(character_item),
        reply_markup=keyboard.as_markup(),
    )


@backpack_router.callback_query(
    BackpackData.filter(F.action == backpack_action.put_clan_amount)
)
@log_in_dev
async def backpack_put_amount(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: BackpackData,
):
    """Коллбек ввода количества предметов на отправку."""
    if not await CharacterItem.objects.filter(id=callback_data.id).aexists():
        await callback.message.delete()
        return
    character_item = await CharacterItem.objects.select_related(
        "character", "character__clan", "item"
    ).aget(id=callback_data.id)
    if character_item.amount > 1:
        keyboard = await enter_put_amount_keyboard(callback_data)
        await callback.message.edit_text(
            text=ENTER_AMOUNT_TO_CLAN_MESSAGE.format(
                character_item.name_with_enhance,
                character_item.character.clan.name_with_emoji,
            ),
            reply_markup=keyboard.as_markup(),
        )
        await state.update_data(
            action=callback_data.action,
            id=callback_data.id,
            type=callback_data.type,
            page=callback_data.page,
            amount=callback_data.amount,
        )
        await state.set_state(BackpackState.item_amount)
        return
    callback_data.amount = 1
    keyboard = await put_clan_confirm_keyboard(callback_data)
    await callback.message.edit_text(
        text=PUT_CONFIRM_MESSAGE.format(
            character_item.name_with_enhance,
            character_item.amount,
            character_item.character.clan.name_with_emoji,
        ),
        reply_markup=keyboard.as_markup(),
    )


@backpack_router.message(BackpackState.item_amount)
@log_in_dev
async def put_to_clan_amount_state_handler(
    message: types.Message, state: FSMContext
):
    """Хендлер ввода количества."""
    amount = message.text
    data = await state.get_data()
    is_correct = await check_correct_amount(amount)
    callback_data = BackpackData(
        action=data["action"],
        id=data["id"],
        type=data["type"],
        page=data["page"],
        amount=data["amount"],
    )
    if not is_correct:
        keyboard = await not_correct_amount_keyboard(callback_data)
        await message.answer(
            text=NOT_CORRECT_AMOUNT_MESSAGE, reply_markup=keyboard.as_markup()
        )
        await state.set_state(BackpackState.item_amount)
        return
    callback_data.amount = amount
    character_item = await CharacterItem.objects.select_related(
        "character", "character__clan", "item"
    ).aget(pk=callback_data.id)
    keyboard = await put_clan_confirm_keyboard(callback_data)
    await message.answer(
        text=PUT_CONFIRM_MESSAGE.format(
            character_item.name_with_enhance,
            amount,
            character_item.character.clan.name_with_emoji,
        ),
        reply_markup=keyboard.as_markup(),
    )


@backpack_router.callback_query(
    BackpackData.filter(F.action == backpack_action.put_clan)
)
@log_in_dev
async def put_into_clan_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: BackpackData,
):
    """Коллбек отправки предмета персонажу."""
    character_item = await CharacterItem.objects.select_related(
        "character", "character__clan", "item", "character__clan__leader"
    ).aget(pk=callback_data.id)
    success, text = await send_item_to_clan_warehouse(
        character_item, callback.bot, callback_data.amount
    )
    keyboard = await put_item_keyboard(callback_data)
    await callback.message.edit_text(
        text=text, reply_markup=keyboard.as_markup()
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
        "character__current_location",
        "character__character_class",
        "item",
    ).aget(id=callback_data.id)
    equip_item_data = {
        ItemType.WEAPON: equip_item,
        ItemType.ARMOR: equip_item,
        ItemType.BRACELET: equip_item,
        ItemType.TALISMAN: equip_talisman,
    }
    success, text = await equip_item_data[character_item.item.type](
        character_item
    )
    if not success:
        keyboard = await not_success_equip_keyboard(callback_data)
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard.as_markup(),
        )
        return
    character_item = await CharacterItem.objects.select_related(
        "character", "character__clan", "item"
    ).aget(id=callback_data.id)
    keyboard = await item_get_keyboard(character_item.character, callback_data)
    await callback.message.edit_text(
        text=await get_item_info_text(character_item),
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
        "character__character_class",
        "item",
    ).aget(id=callback_data.id)
    usable_item_data = {
        ItemType.POTION: use_potion,
        ItemType.RECIPE: use_recipe,
        ItemType.BOOK: use_book,
    }
    if character_item.item.type == ItemType.SCROLL:
        keyboard = await use_scroll_keyboard(character_item)
        await callback.message.edit_text(
            text=SCROLL_LIST_MESSAGE.format(
                character_item.item.name_with_type
            ),
            reply_markup=keyboard.as_markup(),
        )
        return
    success, text = await usable_item_data[character_item.item.type](
        character_item.character, character_item.item
    )
    callback_data.amount = character_item.amount - 1
    keyboard = await use_item_keyboard(callback_data)
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup(),
    )


@backpack_router.callback_query(
    BackpackData.filter(F.action == backpack_action.open)
)
@log_in_dev
async def backpack_open_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: BackpackData,
):
    """Коллбек открытия предмета."""
    character_item = await CharacterItem.objects.select_related(
        "character",
        "item",
    ).aget(id=callback_data.id)
    open_amount = callback_data.amount
    drop_data = await open_bag(
        character_item.character, character_item.item, open_amount
    )
    callback_data.amount = character_item.amount - open_amount
    keyboard = await open_more_keyboard(callback_data)
    await callback.message.edit_text(
        text=SUCCESS_OPEN_BAG_MESSAGE.format(
            character_item.item.name_with_type,
            open_amount,
            "\n".join(
                [
                    f"{name} - {amount} шт."
                    for name, amount in drop_data.items()
                ]
            ),
            character_item.amount - open_amount,
        ),
        reply_markup=keyboard.as_markup(),
    )


@backpack_router.callback_query(
    BackpackData.filter(F.action == backpack_action.enhance_get)
)
@log_in_dev
async def enhance_get_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: BackpackData,
):
    """Коллбек получения предмета для улучшения."""
    if not await CharacterItem.objects.filter(id=callback_data.id).aexists():
        await callback.message.delete()
        return
    character_item = await CharacterItem.objects.select_related("item").aget(
        id=callback_data.id
    )
    keyboard = await enhance_get_keyboard(callback_data)
    await callback.message.edit_text(
        text=await get_character_item_enhance_text(character_item),
        reply_markup=keyboard.as_markup(),
    )


@backpack_router.callback_query(
    BackpackData.filter(F.action == backpack_action.enhance)
)
@log_in_dev
async def enhance_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: BackpackData,
):
    """Коллбек получения предмета для улучшения."""
    exists = (
        await CharacterItem.objects.filter(id=callback_data.id).aexists(),
        await CharacterItem.objects.filter(id=callback_data.item_id).aexists(),
    )
    if False in exists:
        await callback.message.delete()
        return
    enhance_item = await CharacterItem.objects.select_related(
        "item", "character"
    ).aget(id=callback_data.id)
    scroll_item = await CharacterItem.objects.select_related(
        "item", "character"
    ).aget(id=callback_data.item_id)
    new_item, text = await use_scroll(scroll_item, enhance_item)
    callback_data.id = new_item.id
    callback_data.amount = scroll_item.amount - 1
    keyboard = await after_use_scroll_keyboard(callback_data)
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup(),
    )
