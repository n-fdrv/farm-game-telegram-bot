from aiogram.utils.keyboard import InlineKeyboardBuilder
from character.models import Character, CharacterClass
from item.models import EffectProperty

from bot.character.buttons import (
    ABOUT_BUTTON,
    AUTO_HP_POTION_BUTTON,
    AUTO_MP_POTION_BUTTON,
    BACKPACK_BUTTON,
    CLASS_CHOOSE_BUTTON,
    EXIT_LOCATION_BUTTON,
    LOCATIONS_BUTTON,
    SHOP_BUTTON,
    SKILLS_BUTTON,
)
from bot.character.messages import TURN_OFF_TEXT, TURN_ON_TEXT
from bot.command.buttons import BACK_BUTTON, YES_BUTTON
from bot.constants.actions import (
    backpack_action,
    character_action,
    location_action,
    shop_action,
)
from bot.constants.callback_data import (
    BackpackData,
    CharacterData,
    LocationData,
    ShopData,
)


async def character_get_keyboard(character: Character):
    """Клавиатура персонажа."""
    keyboard = InlineKeyboardBuilder()
    if character.current_location:
        keyboard.button(
            text=EXIT_LOCATION_BUTTON,
            callback_data=LocationData(
                action=location_action.exit_location_confirm
            ),
        )
    else:
        keyboard.button(
            text=LOCATIONS_BUTTON,
            callback_data=LocationData(action=location_action.list),
        )
        keyboard.button(
            text=SHOP_BUTTON,
            callback_data=ShopData(action=shop_action.get),
        )
    keyboard.button(
        text=BACKPACK_BUTTON,
        callback_data=BackpackData(action=backpack_action.preview),
    )
    keyboard.button(
        text=SKILLS_BUTTON,
        callback_data=CharacterData(action=character_action.skill_list),
    )
    keyboard.button(
        text=ABOUT_BUTTON,
        callback_data=CharacterData(action=character_action.about),
    )
    keyboard.adjust(1, 2, 2)
    return keyboard


async def confirm_nickname_keyboard():
    """Клавиатура подтверждения выбора никнейма."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=YES_BUTTON,
        callback_data=CharacterData(
            action=character_action.class_list,
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.get),
    )
    keyboard.adjust(1)
    return keyboard


async def choose_class_keyboard():
    """Клавиатура выбора класса персонажа."""
    keyboard = InlineKeyboardBuilder()
    async for character_class in CharacterClass.objects.all():
        keyboard.button(
            text=character_class.emoji_name,
            callback_data=CharacterData(
                action=character_action.class_get, id=character_class.id
            ),
        )
    keyboard.adjust(1)
    return keyboard


async def class_get_keyboard(callback_data: CharacterData):
    """Клавиатура выбора класса персонажа."""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=CLASS_CHOOSE_BUTTON,
        callback_data=CharacterData(
            action=character_action.create, id=callback_data.id
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.class_list),
    )
    keyboard.adjust(1)
    return keyboard


async def about_keyboard(character: Character):
    """Клавиатура о персонаже."""
    keyboard = InlineKeyboardBuilder()
    hp_button = AUTO_HP_POTION_BUTTON.format(TURN_OFF_TEXT)
    mp_button = AUTO_MP_POTION_BUTTON.format(TURN_OFF_TEXT)
    if character.auto_use_hp_potion:
        hp_button = AUTO_HP_POTION_BUTTON.format(TURN_ON_TEXT)
    if character.auto_use_mp_potion:
        mp_button = AUTO_MP_POTION_BUTTON.format(TURN_ON_TEXT)
    keyboard.button(
        text=hp_button,
        callback_data=CharacterData(
            action=character_action.auto_use, type=EffectProperty.HEALTH
        ),
    )
    keyboard.button(
        text=mp_button,
        callback_data=CharacterData(
            action=character_action.auto_use, type=EffectProperty.MANA
        ),
    )
    keyboard.button(
        text=BACK_BUTTON,
        callback_data=CharacterData(action=character_action.get),
    )
    keyboard.adjust(1)
    return keyboard
