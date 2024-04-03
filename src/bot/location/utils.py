import datetime
import random

from aiogram.types import Message
from character.models import (
    Character,
    CharacterEffect,
    CharacterItem,
    CharacterSkill,
)
from django.utils import timezone
from item.models import Effect, EffectProperty, EffectSlug
from location.models import Location, LocationDrop
from loguru import logger

from bot.character.backpack.utils import use_potion
from bot.character.keyboards import character_get_keyboard
from bot.character.utils import (
    check_clan_war_exists,
    get_character_item_with_effects,
    get_character_property,
    get_elixir_with_effects_and_expired,
    get_exp,
    regen_health_or_mana,
    remove_exp,
)
from bot.location.keyboards import attack_keyboard
from bot.location.messages import (
    ALREADY_IN_LOCATION_MESSAGE,
    ATTACK_CHARACTER_MESSAGE,
    ATTACK_CHARACTER_MESSAGE_TO_TARGET,
    AUTO_USE_HP_TEXT,
    AUTO_USE_MP_TEXT,
    CHARACTER_KILL_MESSAGE,
    HUNTING_END_MESSAGE,
    KILL_CHARACTER_MESSAGE_TO_ATTACKER,
    LOCATION_CHARACTER_GET_MESSAGE,
    LOCATION_ENTER_MESSAGE,
    LOCATION_FULL_MESSAGE,
    LOCATION_GET_MESSAGE,
    LOCATION_NOT_AVAILABLE,
    LOCATION_WEEK_STRONG_MESSAGE,
    NO_WAR_KILL_MESSAGE_TO_ATTACKER,
    WAR_KILL_MESSAGE_TO_ATTACKER,
)
from bot.models import User
from core.config import game_config


async def get_location_attack_effect(
    character: Character, location: Location
) -> str:
    """Получение информации об эффектах защиты локации."""
    attack = await get_character_property(character, EffectProperty.ATTACK)
    attack_buff = attack / location.attack * 100 - 100
    if attack_buff < 0:
        return (
            f"<i>❌ Ваша атака меньше! "
            f"Штраф к падению предметов:</i> <b>{int(attack_buff)}%</b>"
        )
    return (
        f"<i>✅ Ваша атака больше! "
        f"Бонус к падению предметов:</i> <b>+{int(attack_buff)}%</b>"
    )


async def get_location_drop(character: Character, location: Location) -> str:
    """Получение информации об эффектах защиты локации."""
    attack = await get_character_property(character, EffectProperty.ATTACK)
    attack_buff = attack / location.attack
    drop_modifier = await get_character_property(
        character, EffectProperty.DROP
    )
    drop_buff = drop_modifier * attack_buff
    drop_data = ""
    async for location_drop in (
        LocationDrop.objects.select_related("item")
        .filter(location=location)
        .order_by("-chance")
    ):
        chance = round(location_drop.chance * drop_buff, 2)
        chance_limit = 100
        if chance > chance_limit:
            chance = chance_limit
        amount = ""
        if location_drop.max_amount > 1:
            amount = (
                f"({location_drop.min_amount}-{location_drop.max_amount}) "
            )
        drop_data += (
            f"<b>{location_drop.item.name_with_type}</b> "
            f"<i>{amount}- {chance}%</i>\n"
        )
    return drop_data


async def get_location_info(character: Character, location: Location) -> str:
    """Возвращает сообщение с данными о персонаже."""
    defence = await get_character_property(character, EffectProperty.DEFENCE)
    health_reducing = location.attack - defence
    if health_reducing < 0:
        health_reducing = 0
    hunting_time = (
        await get_character_property(character, EffectProperty.HUNTING_TIME)
        * defence
        / location.defence
    )
    characters_in_location = await Character.objects.filter(
        current_location=location
    ).acount()
    location_exp = (
        await get_character_property(character, EffectProperty.EXP)
        * location.exp
    )
    exp_in_minute = location_exp / character.exp_for_level_up * 100
    return LOCATION_GET_MESSAGE.format(
        location.name,
        location.attack,
        location.defence,
        f"{characters_in_location}/{location.place}",
        round(exp_in_minute, 2),
        health_reducing,
        await get_location_attack_effect(character, location),
        int(hunting_time),
        await get_location_drop(character, location),
    )


async def check_location_access(character: Character, location: Location):
    """Проверка доступа в локацию."""
    check_data = [
        location.attack / character.attack,
        location.defence / character.defence,
        character.attack / location.attack,
        character.defence / location.defence,
    ]
    if max(check_data) >= game_config.LOCATION_STAT_DIFFERENCE:
        return False, LOCATION_NOT_AVAILABLE.format(
            LOCATION_WEEK_STRONG_MESSAGE
        )
    characters_in_location = await Character.objects.filter(
        current_location=location
    ).acount()
    if characters_in_location >= location.place:
        return False, LOCATION_NOT_AVAILABLE.format(LOCATION_FULL_MESSAGE)
    return True, "Успешно"


async def enter_location(character: Character, location: Location):
    """Вход в локацию."""
    if character.current_location:
        return False, ALREADY_IN_LOCATION_MESSAGE.format(
            character.current_location.name
        )
    success, text = await check_location_access(character, location)
    if not success:
        return False, text
    character.current_location = location
    character.hunting_begin = timezone.now()
    character_defence = await get_character_property(
        character, EffectProperty.DEFENCE
    )
    hunting_time = await get_character_property(
        character, EffectProperty.HUNTING_TIME
    )
    hunting_time *= character_defence / location.defence
    character.hunting_end = timezone.now() + datetime.timedelta(
        minutes=int(hunting_time)
    )
    await character.asave(
        update_fields=("current_location", "hunting_begin", "hunting_end")
    )
    time_left = str(character.hunting_end - character.hunting_begin).split(
        "."
    )[0]
    return True, LOCATION_ENTER_MESSAGE.format(
        location.name,
        time_left,
    )


async def get_hunting_minutes(character: Character):
    """Метод получения минут охоты."""
    hunting_end_time = timezone.now()
    if hunting_end_time > character.hunting_end:
        hunting_end_time = character.hunting_end
    minutes = (hunting_end_time - character.hunting_begin).seconds / 60
    return int(minutes)


async def get_health_reducing(character: Character):
    """Получение снятия хп за минуту в локации."""
    health_reducing = (
        character.current_location.attack
        - await get_character_property(character, EffectProperty.DEFENCE)
    )
    if health_reducing < 0:
        health_reducing = 0
    return health_reducing


async def check_health(character: Character, health_reducing: int):
    """Проверка здоровья персонажа на охоте."""
    await regen_health_or_mana(
        character,
        EffectProperty.HEALTH,
        game_config.HEALTH_REGENERATION_IN_MINUTE,
    )
    potion_used = 0
    if character.auto_use_hp_potion:
        if character.mana <= character.max_health * 0.5:
            exists = await CharacterItem.objects.filter(
                character=character,
                item__effects__property=EffectProperty.HEALTH,
            ).aexists()
            if exists:
                character_item = await CharacterItem.objects.select_related(
                    "item"
                ).aget(
                    character=character,
                    item__effects__property=EffectProperty.HEALTH,
                )
                await use_potion(character, character_item.item)
                potion_used = 1
            else:
                character.auto_use_hp_potion = False
                await character.asave(update_fields=("auto_use_hp_potion",))
    if character.health < health_reducing:
        return False, potion_used
    return True, potion_used


async def check_if_dropped(
    character: Character, drop_buff: float, drop_data: dict
):
    """Проверка выпал ли предмет на охоте."""
    async for drop in LocationDrop.objects.select_related(
        "item", "location"
    ).filter(location=character.current_location):
        if random.uniform(0.01, 100) <= drop.chance * drop_buff:
            amount = random.randint(drop.min_amount, drop.max_amount)
            item, created = await CharacterItem.objects.aget_or_create(
                character=character, item=drop.item
            )
            if drop.item.name_with_type not in drop_data:
                drop_data[drop.item.name_with_type] = 0
            drop_data[drop.item.name_with_type] += amount
            item.amount += amount
            await item.asave(update_fields=("amount",))
    return drop_data


async def use_toggle(character: Character):
    """Проверка на атакующей способности."""
    counter = 0
    potion_used = 0
    if character.auto_use_mp_potion:
        if character.mana < character.max_mana * 0.5:
            exists = await CharacterItem.objects.filter(
                character=character,
                item__effects__property=EffectProperty.MANA,
            ).aexists()
            if exists:
                character_item = await CharacterItem.objects.select_related(
                    "item"
                ).aget(
                    character=character,
                    item__effects__property=EffectProperty.MANA,
                )
                await use_potion(character, character_item.item)
                potion_used = 1
            else:
                character.auto_use_mp_potion = False
                await character.asave(update_fields=("auto_use_mp_potion",))
    async for character_toggle in CharacterSkill.objects.select_related(
        "skill"
    ).filter(character=character, turn_on=True):
        if character.mana < character_toggle.skill.mana_cost:
            continue
        character.mana -= character_toggle.skill.mana_cost
        counter += 1
    return counter, potion_used


async def get_hunting_loot(character: Character, bot):
    """Метод получения трофеев с охоты."""
    hunting_stats = {
        "farm_minutes": 0,
        "relax_minutes": 0,
        "skill_uses": 0,
        "hp_potion_uses": 0,
        "mp_potion_uses": 0,
    }
    hunting_minutes = await get_hunting_minutes(character)
    health_reducing = await get_health_reducing(character)
    drop_modifier = await get_character_property(
        character, EffectProperty.DROP
    )
    max_mana = await get_character_property(character, EffectProperty.MAX_MANA)
    location_exp = (
        character.current_location.exp
        * await get_character_property(character, EffectProperty.EXP)
    )
    exp_gained = 0
    drop_data = {}
    for _minute in range(hunting_minutes):
        enough_health, used_potion = await check_health(
            character, health_reducing
        )
        hunting_stats["hp_potion_uses"] += used_potion
        if not enough_health:
            hunting_stats["relax_minutes"] += 1
            continue
        skill_counter, used_potion = await use_toggle(character)
        hunting_stats["skill_uses"] += skill_counter
        hunting_stats["mp_potion_uses"] += used_potion
        drop_buff = (
            drop_modifier
            * await get_character_property(character, EffectProperty.ATTACK)
            / character.current_location.defence
        )
        exp_gained += location_exp
        drop_data = await check_if_dropped(character, drop_buff, drop_data)
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
    add_info = ""
    if hunting_stats["hp_potion_uses"]:
        add_info += AUTO_USE_HP_TEXT.format(hunting_stats["hp_potion_uses"])
    if hunting_stats["mp_potion_uses"]:
        add_info += AUTO_USE_MP_TEXT.format(hunting_stats["mp_potion_uses"])
    logger.info(
        f"{character.name_with_level} окончил охоту\n"
        "Статистика:\n"
        f"Опыт: {exp_gained}\n"
        f"{hunting_stats}\n"
        f"Трофеи: {drop_text}"
    )
    return HUNTING_END_MESSAGE.format(
        round(exp_gained / character.exp_for_level_up * 100, 2),
        hunting_stats["farm_minutes"],
        hunting_stats["skill_uses"],
        add_info,
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


async def location_get_character_about(character: Character) -> str:
    """Возвращает сообщение с данными о персонаже."""
    clan = "Нет"
    if character.clan:
        clan = character.clan.name_with_emoji
    return LOCATION_CHARACTER_GET_MESSAGE.format(
        character.name_with_class,
        clan,
        "\n".join(
            [
                await get_character_item_with_effects(x)
                async for x in CharacterItem.objects.select_related(
                    "item"
                ).filter(character=character, equipped=True)
            ]
        ),
        await get_elixir_with_effects_and_expired(character),
    )


async def attack_character(
    attacker: Character,
    target: Character,
    bot,
    attacker_message: Message,
    target_message_id: int = 0,
):
    """Обработка атаки на персонажа."""
    attacker_attack = await get_character_property(
        attacker, EffectProperty.ATTACK
    )
    target_defence = await get_character_property(
        target, EffectProperty.DEFENCE
    )
    damage = int(attacker_attack - target_defence)
    if damage < 0:
        damage = 0
    keyboard = await attack_keyboard(
        attacker, attacker_message.message_id, target
    )
    target.health -= damage
    target_telegram_id = await User.objects.values_list(
        "telegram_id", flat=True
    ).aget(character=target)
    target_text = ATTACK_CHARACTER_MESSAGE_TO_TARGET.format(
        attacker.name_with_clan, damage, f"{target.health}/{target.max_health}"
    )
    logger.info(
        f"{attacker.name_with_level} ({attacker.hp} напал на "
        f"{target.name_with_level} ({target.mp}) "
        f"Нанесено: {damage} Урона"
    )
    if not target_message_id:
        target_message = await bot.send_message(
            target_telegram_id,
            text=target_text,
            reply_markup=keyboard.as_markup(),
        )
        target_message_id = target_message.message_id
        logger.info(
            "Отправлено сообщение об атаке персонажу"
            f" {target} id: {target_message_id}"
        )
    else:
        await bot.edit_message_text(
            chat_id=target_telegram_id,
            message_id=target_message_id,
            text=target_text,
            reply_markup=keyboard.as_markup(),
        )
        logger.info(
            "Исправлено сообщение об атаке персонажу "
            f"{target} id: {target_message_id}"
        )
    attacker.pvp_mode_expired = timezone.now() + datetime.timedelta(minutes=2)
    await attacker.asave(update_fields=("pvp_mode_expired",))
    await use_toggle(attacker)
    if target.health <= 0:
        await bot.delete_message(
            message_id=target_message_id,
            chat_id=target_telegram_id,
        )
        await kill_character(target, bot, attacker)
        logger.info(f"Персонаж {target} убит!")
        return (
            False,
            KILL_CHARACTER_MESSAGE_TO_ATTACKER.format(target.name_with_clan),
            damage,
            target_message_id,
        )
    await target.asave(update_fields=("health",))
    return (
        True,
        ATTACK_CHARACTER_MESSAGE.format(damage, 3),
        damage,
        target_message_id,
    )


async def kill_character(
    character: Character, bot, attacker: Character = None
):
    """Убийство персонажа."""
    decrease_exp = game_config.EXP_DECREASE_PERCENT
    attacker_text = KILL_CHARACTER_MESSAGE_TO_ATTACKER.format(
        character.name_with_clan
    )
    attacker.kills += 1
    await attacker.asave(update_fields=("kills",))
    clan_war = await check_clan_war_exists(attacker, character)
    if character.pvp_mode_expired < timezone.now() and not clan_war:
        async for effect in Effect.objects.filter(slug=EffectSlug.FATIGUE):
            fatigue, created = await CharacterEffect.objects.aget_or_create(
                character=attacker,
                effect=effect,
            )
            fatigue.expired += datetime.timedelta(hours=1)
            await fatigue.asave(update_fields=("expired",))
        attacker_text += NO_WAR_KILL_MESSAGE_TO_ATTACKER
    if clan_war:
        decrease_exp = game_config.WAR_EXP_DECREASE_PERCENT
        if character.clan.reputation:
            character.clan.reputation -= 1
            attacker.clan.reputation += 1
            await character.clan.asave(update_fields=("reputation",))
            await attacker.clan.asave(update_fields=("reputation",))
            attacker_text += WAR_KILL_MESSAGE_TO_ATTACKER
        attacker_telegram_id = await User.objects.values_list(
            "telegram_id", flat=True
        ).aget(character=attacker)
        await bot.send_message(attacker_telegram_id, attacker_text)

    character_telegram_id = await User.objects.values_list(
        "telegram_id", flat=True
    ).aget(character=character)
    character.hunting_end = timezone.now()
    text = await get_hunting_loot(character, bot)
    await bot.send_message(
        character_telegram_id,
        text,
    ),
    lost_exp = int(character.exp_for_level_up / 100 * decrease_exp)
    if character.premium_expired > timezone.now():
        lost_exp *= game_config.PREMIUM_DEATH_EXP_MODIFIER
    await remove_exp(character, lost_exp)
    lost_exp = character.exp_for_level_up / lost_exp
    async for character_effect in CharacterEffect.objects.exclude(
        effect__slug=EffectSlug.FATIGUE
    ).filter(
        character=character,
    ):
        await character_effect.adelete()
    await bot.send_message(
        character_telegram_id,
        CHARACTER_KILL_MESSAGE.format(
            attacker.name_with_clan, round(lost_exp, 2)
        ),
    )
