import datetime
import random

from aiogram.types import Message
from character.models import Character, CharacterEffect, CharacterItem
from clan.models import ClanWar
from django.db.models import Q
from django.utils import timezone
from item.models import Effect, EffectProperty, EffectSlug
from loguru import logger

from bot.character.backpack.utils import use_potion
from bot.character.skills.utils import use_toggle
from bot.character.utils import (
    get_character_item_with_effects,
    get_character_property,
    get_elixir_with_effects_and_expired,
    remove_exp,
)
from bot.hunting.utils import exit_hunting_zone
from bot.models import User
from bot.pvp.keyboards import attack_keyboard
from bot.pvp.messages import (
    ATTACK_CHARACTER_MESSAGE,
    ATTACK_CHARACTER_MESSAGE_TO_TARGET,
    CHARACTER_KILL_MESSAGE,
    CRITICAL_DAMAGE_INFO,
    DAMAGE_INFO,
    KILL_CHARACTER_MESSAGE_TO_ATTACKER,
    NO_WAR_KILL_MESSAGE_TO_ATTACKER,
    NOT_SUCCESS_ATTACK_INFO,
    PVP_CHARACTER_GET_MESSAGE,
    WAR_KILL_MESSAGE_TO_ATTACKER,
)
from core.config.game_config import (
    EVASION_CHANCE_BY_POINT,
    EXP_DECREASE_PERCENT,
    PREMIUM_DEATH_EXP_MODIFIER,
    WAR_EXP_DECREASE_PERCENT,
)


async def pvp_get_character_about(character: Character) -> str:
    """Возвращает сообщение с данными о персонаже."""
    clan = "Нет"
    if character.clan:
        clan = character.clan.name_with_emoji
    return PVP_CHARACTER_GET_MESSAGE.format(
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


async def check_clan_war_exists(attacker: Character, enemy: Character):
    """Проверка есть ли война между персонажами."""
    if attacker.clan and enemy.clan:
        return await ClanWar.objects.filter(
            Q(clan=attacker.clan, enemy=enemy.clan, accepted=True)
            | Q(enemy=attacker.clan, clan=enemy.clan, accepted=True)
        ).aexists()
    return False


async def check_attack_accuracy(attacker: Character, target: Character):
    """Проверка попадания атаки в цель."""
    attacker_accuracy = await get_character_property(
        attacker, EffectProperty.ACCURACY
    )
    target_evasion = await get_character_property(
        target, EffectProperty.EVASION
    )
    evasion_chance = target_evasion - attacker_accuracy
    if evasion_chance <= 0:
        return True
    evasion_chance *= EVASION_CHANCE_BY_POINT
    evasion_success = random.randint(1, 100)
    if evasion_success <= evasion_chance:
        return False
    return True


async def get_damage_amount(attacker: Character, target: Character):
    """Метод получения количества урона."""
    if not await check_attack_accuracy(attacker, target):
        return 0, NOT_SUCCESS_ATTACK_INFO.format(target.name_with_clan)
    attacker_attack = await get_character_property(
        attacker, EffectProperty.ATTACK
    )
    target_defence = await get_character_property(
        target, EffectProperty.DEFENCE
    )
    damage = attacker_attack - target_defence
    if damage < 0:
        return 0, DAMAGE_INFO.format(0)
    crit_success = random.randint(1, 1000)
    if crit_success <= attacker.crit_rate:
        damage += damage / 100 * attacker.crit_power
        return int(damage), CRITICAL_DAMAGE_INFO.format(int(damage))
    return int(damage), DAMAGE_INFO.format(int(damage))


async def attack_character(
    attacker: Character,
    target: Character,
    bot,
    attacker_message: Message,
    target_message_id: int = 0,
):
    """Обработка атаки на персонажа."""
    attacker.pvp_mode_expired = timezone.now() + datetime.timedelta(minutes=2)
    await attacker.asave(update_fields=("pvp_mode_expired",))
    await use_toggle(attacker)
    damage, damage_text = await get_damage_amount(attacker, target)
    keyboard = await attack_keyboard(attacker_message.message_id, target)
    target.health -= damage
    target_telegram_id = await User.objects.values_list(
        "telegram_id", flat=True
    ).aget(character=target)
    target_max_health = await get_character_property(
        target, EffectProperty.MAX_HEALTH
    )
    exists = await CharacterItem.objects.filter(
        character=target,
        item__effects__property=EffectProperty.HEALTH,
    ).aexists()
    target_add_info = ""
    if target.health < target_max_health * 0.5 and exists:
        character_item = await CharacterItem.objects.select_related(
            "item"
        ).aget(
            character=target,
            item__effects__property=EffectProperty.MANA,
        )
        await use_potion(target, character_item.item)
        target_add_info = "Использовано Зелье Здоровья"
    target_text = ATTACK_CHARACTER_MESSAGE_TO_TARGET.format(
        attacker.name_with_clan,
        damage,
        f"{target.health}/{target_max_health}",
        target_add_info,
    )
    logger.info(
        f"{attacker.name_with_level} ({attacker.hp} напал на "
        f"{target.name_with_level} ({target.hp}) "
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
    if target.health <= 0:
        await bot.delete_message(
            message_id=target_message_id,
            chat_id=target_telegram_id,
        )
        text = await kill_character(target, bot, attacker)
        logger.info(f"Персонаж {target} убит!")
        return (
            False,
            text,
            damage_text,
            target_message_id,
        )
    await target.asave(update_fields=("health",))
    return (
        True,
        ATTACK_CHARACTER_MESSAGE.format(target.name_with_clan, damage_text, 3),
        damage_text,
        target_message_id,
    )


async def kill_character(
    character: Character, bot, attacker: Character = None
):
    """Убийство персонажа."""
    decrease_exp = EXP_DECREASE_PERCENT
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
        decrease_exp = WAR_EXP_DECREASE_PERCENT
        if character.clan.reputation:
            character.clan.reputation -= 1
            attacker.clan.reputation += 1
            await character.clan.asave(update_fields=("reputation",))
            await attacker.clan.asave(update_fields=("reputation",))
            attacker_text += WAR_KILL_MESSAGE_TO_ATTACKER
    character_telegram_id = await User.objects.values_list(
        "telegram_id", flat=True
    ).aget(character=character)
    text = await exit_hunting_zone(character, bot)
    await bot.send_message(
        character_telegram_id,
        text,
    ),
    lost_exp = int(character.exp_for_level_up / 100 * decrease_exp)
    if character.premium_expired > timezone.now():
        lost_exp *= PREMIUM_DEATH_EXP_MODIFIER
    await remove_exp(character, lost_exp)
    character.health = character.max_health // 2
    await character.asave(update_fields=("health",))
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
    return attacker_text
