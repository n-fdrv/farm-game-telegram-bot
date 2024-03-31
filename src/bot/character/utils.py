import datetime
import random
import re

from character.models import (
    Character,
    CharacterClass,
    CharacterEffect,
    CharacterItem,
    CharacterSkill,
    SkillEffect,
    SkillType,
)
from clan.models import ClanWar
from django.db.models import Q
from django.utils import timezone
from item.models import Effect, EffectProperty, EffectSlug
from location.models import LocationDrop

from bot.character.keyboards import character_get_keyboard
from bot.character.messages import (
    CHARACTER_ABOUT_MESSAGE,
    CHARACTER_INFO_MESSAGE,
    CHARACTER_KILL_MESSAGE,
    INCREASE_CLAN_REPUTATION_MESSAGE,
    LEVEL_UP_MESSAGE,
    NO_WAR_KILL_MESSAGE_TO_ATTACKER,
    SUCCESS_KILL_MESSAGE_TO_ATTACKER,
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


async def check_clan_war_exists(attacker: Character, enemy: Character):
    """Проверка есть ли война между персонажами."""
    if attacker.clan and enemy.clan:
        return await ClanWar.objects.filter(
            Q(clan=attacker.clan, enemy=enemy.clan, accepted=True)
            | Q(enemy=attacker.clan, clan=enemy.clan, accepted=True)
        ).aexists()
    return False


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
        EffectProperty.DROP: game_config.DROP_RATE,
        EffectProperty.EXP: game_config.EXP_RATE,
        EffectProperty.ATTACK: character.attack,
        EffectProperty.DEFENCE: character.defence,
        EffectProperty.HUNTING_TIME: character.max_hunting_time,
        EffectProperty.MAX_HEALTH: character.max_health,
        EffectProperty.MAX_MANA: character.max_mana,
    }
    chosen_property = property_data[effect_property]
    if effect_property == EffectProperty.HUNTING_TIME:
        chosen_property = (
            character.max_hunting_time.hour * 60
            + character.max_hunting_time.minute
            + character.max_hunting_time.second // 60
        )
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
    return round(chosen_property, 2)


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
    clan = "Нет"
    if character.clan:
        clan = character.clan.name_with_emoji
    max_health = await get_character_property(
        character, EffectProperty.MAX_HEALTH
    )
    max_mana = await get_character_property(character, EffectProperty.MAX_MANA)
    return CHARACTER_INFO_MESSAGE.format(
        character.name_with_class,
        character.level,
        exp_in_percent,
        clan,
        f"{character.health}/{max_health}",
        f"{character.mana}/{max_mana}",
        int(await get_character_property(character, EffectProperty.ATTACK)),
        int(await get_character_property(character, EffectProperty.DEFENCE)),
        location,
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


async def get_expired_text(time_left: datetime.timedelta):
    """Получения остатка времени действия эликсира."""
    if time_left > datetime.timedelta(days=1):
        return f"более {time_left.days} суток"
    return str(time_left).split(".")[0]


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
        f"{character.health}/{max_health}",
        f"{character.mana}/{max_mana}",
        int(await get_character_property(character, EffectProperty.ATTACK)),
        int(await get_character_property(character, EffectProperty.DEFENCE)),
        character.kills,
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


async def get_hunting_minutes(character: Character):
    """Метод получения минут охоты."""
    hunting_end_time = timezone.now()
    if hunting_end_time > character.hunting_end:
        hunting_end_time = character.hunting_end
    minutes = (hunting_end_time - character.hunting_begin).seconds / 60
    return int(minutes)


async def get_exp(character: Character, exp_amount: int, bot):
    """Метод получения опыта."""
    character.exp += exp_amount
    while character.exp >= character.exp_for_level_up:
        character.exp -= character.exp_for_level_up
        character.exp_for_level_up *= game_config.EXP_FOR_LEVEL_UP_MULTIPLIER
        character.attack += game_config.ATTACK_INCREASE_LEVEL_UP
        character.defence += game_config.DEFENCE_INCREASE_LEVEL_UP
        character.level += 1
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
            "health",
            "mana",
            "max_health",
            "max_mana",
        )
    )
    return character


async def remove_exp(character: Character, exp_amount: int):
    """Метод отнятия опыта."""
    character.exp -= exp_amount
    if character.level == 1 and character.exp < 0:
        character.exp = 0
    while character.exp < 0:
        character.level -= 1
        character.exp_for_level_up /= game_config.EXP_FOR_LEVEL_UP_MULTIPLIER
        character.exp += character.exp_for_level_up
        character.attack -= game_config.ATTACK_INCREASE_LEVEL_UP
        character.defence -= game_config.DEFENCE_INCREASE_LEVEL_UP
        character.max_health -= game_config.HEALTH_INCREASE_LEVEL_UP
        character.max_mana -= game_config.MANA_INCREASE_LEVEL_UP
        character.health = character.max_health
        character.mana = character.max_mana

    await character.asave(
        update_fields=(
            "level",
            "exp",
            "exp_for_level_up",
            "attack",
            "defence",
            "health",
            "mana",
            "max_health",
            "max_mana",
        )
    )
    return character


async def use_toggle(character: Character):
    """Проверка на атакующей способности."""
    counter = 0
    async for character_toggle in CharacterSkill.objects.select_related(
        "skill"
    ).filter(character=character, turn_on=True):
        if character.mana < character_toggle.skill.mana_cost:
            continue
        character.mana -= character_toggle.skill.mana_cost
        counter += 1
    return counter


async def get_health_reducing(character: Character):
    """Получение снятия хп за минуту в локации."""
    health_reducing = (
        character.current_location.attack
        - await get_character_property(character, EffectProperty.DEFENCE)
    )
    if health_reducing < 0:
        health_reducing = 0
    return health_reducing


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


async def get_hunting_loot(character: Character, bot):
    """Метод получения трофеев с охоты."""
    hunting_stats = {
        "farm_minutes": 0,
        "relax_minutes": 0,
        "skill_uses": 0,
    }
    hunting_minutes = await get_hunting_minutes(character)
    health_reducing = await get_health_reducing(character)
    drop_modifier = (
        await get_character_property(character, EffectProperty.DROP),
    )
    max_mana = (
        await get_character_property(character, EffectProperty.MAX_MANA),
    )
    location_exp = (
        (
            character.current_location.exp
            * await get_character_property(character, EffectProperty.EXP)
        ),
    )

    exp_gained = 0
    drop_data = {}
    for _minute in range(hunting_minutes):
        if character.health < health_reducing:
            await regen_health_or_mana(
                character,
                EffectProperty.HEALTH,
                game_config.HEALTH_REGENERATION_IN_MINUTE,
            )
            hunting_stats["relax_minutes"] += 1
            continue
        hunting_stats["skill_uses"] += await use_toggle(character)
        hunting_stats["exp_gained"] += hunting_stats["location_exp"]
        drop_chance = (
            drop_modifier
            * await get_character_property(character, EffectProperty.ATTACK)
            / character.current_location.defence
        )
        exp_gained += location_exp
        async for drop in LocationDrop.objects.select_related(
            "item", "location"
        ).filter(location=character.current_location):
            if random.uniform(0.01, 100) <= drop.chance * drop_chance:
                amount = random.randint(drop.min_amount, drop.max_amount)
                item, created = await CharacterItem.objects.aget_or_create(
                    character=character, item=drop.item
                )
                if drop.item.name_with_type not in drop_data:
                    drop_data[drop.item.name_with_type] = 0
                drop_data[drop.item.name_with_type] += amount
                item.amount += amount
                await item.asave(update_fields=("amount",))
        character.health -= health_reducing
        character.mana += game_config.MANA_REGENERATION_IN_MINUTE
        if character.mana > max_mana:
            character.mana = max_mana
        hunting_stats["farm_minutes"] += 1
    await get_exp(character, exp_gained, bot)
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
            "health",
            "mana",
        )
    )
    return HUNTING_END_MESSAGE.format(
        round(exp_gained / character.exp_for_level_up * 100, 2),
        hunting_stats["farm_minutes"],
        hunting_stats["skill_uses"],
        hunting_stats["relax_minutes"],
        drop_text,
    )


async def end_hunting(character: Character, bot):
    """Конец охоты по времени."""
    await character.asave(update_fields=("hunting_end",))
    text = await get_hunting_loot(character, bot)
    user = await User.objects.aget(character=character)
    keyboard = await character_get_keyboard(character)
    await bot.send_message(
        user.telegram_id,
        text,
        reply_markup=keyboard.as_markup(),
    )


async def kill_character(
    character: Character, bot, attacker: Character = None
):
    """Убийство персонажа."""
    decrease_exp = game_config.EXP_DECREASE_PERCENT
    if attacker:
        attacker_text = SUCCESS_KILL_MESSAGE_TO_ATTACKER.format(
            character.name_with_clan
        )
        attacker.kills += 1
        await attacker.asave(update_fields=("kills",))
        if await check_clan_war_exists(attacker, character):
            decrease_exp = game_config.WAR_EXP_DECREASE_PERCENT
            if character.clan.reputation:
                character.clan.reputation -= 1
                attacker.clan.reputation += 1
                await character.clan.asave(update_fields=("reputation",))
                await attacker.clan.asave(update_fields=("reputation",))
                attacker_text += INCREASE_CLAN_REPUTATION_MESSAGE.format("1")
        else:
            async for effect in Effect.objects.filter(slug=EffectSlug.FATIGUE):
                fatigue, created = (
                    await CharacterEffect.objects.aget_or_create(
                        character=attacker,
                        effect=effect,
                    )
                )
                fatigue.expired += datetime.timedelta(hours=1)
                await fatigue.asave(update_fields=("expired",))
            attacker_text += NO_WAR_KILL_MESSAGE_TO_ATTACKER
        attacker_telegram_id = await User.objects.values_list(
            "telegram_id", flat=True
        ).aget(character=attacker)
        await bot.send_message(attacker_telegram_id, attacker_text)
    character_telegram_id = await User.objects.values_list(
        "telegram_id", flat=True
    ).aget(character=character)
    attacker_name = "Монстры в Локации"
    if attacker:
        attacker_name = attacker.name_with_clan
    if character.current_location:
        character.hunting_end = timezone.now()
        await character.asave(update_fields=("hunting_end",))
        text = await get_hunting_loot(character, bot)
        await bot.send_message(
            character_telegram_id,
            text,
        ),
    lost_exp = int(character.exp_for_level_up / 100 * decrease_exp)
    if character.premium_expired > timezone.now():
        lost_exp *= game_config.PREMIUM_DEATH_EXP_MODIFIER
    await remove_exp(character, lost_exp)
    async for character_effect in CharacterEffect.objects.exclude(
        effect__slug=EffectSlug.FATIGUE
    ).filter(
        character=character,
    ):
        await character_effect.adelete()
    await bot.send_message(
        character_telegram_id,
        CHARACTER_KILL_MESSAGE.format(attacker_name, round(lost_exp, 2)),
    )
