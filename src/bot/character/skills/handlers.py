from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from character.models import Skill

from bot.character.skills.keyboards import (
    skill_get_keyboard,
    skill_list_keyboard,
)
from bot.character.skills.messages import (
    SKILL_GET_MESSAGE,
    SKILL_LIST_MESSAGE,
)
from bot.character.skills.utils import (
    get_skill_effects_info,
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
    skill = await Skill.objects.aget(id=callback_data.id)
    keyboard = await skill_get_keyboard(skill)
    await callback.message.edit_text(
        text=SKILL_GET_MESSAGE.format(
            skill.name_with_level,
            skill.description,
            await get_skill_effects_info(skill),
        ),
        reply_markup=keyboard.as_markup(),
    )
