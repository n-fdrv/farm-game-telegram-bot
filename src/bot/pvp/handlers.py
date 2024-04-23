import asyncio

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import Character

from bot.character.keyboards import (
    character_get_keyboard,
)
from bot.constants.actions import pvp_action
from bot.constants.callback_data import PvPData
from bot.pvp.keyboards import (
    attack_character_confirm_keyboard,
    attack_more_keyboard,
    pvp_get_keyboard,
)
from bot.pvp.messages import (
    ATTACK_CHARACTER_MESSAGE,
    CHARACTER_KILL_CONFIRM_MESSAGE,
    NO_WAR_KILL_CONFIRM_MESSAGE,
    WAR_KILL_CONFIRM_MESSAGE,
)
from bot.pvp.utils import (
    attack_character,
    check_clan_war_exists,
    pvp_get_character_about,
)
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

pvp_router = Router()


@pvp_router.callback_query(PvPData.filter(F.action == pvp_action.get))
@log_in_dev
async def pvp_get_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: PvPData,
):
    """Хендлер получения персонажа для ПВП."""
    character = await Character.objects.select_related(
        "current_place", "character_class", "clan"
    ).aget(id=callback_data.id)
    keyboard = await pvp_get_keyboard(callback_data)
    await callback.message.edit_text(
        text=await pvp_get_character_about(character),
        reply_markup=keyboard.as_markup(),
    )


@pvp_router.callback_query(
    PvPData.filter(F.action == pvp_action.attack_confirm)
)
@log_in_dev
async def pvp_attack_confirm_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: PvPData,
):
    """Хендлер подтверждения атаки на персонажа."""
    user = await get_user(callback.from_user.id)
    enemy = await Character.objects.select_related(
        "character_class", "clan"
    ).aget(id=callback_data.id)
    keyboard = await attack_character_confirm_keyboard(callback_data)
    war_text = NO_WAR_KILL_CONFIRM_MESSAGE.format(enemy.name_with_clan)
    if await check_clan_war_exists(user.character, enemy):
        war_text = WAR_KILL_CONFIRM_MESSAGE
    await callback.message.edit_text(
        text=CHARACTER_KILL_CONFIRM_MESSAGE.format(
            enemy.name_with_class, war_text
        ),
        reply_markup=keyboard.as_markup(),
    )


@pvp_router.callback_query(PvPData.filter(F.action == pvp_action.attack))
@log_in_dev
async def pvp_attack_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: PvPData,
):
    """Хендлер атаки на персонажа."""
    target = await Character.objects.select_related(
        "current_place", "character_class", "clan"
    ).aget(id=callback_data.id)
    user = await get_user(callback.from_user.id)
    (more_attack, text, damage_text, callback_data.message_id) = (
        await attack_character(
            user.character,
            target,
            callback.bot,
            callback.message,
            callback_data.message_id,
        )
    )
    if not more_attack:
        keyboard = await character_get_keyboard(user.character)
        await callback.message.delete()
        await callback.message.answer(
            text=text,
            reply_markup=keyboard.as_markup(),
        )
        return
    await callback.message.edit_text(
        text=text,
    )
    seconds = 2
    for i in range(seconds):
        await asyncio.sleep(1)
        await callback.message.edit_text(
            text=ATTACK_CHARACTER_MESSAGE.format(
                target.name_with_clan, damage_text, seconds - i
            ),
        )
    keyboard = await attack_more_keyboard(callback_data)
    await callback.message.edit_text(
        text=ATTACK_CHARACTER_MESSAGE.format(
            target.name_with_clan, damage_text, 0
        ),
        reply_markup=keyboard.as_markup(),
    )
