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
from location.models import (
    Dungeon,
    DungeonCharacter,
    DungeonRequiredItem,
    HuntingZoneDrop,
    Location,
    LocationBoss,
    LocationBossDrop,
)
from loguru import logger

from bot.character.backpack.utils import use_potion
from bot.character.utils import (
    check_clan_war_exists,
    get_character_item_with_effects,
    get_character_power,
    get_character_property,
    get_elixir_with_effects_and_expired,
    get_exp,
    remove_exp,
)
from bot.location.dungeon.messages import DUNGEON_GET_MESSAGE
from bot.location.keyboards import (
    alert_about_location_boss_respawn_keyboard,
    attack_keyboard,
)
from bot.location.messages import (
    ALERT_ABOUT_BOSS_RESPAWN_MESSAGE,
    ALREADY_IN_LOCATION_MESSAGE,
    ATTACK_CHARACTER_MESSAGE,
    ATTACK_CHARACTER_MESSAGE_TO_TARGET,
    CHARACTER_KILL_MESSAGE,
    GET_LOCATION_BOSS_MESSAGE,
    HUNTING_END_MESSAGE,
    KILL_CHARACTER_MESSAGE_TO_ATTACKER,
    LOCATION_CHARACTER_GET_MESSAGE,
    LOCATION_ENTER_MESSAGE,
    LOCATION_FULL_MESSAGE,
    LOCATION_NOT_AVAILABLE,
    LOCATION_WEEK_STRONG_MESSAGE,
    NO_WAR_KILL_MESSAGE_TO_ATTACKER,
    NOT_ENOUGH_POWER_MESSAGE,
    SUCCESS_ACCEPT_BOSS_MESSAGE,
    SUCCESS_BOSS_KILLED_MESSAGE,
    WAR_KILL_MESSAGE_TO_ATTACKER,
)
from bot.models import User
from bot.utils.game_utils import add_item, get_expired_text
from bot.utils.messages import ALREADY_KILLED_MESSAGE
from bot.utils.schedulers import remove_scheduler, run_date_job
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


async def get_dungeon_required_items(dungeon: Dungeon) -> str:
    """Получение информации об эффектах защиты локации."""
    items_data = ""
    async for required_item in (
        DungeonRequiredItem.objects.select_related("item")
        .filter(dungeon=dungeon)
        .order_by("-amount")
    ):
        items_data += (
            f"<b>{required_item.item.name_with_type}</b> - "
            f"<i>{required_item.amount} шт.</i>\n"
        )
    return items_data


async def get_dungeon_drop(character: Character, dungeon: Dungeon) -> str:
    """Получение информации об эффектах защиты локации."""
    drop_modifier = (
        await get_character_property(character, EffectProperty.DROP)
        * game_config.DROP_RATE
    )
    drop_data = ""
    async for dungeon_drop in (
        HuntingZoneDrop.objects.select_related("item")
        .filter(hunting_zone=dungeon)
        .order_by("-chance")
    ):
        chance = round(dungeon_drop.chance * drop_modifier, 2)
        chance_limit = 100
        if chance > chance_limit:
            chance = chance_limit
        amount = ""
        if dungeon_drop.max_amount > 1:
            amount = f"({dungeon_drop.min_amount}-{dungeon_drop.max_amount}) "
        drop_data += (
            f"<b>{dungeon_drop.item.name_with_type}</b> "
            f"<i>{amount}- {chance}%</i>\n"
        )
    return drop_data


async def check_dungeon_access(character: Character, dungeon: Dungeon):
    """Проверка доступности подземелья."""
    dungeon_character, created = await DungeonCharacter.objects.aget_or_create(
        character=character, dungeon=dungeon
    )
    if (
        created
        or dungeon_character.hunting_begin
        < timezone.now() - datetime.timedelta(hours=dungeon.cooldown_hours)
    ):
        return "Доступно"
    time_left = (
        dungeon_character.hunting_begin
        + datetime.timedelta(hours=dungeon.cooldown_hours)
        - timezone.now()
    )
    return await get_expired_text(time_left)


async def get_dungeon_info(character: Character, dungeon: Dungeon) -> str:
    """Возвращает сообщение с данными о персонаже."""
    location_exp = (
        await get_character_property(character, EffectProperty.EXP)
        * dungeon.exp
    )
    exp_by_kill = location_exp / character.exp_for_level_up * 100
    return DUNGEON_GET_MESSAGE.format(
        dungeon.name_with_level,
        await check_dungeon_access(character, dungeon),
        dungeon.hunting_hours,
        round(exp_by_kill, 2),
        await get_dungeon_drop(character, dungeon),
        await get_dungeon_required_items(dungeon),
    )


async def check_location_access(character: Character, location: Location):
    """Проверка доступа в локацию."""
    character_power = await get_character_power(character)
    check_data = [
        location.required_power / character_power,
        character_power / location.required_power,
    ]
    if max(check_data) >= game_config.LOCATION_STAT_DIFFERENCE:
        return False, LOCATION_NOT_AVAILABLE.format(
            LOCATION_WEEK_STRONG_MESSAGE
        )
    characters_in_location = await Character.objects.filter(
        current_place=location
    ).acount()
    if characters_in_location >= location.place:
        return False, LOCATION_NOT_AVAILABLE.format(LOCATION_FULL_MESSAGE)
    return True, "Успешно"


async def enter_location(character: Character, location: Location, bot):
    """Вход в локацию."""
    if character.current_place:
        return False, ALREADY_IN_LOCATION_MESSAGE.format(
            character.current_place.name
        )
    success, text = await check_location_access(character, location)
    if not success:
        return False, text
    character.current_place = location
    character.hunting_begin = timezone.now()
    job = await run_date_job(
        end_hunting,
        timezone.now()
        + datetime.timedelta(hours=game_config.HUNTING_ALERT_HOURS),
        [character, bot],
    )
    character.job_id = job.id
    await character.asave(
        update_fields=("current_place", "hunting_begin", "job_id")
    )
    return True, LOCATION_ENTER_MESSAGE.format(
        location.name,
    )


async def exit_location(character: Character, bot):
    """Выход из локации."""
    await remove_scheduler(character.job_id)
    text = await get_hunting_loot(character, bot)
    await remove_scheduler(character.job_id)
    character.hunting_begin = None
    character.current_place = None
    character.job_id = None
    await character.asave(
        update_fields=("hunting_begin", "current_place", "job_id")
    )
    return text


async def check_if_dropped(
    character: Character, drop_buff: float, drop_data: dict
):
    """Проверка выпал ли предмет на охоте."""
    async for drop in HuntingZoneDrop.objects.select_related(
        "item", "location"
    ).filter(hunting_zone=character.current_place):
        if random.uniform(0.01, 100) <= drop.chance * drop_buff:
            amount = random.randint(
                drop.min_amount,
                drop.max_amount,
            )
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
    monster_killed = (timezone.now() - character.hunting_begin).seconds / 60
    monster_killed *= (
        await get_character_power(character)
        / character.current_place.required_power
    )
    drop_modifier = (
        await get_character_property(character, EffectProperty.DROP)
        * game_config.DROP_RATE
    )
    exp_gained = (
        character.current_place.exp
        * await get_character_property(character, EffectProperty.EXP)
    ) * monster_killed
    drop_data = {}
    for _minute in range(int(monster_killed)):
        drop_data = await check_if_dropped(character, drop_modifier, drop_data)
    exp_gained = await get_exp(character, exp_gained, bot)
    character.hunting_begin = timezone.now()
    async for character_effect in CharacterEffect.objects.filter(
        character=character, expired__lte=timezone.now()
    ):
        await character_effect.adelete()
    drop_text = "\n"
    for name, amount in drop_data.items():
        drop_text += f"<b>{name}</b> - {amount} шт.\n"
    if not drop_data:
        drop_text = "❌"
    job = await run_date_job(
        end_hunting,
        timezone.now()
        + datetime.timedelta(hours=game_config.HUNTING_ALERT_HOURS),
        [character, bot],
    )
    character.job_id = job.id
    await character.asave(
        update_fields=(
            "hunting_begin",
            "job_id",
        )
    )
    return HUNTING_END_MESSAGE.format(
        round(exp_gained / character.exp_for_level_up * 100, 2),
        int(monster_killed),
        drop_text,
    )


async def make_hunting_end_schedulers_after_restart(bot):
    """Создание шедулеров на оповещения после рестарта сервера."""
    async for character in Character.objects.select_related(
        "current_place"
    ).exclude(current_place=None):
        await run_date_job(
            end_hunting,
            timezone.now()
            + datetime.timedelta(hours=game_config.HUNTING_ALERT_HOURS),
            [character, bot],
        )


async def end_hunting(character: Character, bot):
    """Конец охоты по времени."""
    text = await get_hunting_loot(character, bot)
    user = await User.objects.aget(character=character)
    await bot.send_message(
        user.telegram_id,
        text,
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
    character_telegram_id = await User.objects.values_list(
        "telegram_id", flat=True
    ).aget(character=character)
    text = await exit_location(character, bot)
    await bot.send_message(
        character_telegram_id,
        text,
    ),
    lost_exp = int(character.exp_for_level_up / 100 * decrease_exp)
    if character.premium_expired > timezone.now():
        lost_exp *= game_config.PREMIUM_DEATH_EXP_MODIFIER
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


async def get_location_boss_drop(boss: LocationBoss):
    """Получение информации о дропе с босса."""
    drop_data = ""
    async for location_drop in (
        LocationBossDrop.objects.select_related("item")
        .filter(boss=boss)
        .order_by("-chance")
    ):
        chance = round(location_drop.chance, 2)
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


async def get_location_boss_info(boss: LocationBoss) -> str:
    """Получение информации о боссе."""
    return GET_LOCATION_BOSS_MESSAGE.format(
        boss.name_with_power, await get_location_boss_drop(boss)
    )


async def make_location_bosses_schedulers_after_restart(bot):
    """Создание шедулеров на оповещения после рестарта сервера."""
    async for boss in LocationBoss.objects.select_related("location").all():
        if boss.respawn < timezone.now():
            boss.respawn = timezone.now() + datetime.timedelta(
                hours=random.randint(
                    game_config.RESPAWN_HOURS_LOCATION_BOSS - 3,
                    game_config.RESPAWN_HOURS_LOCATION_BOSS + 3,
                ),
                minutes=random.randint(1, 59),
                seconds=random.randint(1, 59),
            )
            await boss.asave(update_fields=("respawn",))
        await run_date_job(
            alert_about_location_boss_respawn, boss.respawn, [boss, bot]
        )


async def alert_about_location_boss_respawn(boss: LocationBoss, bot):
    """Оповещение клана о респауне босса."""
    keyboard = await alert_about_location_boss_respawn_keyboard(boss)
    async for character in Character.objects.filter(
        current_place=boss.location
    ):
        telegram_id = await User.objects.values_list(
            "telegram_id", flat=True
        ).aget(character=character)
        await bot.send_message(
            chat_id=telegram_id,
            text=ALERT_ABOUT_BOSS_RESPAWN_MESSAGE.format(boss.name),
            reply_markup=keyboard.as_markup(),
        )
    await run_date_job(
        kill_location_boss,
        timezone.now()
        + datetime.timedelta(minutes=game_config.MINUTES_FOR_ENTER_CLAN_RAID),
        [boss, bot],
    )


async def accept_location_boss_raid(boss: LocationBoss, character: Character):
    """Подтверждение рейда персонажем."""
    if boss.respawn > timezone.now():
        return False, ALREADY_KILLED_MESSAGE.format(boss.name)
    character_power = await get_character_property(
        character, EffectProperty.ATTACK
    )
    character_power += await get_character_property(
        character, EffectProperty.DEFENCE
    )
    if character_power < boss.required_power:
        return False, NOT_ENOUGH_POWER_MESSAGE.format(boss.name)
    await boss.characters.aadd(character)
    return True, SUCCESS_ACCEPT_BOSS_MESSAGE.format(boss.name)


async def kill_location_boss(boss: LocationBoss, bot):
    """Убийство босса и распределение дропа."""
    boss.respawn = timezone.now() + datetime.timedelta(
        hours=random.randint(
            game_config.RESPAWN_HOURS_LOCATION_BOSS - 3,
            game_config.RESPAWN_HOURS_LOCATION_BOSS + 3,
        ),
        minutes=random.randint(1, 59),
        seconds=random.randint(1, 59),
    )
    await boss.asave(update_fields=("respawn",))
    clan_chances_data = []
    if not await boss.characters.aexists():
        return False
    async for character in boss.characters.all():
        clan_chances_data.extend(
            [character.pk]
            * sum(
                (
                    int(
                        await get_character_property(
                            character, EffectProperty.ATTACK
                        )
                    ),
                    int(
                        await get_character_property(
                            character, EffectProperty.DEFENCE
                        )
                    ),
                )
            )
        )
    winner = await Character.objects.select_related("clan").aget(
        pk=random.choices(clan_chances_data)[0]
    )
    drop_data = {}
    async for drop in LocationBossDrop.objects.select_related("item").filter(
        boss=boss
    ):
        if random.uniform(0.01, 100) <= drop.chance:
            amount = random.randint(
                drop.min_amount,
                drop.max_amount,
            )
            await add_item(
                character=winner,
                item=drop.item,
                amount=amount,
            )
            if drop.item.name_with_type not in drop_data:
                drop_data[drop.item.name_with_type] = 0
            drop_data[drop.item.name_with_type] += amount
    drop_text = "\n"
    for name, amount in drop_data.items():
        drop_text += f"<b>{name}</b> - {amount} шт.\n"
    if not drop_data:
        drop_text = "❌"
    async for character in boss.characters.all():
        telegram_id = await User.objects.values_list(
            "telegram_id", flat=True
        ).aget(character=character)
        await bot.send_message(
            chat_id=telegram_id,
            text=SUCCESS_BOSS_KILLED_MESSAGE.format(
                boss.name,
                winner.name_with_clan,
                drop_text,
            ),
        )
    await boss.characters.aclear()
