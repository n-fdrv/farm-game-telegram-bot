import datetime

from aiogram.types import Message
from character.models import Character, CharacterEffect
from django.utils import timezone
from item.models import Effect, EffectProperty, EffectSlug
from loguru import logger

from bot.character.skills.utils import use_toggle
from bot.character.utils import (
    check_clan_war_exists,
    get_character_property,
    remove_exp,
)
from bot.hunting.utils import exit_hunting_zone
from bot.models import User
from bot.pvp.keyboards import attack_keyboard
from bot.pvp.messages import (
    ATTACK_CHARACTER_MESSAGE,
    ATTACK_CHARACTER_MESSAGE_TO_TARGET,
    CHARACTER_KILL_MESSAGE,
    KILL_CHARACTER_MESSAGE_TO_ATTACKER,
    NO_WAR_KILL_MESSAGE_TO_ATTACKER,
    WAR_KILL_MESSAGE_TO_ATTACKER,
)
from core.config.game_config import (
    EXP_DECREASE_PERCENT,
    PREMIUM_DEATH_EXP_MODIFIER,
    WAR_EXP_DECREASE_PERCENT,
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
    attacker.pvp_mode_expired = timezone.now() + datetime.timedelta(minutes=2)
    await attacker.asave(update_fields=("pvp_mode_expired",))
    await use_toggle(attacker)
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
