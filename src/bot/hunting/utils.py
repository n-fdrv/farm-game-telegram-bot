import datetime
import random

from character.models import Character, CharacterEffect, CharacterItem
from django.utils import timezone
from item.models import EffectProperty
from location.models import (
    Dungeon,
    HuntingZone,
    HuntingZoneDrop,
    HuntingZoneType,
    Location,
)

from bot.character.utils import (
    get_character_power,
    get_character_property,
    get_exp,
)
from bot.hunting.dungeon.messages import (
    DUNGEON_GET_MESSAGE,
    DUNGEON_HUNTING_END_MESSAGE,
)
from bot.hunting.dungeon.utils import (
    check_dungeon_access,
    get_dungeon_required_items,
)
from bot.hunting.location.messages import (
    HUNTING_ALERT_MESSAGE,
    LOCATION_GET_MESSAGE,
)
from bot.hunting.location.utils import check_location_access
from bot.hunting.messages import (
    ALREADY_IN_ZONE_MESSAGE,
    HUNTING_ZONE_ENTER_MESSAGE,
)
from bot.models import User
from bot.utils.schedulers import remove_scheduler, run_date_job
from core.config.game_config import DROP_RATE, HUNTING_ALERT_HOURS


async def get_hunting_zone_drop(
    character: Character, hunting_zone: [HuntingZone, Location, Dungeon]
) -> str:
    """Получение информации об эффектах защиты локации."""
    drop_modifier = (
        await get_character_property(character, EffectProperty.DROP)
        * DROP_RATE
    )
    drop_data = ""
    async for location_drop in (
        HuntingZoneDrop.objects.select_related("item")
        .filter(hunting_zone=hunting_zone)
        .order_by("-chance")
    ):
        chance = round(location_drop.chance * drop_modifier, 2)
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


async def get_hunting_zone_info(
    character: Character, hunting_zone: [HuntingZone, Location, Dungeon]
) -> str:
    """Возвращает сообщение с данными о персонаже."""
    characters_in_location = await Character.objects.filter(
        current_place=hunting_zone
    ).acount()
    location_exp = (
        await get_character_property(character, EffectProperty.EXP)
        * hunting_zone.exp
    )
    exp_by_kill = round(location_exp / character.exp_for_level_up * 100, 2)
    drop = await get_hunting_zone_drop(character, hunting_zone)
    if hunting_zone.type == HuntingZoneType.LOCATION:
        location = hunting_zone
        if location != Location:
            location = await Location.objects.aget(pk=hunting_zone.pk)
        hunting_speed = (
            await get_character_power(character) / location.required_power
        )
        return LOCATION_GET_MESSAGE.format(
            location.name,
            location.required_power,
            f"{characters_in_location}/{location.place}",
            exp_by_kill,
            round(hunting_speed, 2),
            drop,
        )
    dungeon = hunting_zone
    if dungeon != Dungeon:
        dungeon = await Dungeon.objects.aget(pk=hunting_zone.pk)
    return DUNGEON_GET_MESSAGE.format(
        dungeon.name_with_level,
        await check_dungeon_access(character, dungeon),
        dungeon.hunting_hours,
        exp_by_kill,
        drop,
        await get_dungeon_required_items(dungeon),
    )


async def check_hunting_zone_access(
    character: Character, hunting_zone: [HuntingZone, Location, Dungeon]
):
    """Проверка доступа в локацию."""
    if hunting_zone.type == HuntingZoneType.LOCATION:
        if hunting_zone != Location:
            hunting_zone = await Location.objects.aget(pk=hunting_zone.pk)
        return await check_location_access(character, hunting_zone)


async def enter_hunting_zone(
    character: Character, hunting_zone: [HuntingZone, Location, Dungeon], bot
):
    """Вход в локацию."""
    if character.current_place:
        return False, ALREADY_IN_ZONE_MESSAGE.format(
            character.current_place.name
        )
    success, text = await check_hunting_zone_access(character, hunting_zone)
    if not success:
        return False, text
    character.current_place = hunting_zone
    character.hunting_begin = timezone.now()
    job_time = timezone.now() + datetime.timedelta(hours=HUNTING_ALERT_HOURS)
    if hunting_zone.type == HuntingZoneType.DUNGEON:
        if hunting_zone != Dungeon:
            hunting_zone = Dungeon.objects.aget(pk=hunting_zone.pk)
        job_time = timezone.now() + datetime.timedelta(
            hours=hunting_zone.hunting_time
        )
    job = await run_date_job(
        end_hunting,
        job_time,
        [character, bot],
    )
    character.job_id = job.id
    await character.asave(
        update_fields=("current_place", "hunting_begin", "job_id")
    )
    return True, HUNTING_ZONE_ENTER_MESSAGE.format(
        hunting_zone.name_with_type,
    )


async def exit_hunting_zone(character: Character, bot):
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


async def get_hunting_drop(character: Character, monster_killed: int):
    """Проверка выпал ли предмет на охоте."""
    drop_modifier = (
        await get_character_property(character, EffectProperty.DROP)
        * DROP_RATE
    )
    drop_data = {}
    for _minute in range(int(monster_killed)):
        async for drop in HuntingZoneDrop.objects.select_related(
            "item", "hunting_zone"
        ).filter(hunting_zone=character.current_place):
            if random.uniform(0.01, 100) <= drop.chance * drop_modifier:
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
    drop_text = "\n"
    for name, amount in drop_data.items():
        drop_text += f"<b>{name}</b> - {amount} шт.\n"
    if not drop_data:
        drop_text = "❌"
    return drop_text


async def get_monster_killed_amount(character: Character):
    """Метод получения количества убитых монстров."""
    monster_killed = (timezone.now() - character.hunting_begin).seconds / 60
    if character.current_place.type == HuntingZoneType.LOCATION:
        required_power = await Location.objects.values_list(
            "required_power", flat=True
        ).aget(pk=character.current_place.pk)
        monster_killed *= await get_character_power(character) / required_power
        return monster_killed
    max_hunting_minutes = (
        await Dungeon.objects.values_list("hunting_hours", flat=True).aget(
            pk=character.current_place.pk
        )
        * 60
    )
    if monster_killed > max_hunting_minutes:
        monster_killed = max_hunting_minutes
    return monster_killed


async def get_hunting_loot(character: Character, bot):
    """Метод получения трофеев с охоты."""
    monster_killed = await get_monster_killed_amount(character)
    exp_gained = (
        character.current_place.exp
        * await get_character_property(character, EffectProperty.EXP)
    ) * monster_killed
    drop_text = await get_hunting_drop(character, monster_killed)
    exp_gained = await get_exp(character, exp_gained, bot)
    async for character_effect in CharacterEffect.objects.filter(
        character=character, expired__lte=timezone.now()
    ):
        await character_effect.adelete()
    if character.current_place.type == HuntingZoneType.LOCATION:
        character.hunting_begin = timezone.now()
        job = await run_date_job(
            end_hunting,
            timezone.now() + datetime.timedelta(hours=HUNTING_ALERT_HOURS),
            [character, bot],
        )
        character.job_id = job.id
        await character.asave(
            update_fields=(
                "hunting_begin",
                "job_id",
            )
        )
        return HUNTING_ALERT_MESSAGE.format(
            round(exp_gained / character.exp_for_level_up * 100, 2),
            int(monster_killed),
            drop_text,
        )
    await remove_scheduler(character.job_id)
    character.current_place = None
    character.hunting_begin = None
    character.job_id = None
    await character.asave(
        update_fields=(
            "current_place",
            "hunting_begin",
            "job_id",
        )
    )
    return DUNGEON_HUNTING_END_MESSAGE.format(
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
            timezone.now() + datetime.timedelta(hours=HUNTING_ALERT_HOURS),
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
