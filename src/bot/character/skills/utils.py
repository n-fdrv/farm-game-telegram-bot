import datetime

from character.models import (
    CharacterEffect,
    CharacterSkill,
    SkillType,
)
from django.utils import timezone

from bot.character.skills.messages import (
    ACTIVE_SKILL_INFO_MESSAGE,
    NOT_ENOUGH_MANA_MESSAGE,
    NOT_READY_SKILL_MESSAGE,
    SKILL_GET_MESSAGE,
    SUCCESS_USE_SKILL_MESSAGE,
    TOGGLE_SKILL_INFO_MESSAGE,
)
from bot.character.utils import get_expired_text


async def get_skill_info(character_skill: CharacterSkill):
    """Получение информации о способности."""
    add_info = ""
    skill_type = character_skill.skill.get_type_display()
    if character_skill.skill.type == SkillType.TOGGLE:
        add_info = TOGGLE_SKILL_INFO_MESSAGE.format(
            character_skill.skill.mana_cost,
        )
        active = "❌Выключена"
        if character_skill.turn_on:
            active = "✅Включена"
        skill_type += f" ({active})"
    elif character_skill.skill.type == SkillType.ACTIVE:
        add_info = ACTIVE_SKILL_INFO_MESSAGE.format(
            character_skill.skill.mana_cost,
            character_skill.skill.effect_time,
            character_skill.skill.cooldown,
        )
        cooldown = "✅Готова к использованию"
        if timezone.now() <= character_skill.cooldown:
            expired = character_skill.cooldown - timezone.now()
            cooldown = "⏳До готовности: " f"{await get_expired_text(expired)}"
        skill_type += f" ({cooldown})"
    return SKILL_GET_MESSAGE.format(
        character_skill.skill.name_with_level,
        skill_type,
        character_skill.skill.description,
        add_info,
        "\n".join(
            [
                x.get_property_with_amount()
                async for x in character_skill.skill.effects.all()
            ]
        ),
    )


async def use_skill(character_skill: CharacterSkill):
    """Использование способности."""
    if character_skill.character.mana < character_skill.skill.mana_cost:
        return False, NOT_ENOUGH_MANA_MESSAGE
    if character_skill.cooldown > timezone.now():
        return False, NOT_READY_SKILL_MESSAGE
    character_skill.character.mana -= character_skill.skill.mana_cost
    cooldown_minutes = (
        character_skill.skill.cooldown.hour * 60
        + character_skill.skill.cooldown.minute
        + character_skill.skill.cooldown.second // 60
    )
    character_skill.cooldown = timezone.now() + datetime.timedelta(
        minutes=int(cooldown_minutes),
    )
    await character_skill.asave(update_fields=("cooldown",))
    await character_skill.character.asave(update_fields=("mana",))
    async for effect in character_skill.skill.effects.all():
        effect_minutes = (
            character_skill.skill.effect_time.hour * 60
            + character_skill.skill.effect_time.minute
            + character_skill.skill.effect_time.second // 60
        )
        await CharacterEffect.objects.acreate(
            character=character_skill.character,
            effect=effect,
            expired=timezone.now()
            + datetime.timedelta(
                minutes=int(effect_minutes),
            ),
        )
    return True, SUCCESS_USE_SKILL_MESSAGE.format(
        character_skill.skill.name_with_level
    )
