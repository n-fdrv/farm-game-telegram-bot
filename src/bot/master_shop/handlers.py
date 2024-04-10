from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import CharacterRecipe, RecipeShare

from bot.command.buttons import MASTER_SHOP_BUTTON
from bot.command.keyboards import user_created_keyboard
from bot.command.messages import NOT_CREATED_CHARACTER_MESSAGE
from bot.constants.actions import master_shop_action
from bot.constants.callback_data import MasterShopData
from bot.constants.states import MasterShopState
from bot.master_shop.keyboards import (
    enter_recipe_price_keyboard,
    master_shop_choose_type_keyboard,
    master_shop_craft_choose_type_keyboard,
    master_shop_craft_confirm_keyboard,
    master_shop_craft_get_keyboard,
    master_shop_craft_keyboard,
    master_shop_craft_list_keyboard,
    master_shop_get_keyboard,
    master_shop_list_keyboard,
    master_shop_preview_keyboard,
    master_shop_recipe_list_keyboard,
    master_shop_recipe_search_keyboard,
    master_shop_recipe_search_list_keyboard,
    recipe_create_confirm_keyboard,
    recipe_search_keyboard,
    recipe_update_keyboard,
)
from bot.master_shop.messages import (
    ENTER_RECIPE_PRICE_MESSAGE,
    MASTER_SHOP_CHOOSE_TYPE_MESSAGE,
    MASTER_SHOP_CRAFT_CONFIRM,
    MASTER_SHOP_LIST_MESSAGE,
    MASTER_SHOP_PREVIEW_MESSAGE,
    RECIPE_CREATE_CONFIRM_MESSAGE,
    RECIPE_DELETE_CONFIRM_MESSAGE,
    RECIPE_LIST_MESSAGE,
    RECIPE_SEARCH_AMOUNT_MESSAGE,
    RECIPE_SEARCH_MESSAGE,
    SEARCH_RECIPE_LIST_MESSAGE,
)
from bot.master_shop.utils import (
    craft_item,
    get_character_recipe_info,
    get_share_recipe_info,
    share_recipe_update,
)
from bot.utils.game_utils import check_correct_amount
from bot.utils.messages import (
    NOT_CORRECT_PRICE_MESSAGE,
)
from bot.utils.user_helpers import get_user
from core.config import game_config
from core.config.logging import log_in_dev

master_shop_router = Router()


@master_shop_router.message(F.text == MASTER_SHOP_BUTTON)
@log_in_dev
async def clan_preview_handler(message: types.Message, state: FSMContext):
    """Хендлер меню Клана."""
    await state.clear()
    user = await get_user(message.from_user.id)
    if not user.character:
        inline_keyboard = await user_created_keyboard()
        await message.answer(
            text=NOT_CREATED_CHARACTER_MESSAGE,
            reply_markup=inline_keyboard.as_markup(),
        )
        return
    keyboard = await master_shop_preview_keyboard(user.character)
    await message.answer(
        text=MASTER_SHOP_PREVIEW_MESSAGE,
        reply_markup=keyboard.as_markup(),
    )


@master_shop_router.callback_query(
    MasterShopData.filter(F.action == master_shop_action.preview)
)
@log_in_dev
async def master_shop_preview_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MasterShopData,
):
    """Коллбек меню Клана."""
    await state.clear()
    user = await get_user(callback.from_user.id)
    if not user.character:
        inline_keyboard = await user_created_keyboard()
        await callback.message.edit_text(
            text=NOT_CREATED_CHARACTER_MESSAGE,
            reply_markup=inline_keyboard.as_markup(),
        )
        return
    keyboard = await master_shop_preview_keyboard(user.character)
    await callback.message.edit_text(
        text=MASTER_SHOP_PREVIEW_MESSAGE,
        reply_markup=keyboard.as_markup(),
    )


@master_shop_router.callback_query(
    MasterShopData.filter(F.action == master_shop_action.choose_type)
)
@log_in_dev
async def master_shop_choose_type_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MasterShopData,
):
    """Коллбек меню Клана."""
    keyboard = await master_shop_choose_type_keyboard()
    await callback.message.edit_text(
        text=MASTER_SHOP_CHOOSE_TYPE_MESSAGE,
        reply_markup=keyboard.as_markup(),
    )


@master_shop_router.callback_query(
    MasterShopData.filter(F.action == master_shop_action.list)
)
@log_in_dev
async def master_shop_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MasterShopData,
):
    """Коллбек меню Клана."""
    paginator = await master_shop_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=MASTER_SHOP_LIST_MESSAGE,
        reply_markup=paginator,
    )


@master_shop_router.callback_query(
    MasterShopData.filter(F.action == master_shop_action.get)
)
@log_in_dev
async def master_shop_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MasterShopData,
):
    """Коллбек меню Клана."""
    user = await get_user(callback.from_user.id)
    recipe_share = await RecipeShare.objects.select_related(
        "character_recipe__character",
        "character_recipe__character__clan",
        "character_recipe__recipe",
        "character_recipe__recipe__create",
    ).aget(pk=callback_data.id)
    keyboard = await master_shop_get_keyboard(callback_data)
    await callback.message.edit_text(
        text=await get_share_recipe_info(user.character, recipe_share),
        reply_markup=keyboard.as_markup(),
    )


@master_shop_router.callback_query(
    MasterShopData.filter(F.action == master_shop_action.craft_confirm)
)
@log_in_dev
async def master_shop_craft_confirm_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MasterShopData,
):
    """Коллбек меню Клана."""
    keyboard = await master_shop_craft_confirm_keyboard(callback_data)
    await callback.message.edit_text(
        text=MASTER_SHOP_CRAFT_CONFIRM,
        reply_markup=keyboard.as_markup(),
    )


@master_shop_router.callback_query(
    MasterShopData.filter(F.action == master_shop_action.craft)
)
@log_in_dev
async def master_shop_craft_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MasterShopData,
):
    """Коллбек меню Клана."""
    user = await get_user(callback.from_user.id)
    recipe_share = await RecipeShare.objects.select_related(
        "character_recipe__character",
        "character_recipe__character__clan",
        "character_recipe__recipe",
        "character_recipe__recipe__create",
    ).aget(pk=callback_data.id)
    success, text = await craft_item(
        user.character, recipe_share, callback.bot
    )
    keyboard = await master_shop_craft_keyboard(callback_data)
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup(),
    )


@master_shop_router.callback_query(
    MasterShopData.filter(F.action == master_shop_action.search_recipe)
)
@log_in_dev
async def recipe_search_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MasterShopData,
):
    """Коллбек получения предмета в инвентаре."""
    await state.clear()
    keyboard = await master_shop_recipe_search_keyboard()
    await callback.message.edit_text(
        text=RECIPE_SEARCH_MESSAGE, reply_markup=keyboard.as_markup()
    )
    await state.set_state(MasterShopState.recipe_search)


@master_shop_router.message(MasterShopState.recipe_search)
@log_in_dev
async def recipe_search_state(message: types.Message, state: FSMContext):
    """Хендлер обработки количества товаров."""
    name_contains = message.text
    items_amount = await RecipeShare.objects.filter(
        character_recipe__recipe__name__contains=name_contains,
    ).acount()
    keyboard = await recipe_search_keyboard(name_contains)
    await message.answer(
        text=RECIPE_SEARCH_AMOUNT_MESSAGE.format(items_amount, name_contains),
        reply_markup=keyboard.as_markup(),
    )


@master_shop_router.callback_query(
    MasterShopData.filter(F.action == master_shop_action.search_recipe_list)
)
@log_in_dev
async def search_recipe_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MasterShopData,
):
    """Коллбек получения предмета в инвентаре."""
    await state.clear()
    paginator = await master_shop_recipe_search_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=SEARCH_RECIPE_LIST_MESSAGE, reply_markup=paginator
    )


@master_shop_router.callback_query(
    MasterShopData.filter(F.action == master_shop_action.craft_choose_type)
)
@log_in_dev
async def master_shop_craft_choose_type_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MasterShopData,
):
    """Коллбек меню Клана."""
    keyboard = await master_shop_craft_choose_type_keyboard(callback_data)
    await callback.message.edit_text(
        text=MASTER_SHOP_CHOOSE_TYPE_MESSAGE,
        reply_markup=keyboard.as_markup(),
    )


@master_shop_router.callback_query(
    MasterShopData.filter(F.action == master_shop_action.craft_list)
)
@log_in_dev
async def master_shop_craft_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MasterShopData,
):
    """Коллбек получения предмета в инвентаре."""
    paginator = await master_shop_craft_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=MASTER_SHOP_LIST_MESSAGE, reply_markup=paginator
    )


@master_shop_router.callback_query(
    MasterShopData.filter(F.action == master_shop_action.craft_get)
)
@log_in_dev
async def master_shop_craft_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MasterShopData,
):
    """Коллбек меню Клана."""
    character_recipe = await CharacterRecipe.objects.select_related(
        "character", "recipe", "recipe__create"
    ).aget(pk=callback_data.id)
    keyboard = await master_shop_craft_get_keyboard(
        character_recipe, callback_data.back_action
    )
    await callback.message.edit_text(
        text=await get_character_recipe_info(character_recipe),
        reply_markup=keyboard.as_markup(),
    )


@master_shop_router.callback_query(
    MasterShopData.filter(F.action == master_shop_action.recipe_list)
)
@log_in_dev
async def master_shop_recipe_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MasterShopData,
):
    """Коллбек меню Клана."""
    recipe_share_amount = await RecipeShare.objects.filter(
        character_recipe__character__pk=callback_data.character_id
    ).acount()
    paginator = await master_shop_recipe_list_keyboard(callback_data)
    await callback.message.edit_text(
        text=RECIPE_LIST_MESSAGE.format(
            recipe_share_amount, game_config.MAX_RECIPE_AMOUNT
        ),
        reply_markup=paginator,
    )


@master_shop_router.callback_query(
    MasterShopData.filter(F.action == master_shop_action.recipe_create_amount)
)
@log_in_dev
async def master_shop_recipe_create_amount_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MasterShopData,
):
    """Коллбек меню Клана."""
    keyboard = await enter_recipe_price_keyboard(callback_data)
    await callback.message.edit_text(
        text=ENTER_RECIPE_PRICE_MESSAGE,
        reply_markup=keyboard.as_markup(),
    )
    await state.update_data(
        action=callback_data.action,
        id=callback_data.id,
        back_action=callback_data.back_action,
    )
    await state.set_state(MasterShopState.enter_price)


@master_shop_router.message(MasterShopState.enter_price)
@log_in_dev
async def master_shop_enter_price_handler(
    message: types.Message, state: FSMContext
):
    """Хендлер ввода количества."""
    price = message.text
    data = await state.get_data()
    is_correct = await check_correct_amount(price)
    callback_data = MasterShopData(
        action=data["action"], id=data["id"], back_action=data["back_action"]
    )
    if not is_correct:
        keyboard = await enter_recipe_price_keyboard(callback_data)
        await message.answer(
            text=NOT_CORRECT_PRICE_MESSAGE, reply_markup=keyboard.as_markup()
        )
        await state.set_state(MasterShopState.enter_price)
        return
    callback_data.price = price
    character_recipe = await CharacterRecipe.objects.select_related(
        "recipe"
    ).aget(pk=callback_data.id)
    keyboard = await recipe_create_confirm_keyboard(callback_data)
    await message.answer(
        text=RECIPE_CREATE_CONFIRM_MESSAGE.format(
            character_recipe.recipe.name_with_chance, price
        ),
        reply_markup=keyboard.as_markup(),
    )
    await state.clear()


@master_shop_router.callback_query(
    MasterShopData.filter(F.action == master_shop_action.recipe_delete_confirm)
)
@log_in_dev
async def master_shop_recipe_delete_confirm_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MasterShopData,
):
    """Коллбек меню Клана."""
    character_recipe = await CharacterRecipe.objects.select_related(
        "recipe"
    ).aget(pk=callback_data.id)
    keyboard = await recipe_create_confirm_keyboard(callback_data)
    await callback.message.edit_text(
        text=RECIPE_DELETE_CONFIRM_MESSAGE.format(
            character_recipe.recipe.name_with_chance
        ),
        reply_markup=keyboard.as_markup(),
    )


@master_shop_router.callback_query(
    MasterShopData.filter(F.action == master_shop_action.recipe_update)
)
@log_in_dev
async def master_shop_recipe_update_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: MasterShopData,
):
    """Коллбек меню Клана."""
    character_recipe = await CharacterRecipe.objects.select_related(
        "recipe", "character"
    ).aget(pk=callback_data.id)
    success, text = await share_recipe_update(
        character_recipe, callback_data.price
    )
    keyboard = await recipe_update_keyboard(callback_data)
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup(),
    )
