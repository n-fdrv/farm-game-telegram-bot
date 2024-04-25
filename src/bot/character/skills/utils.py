import datetime

from character.models import (
    Character,
    CharacterEffect,
    CharacterItem,
    CharacterSkill,
    SkillType,
)
from django.utils import timezone
from item.models import EffectProperty

from bot.character.backpack.utils import use_potion
from bot.character.skills.messages import (
    ACTIVE_SKILL_INFO_MESSAGE,
    ERROR_IN_USE_SKILL_MESSAGE,
    NOT_ENOUGH_MANA_MESSAGE,
    NOT_READY_SKILL_MESSAGE,
    SKILL_GET_MESSAGE,
    SUCCESS_USE_SKILL_MESSAGE,
    TOGGLE_SKILL_INFO_MESSAGE,
)
from bot.character.skills.skills_data import create_elixir, regeneration
from bot.character.utils import get_character_property, get_expired_text


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
        effect_time = ""
        if character_skill.skill.effect_time:
            effect_time = (
                "<i>⏳Длительность:</i> "
                f"<b>{character_skill.skill.effect_time}</b>\n"
            )
        add_info = ACTIVE_SKILL_INFO_MESSAGE.format(
            character_skill.skill.mana_cost,
            effect_time,
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


async def use_self_buff(character_skill: CharacterSkill):
    """Использование баффа."""
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
    add_info = ""
    if await character_skill.skill.effects.exclude(
        skill__effect_time=None
    ).aexists():
        await use_self_buff(character_skill)
        return True, SUCCESS_USE_SKILL_MESSAGE.format(
            character_skill.skill.name_with_level, add_info
        )
    skill_data = {
        "Концентрация": regeneration,
        "Создание Эликсира": create_elixir,
    }
    if character_skill.skill.name not in skill_data.keys():
        return False, ERROR_IN_USE_SKILL_MESSAGE
    add_info = await skill_data[character_skill.skill.name](character_skill)
    return True, SUCCESS_USE_SKILL_MESSAGE.format(
        character_skill.skill.name_with_level, add_info
    )


async def use_toggle(character: Character):
    """Проверка на атакующей способности."""
    max_mana = await get_character_property(character, EffectProperty.MAX_MANA)
    exists = await CharacterItem.objects.filter(
        character=character,
        item__effects__property=EffectProperty.MANA,
    ).aexists()
    if character.mana < max_mana * 0.5 and exists:
        character_item = await CharacterItem.objects.select_related(
            "item"
        ).aget(
            character=character,
            item__effects__property=EffectProperty.MANA,
        )
        await use_potion(character, character_item.item)
    async for character_toggle in CharacterSkill.objects.select_related(
        "skill"
    ).filter(character=character, turn_on=True):
        if character.mana < character_toggle.skill.mana_cost:
            continue
        character.mana -= character_toggle.skill.mana_cost
