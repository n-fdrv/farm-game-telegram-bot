from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import CharacterSkill

from bot.character.skills.keyboards import (
    skill_get_keyboard,
    skill_list_keyboard,
    skill_use_keyboard,
)
from bot.character.skills.messages import (
    SKILL_LIST_MESSAGE,
)
from bot.character.skills.utils import (
    get_skill_info,
    use_skill,
)
from bot.constants.actions import character_action
from bot.constants.callback_data import CharacterData
from bot.utils.user_helpers import get_user
from core.config.logging import log_in_dev

character_skills_router = Router()


@character_skills_router.callback_query(
    CharacterData.filter(F.action == character_action.skill_list)
)
@log_in_dev
async def skill_list_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер получения умений персонажа."""
    user = await get_user(callback.from_user.id)
    paginator = await skill_list_keyboard(user.character, callback_data)
    await callback.message.edit_text(
        text=SKILL_LIST_MESSAGE, reply_markup=paginator
    )


@character_skills_router.callback_query(
    CharacterData.filter(F.action == character_action.skill_get)
)
@log_in_dev
async def skill_get_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер получения умения персонажа."""
    character_skill = await CharacterSkill.objects.select_related(
        "skill", "character"
    ).aget(pk=callback_data.id)
    keyboard = await skill_get_keyboard(character_skill)
    await callback.message.edit_text(
        text=await get_skill_info(character_skill),
        reply_markup=keyboard.as_markup(),
    )


@character_skills_router.callback_query(
    CharacterData.filter(F.action == character_action.skill_toggle)
)
@log_in_dev
async def skill_toggle_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер получения умений персонажа."""
    character_skill = await CharacterSkill.objects.select_related(
        "skill"
    ).aget(pk=callback_data.id)
    character_skill.turn_on = not character_skill.turn_on
    await character_skill.asave(update_fields=("turn_on",))
    keyboard = await skill_get_keyboard(character_skill)
    await callback.message.edit_text(
        text=await get_skill_info(character_skill),
        reply_markup=keyboard.as_markup(),
    )


@character_skills_router.callback_query(
    CharacterData.filter(F.action == character_action.skill_use)
)
@log_in_dev
async def skill_use_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: CharacterData,
):
    """Хендлер получения умений персонажа."""
    character_skill = await CharacterSkill.objects.select_related(
        "skill", "character"
    ).aget(pk=callback_data.id)
    success, text = await use_skill(character_skill)
    keyboard = await skill_use_keyboard()
    await callback.message.edit_text(
        text=text, reply_markup=keyboard.as_markup()
    )
