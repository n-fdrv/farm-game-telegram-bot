import datetime
import random

from character.models import (
    Character,
)
from django.utils import timezone
from item.models import EffectProperty
from location.models import (
    Location,
    LocationBoss,
    LocationBossDrop,
)

from bot.character.utils import (
    get_character_power,
    get_character_property,
)
from bot.hunting.location.keyboards import (
    alert_about_location_boss_respawn_keyboard,
)
from bot.hunting.location.messages import (
    ALERT_ABOUT_BOSS_RESPAWN_MESSAGE,
    GET_LOCATION_BOSS_MESSAGE,
    LOCATION_FULL_MESSAGE,
    LOCATION_NOT_AVAILABLE,
    LOCATION_WEEK_STRONG_MESSAGE,
    NOT_ENOUGH_POWER_MESSAGE,
    SUCCESS_ACCEPT_BOSS_MESSAGE,
    SUCCESS_BOSS_KILLED_MESSAGE,
)
from bot.models import User
from bot.utils.game_utils import add_item
from bot.utils.messages import ALREADY_KILLED_MESSAGE
from bot.utils.schedulers import run_date_job
from core.config import game_config


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
