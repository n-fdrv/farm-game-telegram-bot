from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character, RecipeShare
from django.db.models import Count
from item.models import ItemType

from bot.command.buttons import (
    BACK_BUTTON,
    CANCEL_BUTTON,
    NO_BUTTON,
    YES_BUTTON,
)
from bot.constants.actions import master_shop_action
from bot.constants.callback_data import MasterShopData
from bot.master_shop.buttons import (
    ADD_RECIPE_BUTTON,
    CRAFT_BUTTON,
    CRAFT_MORE_BUTTON,
    LOOK_MASTER_SHOP,
    LOOK_RECIPE_BUTTON,
    SEARCH_RECIPE_BUTTON,
    TO_SEARCH_RECIPE_LIST_BUTTON,
)
from bot.utils.paginator import Paginator


async def master_shop_preview_keyboard(character: Character):
    """Клавиатура превью мастерской."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=LOOK_MASTER_SHOP,
        callback_data=MasterShopData(action=master_shop_action.choose_type),
    )
    if character.character_class.name == "Мастер":
        keyboard.button(
            text=CRAFT_BUTTON,
            callback_data=MasterShopData(action=master_shop_action.craft_list),
        )
        keyboard.button(
            text=ADD_RECIPE_BUTTON,
            callback_data=MasterShopData(
                action=master_shop_action.add_recipe_list
            ),
        )
        keyboard.button(
            text=LOOK_RECIPE_BUTTON,
            callback_data=MasterShopData(
                action=master_shop_action.recipe_list
            ),
        )
    keyboard.adjust(1)
    return keyboard


async def master_shop_choose_type_keyboard():
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    button_number = 0
    row = []
    button_in_row = 2
    items_data = [
        x
        async for x in RecipeShare.objects.values_list(
            "character_recipe__recipe__create__type", flat=True
        ).annotate(Count("character_recipe__recipe__create__type"))
    ]
    if items_data:
        for item_type in ItemType.choices:
            if item_type[0] in items_data:
                keyboard.button(
                    text=item_type[1],
                    callback_data=MasterShopData(
                        action=master_shop_action.list,
                        type=item_type[0],
                    ),
                )
                button_number += 1
                if button_number == button_in_row:
                    row.append(button_number)
                    button_number = 0
        if button_number > 0:
            row.append(button_number)
        keyboard.button(
            text=SEARCH_RECIPE_BUTTON,
            callback_data=MasterShopData(
                action=master_shop_action.search_recipe,
            ),
        )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=MasterShopData(action=master_shop_action.preview),
    )

    keyboard.adjust(*row, 1, 1)
    return keyboard


async def master_shop_list_keyboard(callback_data: MasterShopData):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    async for recipe_share in (
        RecipeShare.objects.select_related(
            "character_recipe", "character_recipe__recipe"
        )
        .filter(
            character_recipe__recipe__create__type=callback_data.type,
        )
        .order_by("price")
    ):
        keyboard.button(
            text=(
                f"{recipe_share.character_recipe.recipe.name_with_chance} - "
                f"{recipe_share.price}🟡"
            ),
            callback_data=MasterShopData(
                action=master_shop_action.get,
                page=callback_data.page,
                id=recipe_share.id,
                type=callback_data.type,
                back_action=callback_data.action,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=master_shop_action.list,
        size=6,
        page=callback_data.page,
        type=callback_data.type,
    )
    return paginator.get_paginator_with_buttons_list(
        [
            (
                BACK_BUTTON,
                MasterShopData(
                    action=master_shop_action.choose_type,
                ),
            ),
        ]
    )


async def master_shop_get_keyboard(callback_data: MasterShopData):
    """Клавиатура получения рецепта."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=CRAFT_BUTTON,
        callback_data=MasterShopData(
            action=master_shop_action.craft_confirm,
            id=callback_data.id,
            type=callback_data.type,
            page=callback_data.page,
        ),
    )
    if not callback_data.back_action:
        callback_data.back_action = master_shop_action.preview
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=MasterShopData(
            action=callback_data.back_action,
            page=callback_data.page,
            name_contains=callback_data.name_contains,
            type=callback_data.type,
        ),
    )

    keyboard.adjust(1)
    return keyboard


async def master_shop_craft_confirm_keyboard(callback_data: MasterShopData):
    """Клавиатура подтверждения изготовления."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=MasterShopData(
            action=master_shop_action.craft,
            id=callback_data.id,
            type=callback_data.type,
            page=callback_data.page,
        ),
    )
    keyboard.button(
        text=NO_BUTTON,
        callback_data=MasterShopData(
            action=master_shop_action.get,
            id=callback_data.id,
            type=callback_data.type,
            page=callback_data.page,
        ),
    )
    keyboard.adjust(2)
    return keyboard


async def master_shop_craft_keyboard(callback_data: MasterShopData):
    """Клавиатура изготовления."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=CRAFT_MORE_BUTTON,
        callback_data=MasterShopData(
            action=master_shop_action.craft_confirm,
            id=callback_data.id,
            type=callback_data.type,
            page=callback_data.page,
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=MasterShopData(
            action=master_shop_action.get,
            id=callback_data.id,
            type=callback_data.type,
            page=callback_data.page,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def master_shop_recipe_search_keyboard():
    """Клавиатура поиска предмета."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=CANCEL_BUTTON,
        callback_data=MasterShopData(
            action=master_shop_action.choose_type,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def recipe_search_keyboard(recipe_name_contains: str):
    """Клавиатура перехода к списку найденных рецептов."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=TO_SEARCH_RECIPE_LIST_BUTTON,
        callback_data=MasterShopData(
            action=master_shop_action.search_recipe_list,
            name_contains=recipe_name_contains,
        ),
    )
    keyboard.button(
        text=CANCEL_BUTTON,
        callback_data=MasterShopData(
            action=master_shop_action.choose_type,
        ),
    )
    keyboard.adjust(1)
    return keyboard


async def master_shop_recipe_search_list_keyboard(
    callback_data: MasterShopData,
):
    """Клавиатура для нового пользователя."""
    keyboard = InlineKeyboardBuilder()
    async for recipe_share in (
        RecipeShare.objects.select_related(
            "character_recipe", "character_recipe__recipe"
        )
        .filter(
            character_recipe__recipe__create__name__contains=callback_data.name_contains,
        )
        .order_by("price")
    ):
        keyboard.button(
            text=(
                f"{recipe_share.character_recipe.recipe.name_with_chance} - "
                f"{recipe_share.price}🟡"
            ),
            callback_data=MasterShopData(
                action=master_shop_action.get,
                page=callback_data.page,
                id=recipe_share.id,
                name_contains=callback_data.name_contains,
                back_action=callback_data.action,
            ),
        )
    keyboard.adjust(1)
    paginator = Paginator(
        keyboard=keyboard,
        action=master_shop_action.search_recipe_list,
        size=6,
        page=callback_data.page,
        name_contains=callback_data.type,
    )
    return paginator.get_paginator_with_buttons_list(
        [
            (
                BACK_BUTTON,
                MasterShopData(
                    action=master_shop_action.choose_type,
                ),
            ),
        ]
    )
