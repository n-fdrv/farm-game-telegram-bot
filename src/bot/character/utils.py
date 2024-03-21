import random
import re

from character.models import (
    Character,
    CharacterClass,
    CharacterEffect,
    CharacterItem,
    Skill,
    SkillEffect,
)
from django.utils import timezone
from item.models import EffectProperty, EffectSlug, ItemType
from location.models import LocationDrop
from loguru import logger

from bot.character.keyboards import character_get_keyboard
from bot.character.messages import (
    CHARACTER_ABOUT_MESSAGE,
    CHARACTER_INFO_MESSAGE,
    CHARACTER_KILL_MESSAGE,
)
from bot.location.messages import HUNTING_END_MESSAGE
from bot.models import User
from core.config import game_config


async def check_nickname_exist(nickname: str) -> bool:
    """Проверка занят ли никнейм персонажа."""
    return await Character.objects.filter(name=nickname).aexists()


def check_nickname_correct(nickname: str) -> bool:
    """Валидатор проверки корректности ввода имени и фамилии."""
    if not re.search("^[А-Яа-яA-Za-z0-9]{1,16}$", nickname):
        return False
    return True


async def create_character(
    user: User, name: str, character_class: CharacterClass
) -> Character:
    """Создает персонажа и присваивает его пользователю."""
    character = await Character.objects.acreate(
        name=name,
        character_class=character_class,
        attack=character_class.attack,
        defence=character_class.defence,
    )

    async for skill in character_class.skills.all():
        await character.skills.aadd(skill)
    user.character = character
    await user.asave(update_fields=("character",))
    return character


async def get_property_modifier(
    character: Character, effect_property: EffectProperty
):
    """Получение прибавки характеристики от процентных эффектов."""
    modifier = 1

    premium_data = {
        EffectProperty.DROP: game_config.PREMIUM_DROP_MODIFIER,
        EffectProperty.EXP: game_config.PREMIUM_EXP_MODIFIER,
    }
    if (
        effect_property in premium_data.keys()
        and character.premium_expired > timezone.now()
    ):
        modifier *= premium_data[effect_property]
    async for skill_effect in SkillEffect.objects.select_related(
        "effect"
    ).filter(
        effect__property=effect_property,
        effect__in_percent=True,
        skill__in=character.skills.all(),
    ):
        modifier += modifier * skill_effect.effect.amount / 100
    async for character_effect in CharacterEffect.objects.select_related(
        "effect"
    ).filter(
        effect__property=effect_property,
        character=character,
        expired__gte=timezone.now(),
        effect__in_percent=True,
    ):
        modifier += modifier * character_effect.effect.amount / 100
    async for character_item in CharacterItem.objects.select_related(
        "item"
    ).filter(character=character, equipped=True):
        async for effect in character_item.item.effects.filter(
            property=effect_property, in_percent=True
        ):
            amount = (
                effect.amount
                + character_item.enhancement_level
                * game_config.ENHANCE_TALISMAN_INCREASE
            )
            modifier += modifier * amount / 100
    return modifier


async def get_property_amount(
    character: Character, effect_property: EffectProperty
):
    """Получение прибавки характеристики от непроцентных эффектов."""
    amount = 0
    async for skill_effect in SkillEffect.objects.select_related(
        "effect"
    ).filter(
        effect__property=effect_property,
        effect__in_percent=False,
        skill__in=character.skills.all(),
    ):
        amount += skill_effect.effect.amount
    async for character_effect in CharacterEffect.objects.filter(
        effect__property=effect_property,
        character=character,
        expired__gte=timezone.now(),
        effect__in_percent=False,
    ):
        amount += character_effect.effect.amount
    async for character_item in CharacterItem.objects.select_related(
        "item"
    ).filter(character=character, equipped=True):
        async for effect in character_item.item.effects.filter(
            property=effect_property, in_percent=False
        ):
            amount += (
                effect.amount
                + character_item.enhancement_level
                * game_config.ENHANCE_PROPERTY_INCREASE
            )
    return amount


async def get_character_property(
    character: Character, effect_property: EffectProperty
):
    """Метод получения характеристики персонажа."""
    property_data = {
        EffectProperty.DROP: character.drop_modifier,
        EffectProperty.EXP: character.exp_modifier,
        EffectProperty.ATTACK: character.attack,
        EffectProperty.DEFENCE: character.defence,
        EffectProperty.HUNTING_TIME: character.max_hunting_time,
    }
    chosen_property = property_data[effect_property]
    if effect_property == EffectProperty.HUNTING_TIME:
        chosen_property = (
            character.max_hunting_time.hour * 3600
            + character.max_hunting_time.minute * 60
            + character.max_hunting_time.second
        ) / 60
    if game_config.IN_PERCENT_MODIFIER_FIRST:
        chosen_property *= await get_property_modifier(
            character, effect_property
        )
        chosen_property += await get_property_amount(
            character, effect_property
        )
        return chosen_property
    chosen_property += await get_property_amount(character, effect_property)
    chosen_property *= await get_property_modifier(character, effect_property)
    return chosen_property


async def get_character_info(character: Character) -> str:
    """Возвращает сообщение с данными о персонаже."""
    exp_in_percent = round(character.exp / character.exp_for_level_up * 100, 2)
    location = "<b>Город</b>"
    if character.current_location:
        time_left_text = "<b>Охота окончена</b>"
        if character.hunting_end > timezone.now():
            time_left = str(character.hunting_end - timezone.now()).split(".")[
                0
            ]
            time_left_text = f"Осталось: <b>{time_left}</b>"
        location = (
            f"<b>{character.current_location.name}</b>\n" f"⏳{time_left_text}"
        )
    return CHARACTER_INFO_MESSAGE.format(
        character.name_with_class,
        character.level,
        exp_in_percent,
        int(await get_character_property(character, EffectProperty.ATTACK)),
        int(await get_character_property(character, EffectProperty.DEFENCE)),
        location,
    )


async def get_character_item_with_effects(character_item: CharacterItem):
    """Получение предмета с его эффектами."""
    effects = ""
    async for effect in character_item.item.effects.all():
        amount = (
            effect.amount
            + character_item.enhancement_level
            * game_config.ENHANCE_PROPERTY_INCREASE
        )
        if character_item.item.type == ItemType.TALISMAN:
            amount = (
                effect.amount
                + character_item.enhancement_level
                * game_config.ENHANCE_TALISMAN_INCREASE
            )
        effects += f"{effect.get_property_display()}: {amount}"
        if effect.in_percent:
            effects += "%"
    return f"{character_item.name_with_enhance} ({effects})"


async def get_elixir_with_effects_and_expired(character: Character):
    """Получение эффектов от эликсиров."""
    effects = (
        CharacterEffect.objects.select_related("effect")
        .filter(
            character=character,
            expired__gt=timezone.now(),
        )
        .all()
    )
    return "\n".join(
        [
            f"{x.effect.get_property_with_amount()} - "
            f"<b>{str(x.expired - timezone.now()).split('.')[0]}</b>"
            async for x in effects
        ]
    )


async def get_character_about(character: Character) -> str:
    """Возвращает сообщение с данными о персонаже."""
    exp_in_percent = round(character.exp / character.exp_for_level_up * 100, 2)
    skill_effect = SkillEffect.objects.select_related("effect").filter(
        skill__in=character.skills.all()
    )
    premium_expired = "Нет"
    if character.premium_expired > timezone.now():
        premium_expired = character.premium_expired.strftime("%d.%m.%Y %H:%M")
    return CHARACTER_ABOUT_MESSAGE.format(
        character.name_with_class,
        character.level,
        exp_in_percent,
        int(await get_character_property(character, EffectProperty.ATTACK)),
        int(await get_character_property(character, EffectProperty.DEFENCE)),
        premium_expired,
        round(
            await get_character_property(character, EffectProperty.EXP) * 100
            - 100,
            2,
        ),
        round(
            await get_character_property(character, EffectProperty.DROP) * 100
            - 100,
            2,
        ),
        "\n".join(
            [
                await get_character_item_with_effects(x)
                async for x in CharacterItem.objects.select_related(
                    "item"
                ).filter(character=character, equipped=True)
            ]
        ),
        "\n".join(
            [
                x.effect.get_property_with_amount()
                async for x in skill_effect.all()
            ]
        ),
        await get_elixir_with_effects_and_expired(character),
    )


async def get_hunting_minutes(character: Character):
    """Метод получения минут охоты."""
    hunting_end_time = timezone.now()
    if hunting_end_time > character.hunting_end:
        hunting_end_time = character.hunting_end
    minutes = (hunting_end_time - character.hunting_begin).seconds / 60
    return int(minutes)


async def get_exp(character: Character, exp_amount: int):
    """Метод получения опыта."""
    character.exp += exp_amount
    while character.exp >= character.exp_for_level_up:
        character.exp = character.exp - character.exp_for_level_up
        character.exp_for_level_up += (
            character.exp_for_level_up
            * game_config.EXP_FOR_LEVEL_UP_MULTIPLIER
        )
        character.attack += game_config.ATTACK_INCREASE_LEVEL_UP
        character.defence += game_config.DEFENCE_INCREASE_LEVEL_UP
        character.level += 1
    await character.asave(
        update_fields=("level", "exp", "exp_for_level_up", "attack", "defence")
    )
    return character


async def remove_exp(character: Character, exp_amount: int):
    """Метод отнятия опыта."""
    character.exp -= exp_amount
    if character.exp < 0:
        character.exp = 0
    await character.asave(update_fields=("exp",))
    return character


async def get_hunting_loot(character: Character):
    """Метод получения трофеев с охоты."""
    hunting_minutes = await get_hunting_minutes(character)
    exp_gained = int(character.current_location.exp * hunting_minutes)
    exp_gained *= await get_character_property(character, EffectProperty.EXP)
    drop_data = {}
    location_drop_modifier = (
        character.attack / character.current_location.attack
    )
    drop_modifier = (
        await get_character_property(character, EffectProperty.DROP)
        * location_drop_modifier
    )
    await get_exp(character, exp_gained)
    async for drop in LocationDrop.objects.select_related(
        "item", "location"
    ).filter(location=character.current_location):
        for _minute in range(hunting_minutes):
            chance = drop.chance * drop_modifier
            success = random.uniform(0.01, 100) <= chance
            if success:
                amount = random.randint(drop.min_amount, drop.max_amount)
                item, created = await CharacterItem.objects.aget_or_create(
                    character=character, item=drop.item
                )
                if drop.item.name_with_type not in drop_data:
                    drop_data[drop.item.name_with_type] = 0
                drop_data[drop.item.name_with_type] += amount
                item.amount += amount
                await item.asave(update_fields=("amount",))
    logger.info(
        f"{character} - Вышел из {character.current_location} "
        f"и получил {exp_gained} опыта и "
        f"{drop_data} за {hunting_minutes} минут"
    )
    character.current_location = None
    character.hunting_begin = None
    character.hunting_end = None
    character.job_id = None
    async for character_effect in CharacterEffect.objects.filter(
        character=character, expired__lte=timezone.now()
    ):
        await character_effect.adelete()
    drop_text = "\n"
    for name, amount in drop_data.items():
        drop_text += f"<b>{name}</b> - {amount} шт.\n"
    if not drop_data:
        drop_text = "❌"
    await character.asave(
        update_fields=(
            "current_location",
            "hunting_begin",
            "hunting_end",
            "job_id",
        )
    )
    return exp_gained, drop_text


async def end_hunting(character: Character, bot):
    """Конец охоты по времени."""
    await character.asave(update_fields=("hunting_end",))
    exp_gained, drop_text = await get_hunting_loot(character)
    user = await User.objects.aget(character=character)
    keyboard = await character_get_keyboard(character)
    await bot.send_message(
        user.telegram_id,
        HUNTING_END_MESSAGE.format(exp_gained, drop_text),
        reply_markup=keyboard.as_markup(),
    )


async def kill_character(
    character: Character, bot, attacker: Character = None
):
    """Убийство персонажа."""
    character.hunting_end = timezone.now()
    await character.asave(update_fields=("hunting_end",))
    exp_gained, drop_text = await get_hunting_loot(character)
    lost_exp = int(
        character.exp_for_level_up / 100 * game_config.EXP_DECREASE_PERCENT
    )
    if character.premium_expired > timezone.now():
        lost_exp *= game_config.PREMIUM_DEATH_EXP_MODIFIER
    await remove_exp(character, lost_exp)
    async for character_effect in CharacterEffect.objects.exclude(
        effect__slug=EffectSlug.FATIGUE
    ).filter(
        character=attacker,
    ):
        await character_effect.adelete()
    attacker_text = "Монстры в Локации"
    if attacker:
        attacker_text = attacker.name_with_class
    user = await User.objects.aget(character=character)
    await bot.send_message(
        user.telegram_id,
        CHARACTER_KILL_MESSAGE.format(
            attacker_text, exp_gained - lost_exp, drop_text
        ),
    )


async def get_skill_effects_info(skill: Skill):
    """Метод получения текста эффектов умения."""
    text = ""
    async for effect in skill.effects.all():
        text += f"- {effect.get_property_display()}: <b>{effect.amount}</b>"
        if effect.in_percent:
            text += "<b>%</b>"
        text += "\n"
    return text
