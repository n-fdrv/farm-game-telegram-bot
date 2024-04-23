import datetime
import re

from character.models import (
    Character,
    CharacterClass,
    CharacterEffect,
    CharacterItem,
    CharacterPower,
    SkillEffect,
    SkillType,
)
from django.db.models import Q
from django.utils import timezone
from item.models import EffectProperty
from location.models import Dungeon, HuntingZoneType

from bot.character.messages import (
    CHARACTER_ABOUT_MESSAGE,
    CHARACTER_INFO_MESSAGE,
    INCREASE_CLAN_REPUTATION_MESSAGE,
    LEVEL_UP_MESSAGE,
    TURN_OFF_TEXT,
    TURN_ON_TEXT,
)
from bot.models import User
from bot.utils.game_utils import get_expired_text
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
        skill__mana_cost__lte=character.mana,
        skill__in=character.skills.filter(
            Q(type=SkillType.PASSIVE) | Q(characterskill__turn_on=True)
        ),
    ):
        modifier += skill_effect.effect.amount / 100
    async for character_effect in CharacterEffect.objects.select_related(
        "effect"
    ).filter(
        effect__property=effect_property,
        character=character,
        expired__gte=timezone.now(),
        effect__in_percent=True,
    ):
        modifier += character_effect.effect.amount / 100
    async for character_item in CharacterItem.objects.select_related(
        "item"
    ).filter(character=character, equipped=True):
        async for effect in character_item.item.effects.filter(
            property=effect_property, in_percent=True
        ):
            amount = (
                effect.amount
                + character_item.enhancement_level
                * game_config.ENHANCE_IN_PERCENT_INCREASE
            )
            modifier += amount / 100
    if modifier < 0:
        modifier = 0
    return modifier


async def get_property_amount(
    character: Character, effect_property: EffectProperty
):
    """Получение прибавки характеристики от непроцентных эффектов."""
    amount = 0
    async for character_power in CharacterPower.objects.select_related(
        "power__effect"
    ).filter(
        character=character,
        power__effect__property=effect_property,
        power__effect__in_percent=False,
    ):
        amount += character_power.power.effect.amount
    async for skill_effect in SkillEffect.objects.select_related(
        "effect"
    ).filter(
        effect__property=effect_property,
        effect__in_percent=False,
        skill__mana_cost__lte=character.mana,
        skill__in=character.skills.filter(
            Q(type=SkillType.PASSIVE) | Q(characterskill__turn_on=True)
        ),
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
                * game_config.ENHANCE_INCREASE
            )
    return amount


async def get_character_property(
    character: Character, effect_property: EffectProperty
):
    """Метод получения характеристики персонажа."""
    property_data = {
        EffectProperty.DROP: 1,
        EffectProperty.EXP: 1,
        EffectProperty.ATTACK: character.attack,
        EffectProperty.DEFENCE: character.defence,
        EffectProperty.MAX_HEALTH: character.max_health,
        EffectProperty.MAX_MANA: character.max_mana,
        EffectProperty.EVASION: character.evasion,
        EffectProperty.ACCURACY: character.accuracy,
        EffectProperty.CRIT_RATE: character.crit_rate,
        EffectProperty.CRIT_POWER: character.crit_power,
    }
    chosen_property = property_data[effect_property]
    if game_config.IN_PERCENT_MODIFIER_FIRST:
        chosen_property *= await get_property_modifier(
            character, effect_property
        )
        chosen_property += await get_property_amount(
            character, effect_property
        )
        return round(chosen_property, 2)
    chosen_property += await get_property_amount(character, effect_property)
    chosen_property *= await get_property_modifier(character, effect_property)
    return round(chosen_property, 2)


async def get_character_power(character: Character) -> int:
    """Получение силы Персонажа."""
    power_data = [
        await get_character_property(character, EffectProperty.ATTACK),
        await get_character_property(character, EffectProperty.DEFENCE),
        await get_character_property(character, EffectProperty.EVASION) * 4,
        await get_character_property(character, EffectProperty.ACCURACY) * 4,
        await get_character_property(character, EffectProperty.CRIT_RATE) / 2,
        await get_character_property(character, EffectProperty.CRIT_POWER) / 2,
        await get_character_property(character, EffectProperty.MAX_HEALTH) / 3,
        await get_character_property(character, EffectProperty.MAX_MANA) / 2,
    ]
    return int(sum(power_data))


async def get_character_info(character: Character) -> str:
    """Возвращает сообщение с данными о персонаже."""
    exp_in_percent = round(character.exp / character.exp_for_level_up * 100, 2)
    location = "Город"
    if character.current_place:
        location = f"{character.current_place.name}"
        if character.current_place.type == HuntingZoneType.DUNGEON:
            dungeon = await Dungeon.objects.aget(pk=character.current_place.pk)
            time_left = (
                character.hunting_begin
                + datetime.timedelta(hours=dungeon.hunting_hours)
                - timezone.now()
            )
            location += (
                f"\n<i>⏳Осталось:</i> {await get_expired_text(time_left)}"
            )
    clan = "Нет"
    if character.clan:
        clan = character.clan.name_with_emoji
    max_health = await get_character_property(
        character, EffectProperty.MAX_HEALTH
    )
    max_mana = await get_character_property(character, EffectProperty.MAX_MANA)
    hp_text = TURN_OFF_TEXT
    mp_text = TURN_OFF_TEXT
    if character.auto_use_hp_potion:
        hp_text = TURN_ON_TEXT
    if character.auto_use_mp_potion:
        mp_text = TURN_ON_TEXT

    return CHARACTER_INFO_MESSAGE.format(
        character.name_with_class,
        character.level,
        exp_in_percent,
        clan,
        f"{character.health}/{int(max_health)}",
        f"{character.mana}/{int(max_mana)}",
        await get_character_power(character),
        location,
        hp_text,
        mp_text,
    )


async def get_character_item_with_effects(character_item: CharacterItem):
    """Получение предмета с его эффектами."""
    effects = ""
    async for effect in character_item.item.effects.all():
        if effect.in_percent:
            amount = (
                effect.amount
                + character_item.enhancement_level
                * game_config.ENHANCE_IN_PERCENT_INCREASE
            )
        else:
            amount = (
                effect.amount
                + character_item.enhancement_level
                * game_config.ENHANCE_INCREASE
            )
        effects += (
            f"\n- <i>{effect.get_property_display()}:</i> <b>{amount}</b>"
        )
        if effect.in_percent:
            effects += "%"
    return f"{character_item.name_with_enhance}{effects}"


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
    time = timezone.now()
    return "\n".join(
        [
            f"<i>{x.effect.get_property_with_amount()} Осталось: </i> "
            f"<b>{await get_expired_text(x.expired - time)}</b>"
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
    clan = "Нет"
    if character.clan:
        clan = character.clan.name_with_emoji
    max_health = await get_character_property(
        character, EffectProperty.MAX_HEALTH
    )
    max_mana = await get_character_property(character, EffectProperty.MAX_MANA)
    return CHARACTER_ABOUT_MESSAGE.format(
        character.name_with_class,
        character.level,
        exp_in_percent,
        clan,
        character.kills,
        f"{character.health}/{int(max_health)}",
        f"{character.mana}/{int(max_mana)}",
        int(await get_character_property(character, EffectProperty.ATTACK)),
        int(await get_character_property(character, EffectProperty.DEFENCE)),
        int(await get_character_property(character, EffectProperty.ACCURACY)),
        int(await get_character_property(character, EffectProperty.EVASION)),
        int(
            await get_character_property(character, EffectProperty.CRIT_RATE)
            / 10
        ),
        int(
            await get_character_property(character, EffectProperty.CRIT_POWER)
        ),
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
                async for x in skill_effect.filter(
                    Q(skill__type=SkillType.PASSIVE)
                    | Q(skill__characterskill__turn_on=True),
                    skill__characterskill__character=character,
                )
            ]
        ),
        await get_elixir_with_effects_and_expired(character),
    )


async def get_exp(character: Character, exp_amount: int, bot):
    """Метод получения опыта."""
    character.exp += exp_amount * game_config.EXP_RATE
    while character.exp >= character.exp_for_level_up:
        character.exp -= character.exp_for_level_up
        character.exp_for_level_up *= game_config.EXP_FOR_LEVEL_UP_MULTIPLIER
        character.attack += game_config.ATTACK_INCREASE_LEVEL_UP
        character.defence += game_config.DEFENCE_INCREASE_LEVEL_UP
        character.evasion += game_config.EVASION_INCREASE_LEVEL_UP
        character.accuracy += game_config.ACCURACY_INCREASE_LEVEL_UP
        character.level += 1
        character.skill_points += 1
        character.max_health += game_config.HEALTH_INCREASE_LEVEL_UP
        character.max_mana += game_config.MANA_INCREASE_LEVEL_UP
        character.health = character.max_health
        character.mana = character.max_mana
        text = LEVEL_UP_MESSAGE.format(character.level)
        if character.clan:
            gained_reputation = (
                character.level * game_config.REPUTATION_AMOUNT_BY_LEVEL
            )
            character.clan.reputation += gained_reputation
            await character.clan.asave(update_fields=("reputation",))
            text += INCREASE_CLAN_REPUTATION_MESSAGE.format(gained_reputation)
        telegram_id = await User.objects.values_list(
            "telegram_id", flat=True
        ).aget(character=character)
        await bot.send_message(telegram_id, text)
    await character.asave(
        update_fields=(
            "level",
            "exp",
            "exp_for_level_up",
            "attack",
            "defence",
            "evasion",
            "accuracy",
            "health",
            "mana",
            "max_health",
            "max_mana",
            "skill_points",
        )
    )
    return exp_amount * game_config.EXP_RATE


async def remove_exp(character: Character, exp_amount: int):
    """Метод отнятия опыта."""
    character.exp -= exp_amount
    if character.level == 1 and character.exp < 0:
        character.exp = 0
    await character.asave(update_fields=("exp",))
    return character


async def regen_health_or_mana(
    character: Character, health_or_mana: EffectProperty, amount: float
):
    """Регенерация здоровья или маны."""
    if health_or_mana == EffectProperty.HEALTH:
        character.health += amount
        if character.health > await get_character_property(
            character, EffectProperty.MAX_HEALTH
        ):
            character.health = await get_character_property(
                character, EffectProperty.MAX_HEALTH
            )
        await character.asave(update_fields=("health",))
        return character.health
    character.mana += amount
    if character.mana > await get_character_property(
        character, EffectProperty.MAX_MANA
    ):
        character.mana = await get_character_property(
            character, EffectProperty.MAX_MANA
        )
    await character.asave(update_fields=("mana",))
    return character.mana
