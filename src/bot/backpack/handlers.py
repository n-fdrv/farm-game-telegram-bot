from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import CharacterItem
from item.models import ItemType, Scroll

from bot.backpack.keyboards import (
    backpack_list_keyboard,
    backpack_preview_keyboard,
    enhance_get_keyboard,
    in_backpack_keyboard,
    item_get_keyboard,
    not_success_equip_keyboard,
    open_more_keyboard,
    use_scroll_keyboards,
)
from bot.backpack.messages import (
    ITEM_LIST_MESSAGE,
    ITEM_PREVIEW_MESSAGE,
    SCROLL_LIST_MESSAGE,
    SUCCESS_OPEN_BAG_MESSAGE,
)
from bot.backpack.utils import (
    equip_item,
    equip_talisman,
    get_character_item_enhance_text,
    get_character_item_info_text,
    get_diamond_amount,
    get_gold_amount,
    open_bag,
    use_potion,
    use_recipe,
    use_scroll,
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
    diamond = await get_diamond_amount(user.character)
    keyboard = await backpack_preview_keyboard(user.character)
    await callback.message.edit_text(
        text=ITEM_PREVIEW_MESSAGE.format(gold, diamond),
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
    # TODO Изображение всех предметов ???
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
    equip_item_data = {
        ItemType.WEAPON: equip_item,
        ItemType.ARMOR: equip_item,
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
        "character__character_class",
        "item",
    ).aget(id=callback_data.id)
    usable_item_data = {
        ItemType.POTION: use_potion,
        ItemType.RECIPE: use_recipe,
    }
    if character_item.item.type == ItemType.SCROLL:
        scroll = await Scroll.objects.aget(pk=character_item.item.pk)
        keyboard = await use_scroll_keyboards(character_item.character, scroll)
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
    keyboard = await in_backpack_keyboard()
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
    keyboard = await enhance_get_keyboard(callback_data)
    character_item = await CharacterItem.objects.select_related("item").aget(
        id=callback_data.id
    )
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
    character_item = await CharacterItem.objects.select_related(
        "item", "character"
    ).aget(id=callback_data.id)
    scroll = await Scroll.objects.aget(pk=callback_data.item_id)
    success, text = await use_scroll(scroll, character_item)
    keyboard = await in_backpack_keyboard()
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup(),
    )
