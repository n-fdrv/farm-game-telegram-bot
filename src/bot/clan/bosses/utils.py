import datetime
import random

from character.models import Character
from clan.models import Clan, ClanBoss, ClanBossClan, ClanBossDrop
from django.utils import timezone
from item.models import EffectProperty

from bot.character.utils import get_character_property
from bot.clan.bosses.keyboards import alert_about_clan_boss_respawn_keyboard
from bot.clan.bosses.messages import (
    ALERT_ABOUT_CLAN_BOSS_RESPAWN_MESSAGE,
    ALREADY_KILLED_CLAN_BOSS_MESSAGE,
    GET_CLAN_BOSS_MESSAGE,
    NO_BOSS_KILLED_MESSAGE,
    SUCCESS_ACCEPT_CLAN_RAID_MESSAGE,
    SUCCESS_BOSS_KILLED_MESSAGE,
)
from bot.clan.warehouse.utils import add_clan_item
from bot.models import User
from bot.utils.schedulers import run_date_job
from core.config import game_config


async def get_clan_boss_drop(boss: ClanBoss):
    """Получение информации о дропе с кланового босса."""
    drop_data = ""
    async for location_drop in (
        ClanBossDrop.objects.select_related("item")
        .filter(clan_boss=boss)
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


async def get_clan_boss_info(boss: ClanBoss, clan: Clan) -> str:
    """Получение информации о боссе."""
    participating = "❌Не участвует!"
    if await ClanBossClan.objects.filter(clan=clan).aexists():
        participating = "✅Участвует"
    return GET_CLAN_BOSS_MESSAGE.format(
        boss.name_with_power, participating, await get_clan_boss_drop(boss)
    )


async def accept_decline_clan_boss_hunting(boss: ClanBoss, clan: Clan):
    """Включение и отключение охоты на босса."""
    if await ClanBossClan.objects.filter(clan=clan).aexists():
        await ClanBossClan.objects.filter(clan=clan).adelete()
    else:
        await boss.clans.aadd(clan)


async def make_schedulers_after_restart(bot):
    """Создание шедулеров на оповещения после рестарта сервера."""
    async for boss in ClanBoss.objects.filter(respawn__gt=timezone.now()):
        await run_date_job(
            alert_about_clan_boss_respawn, boss.respawn, [boss, bot]
        )


async def alert_about_clan_boss_respawn(boss: ClanBoss, bot):
    """Оповещение клана о респауне босса."""
    keyboard = await alert_about_clan_boss_respawn_keyboard(boss)
    async for character in Character.objects.filter(clan__in=boss.clans.all()):
        telegram_id = await User.objects.values_list(
            "telegram_id", flat=True
        ).aget(character=character)
        await bot.send_message(
            chat_id=telegram_id,
            text=ALERT_ABOUT_CLAN_BOSS_RESPAWN_MESSAGE.format(boss.name),
            reply_markup=keyboard.as_markup(),
        )
    await run_date_job(
        kill_clan_boss,
        timezone.now()
        + datetime.timedelta(minutes=game_config.MINUTES_FOR_ENTER_CLAN_RAID),
        [boss, bot],
    )


async def accept_clan_boss_raid(boss: ClanBoss, character: Character):
    """Подтверждение рейда персонажем."""
    if boss.respawn > timezone.now():
        return False, ALREADY_KILLED_CLAN_BOSS_MESSAGE.format(boss.name)
    await boss.characters.aadd(character)
    return True, SUCCESS_ACCEPT_CLAN_RAID_MESSAGE.format(boss.name)


async def kill_clan_boss(boss: ClanBoss, bot):
    """Убийство босса и распределение дропа."""
    boss.respawn = timezone.now() + datetime.timedelta(
        hours=random.randint(24, 36),
        minutes=random.randint(0, 59),
        seconds=random.randint(1, 59),
    )
    await boss.asave(update_fields=("respawn",))
    raid_power = sum(
        [
            sum(
                (
                    await get_character_property(x, EffectProperty.ATTACK),
                    await get_character_property(x, EffectProperty.DEFENCE),
                )
            )
            async for x in boss.characters.all()
        ]
    )
    if raid_power < boss.required_power:
        async for character in Character.objects.select_related("clan").filter(
            clan__in=boss.clans.all()
        ):
            telegram_id = await User.objects.values_list(
                "telegram_id", flat=True
            ).aget(character=character)
            await bot.send_message(
                chat_id=telegram_id,
                text=NO_BOSS_KILLED_MESSAGE.format(boss.name),
            )
        return False
    clan_chances_data = []
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
    async for drop in ClanBossDrop.objects.select_related("item").filter(
        clan_boss=boss
    ):
        if random.uniform(0.01, 100) <= drop.chance:
            amount = random.randint(
                drop.min_amount,
                drop.max_amount,
            )
            await add_clan_item(
                clan=winner.clan,
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
    winner_characters = ", ".join(
        [x.name async for x in boss.characters.filter(clan=winner.clan)]
    )
    async for character in Character.objects.select_related("clan").filter(
        clan__in=boss.clans.all()
    ):
        telegram_id = await User.objects.values_list(
            "telegram_id", flat=True
        ).aget(character=character)
        await bot.send_message(
            chat_id=telegram_id,
            text=SUCCESS_BOSS_KILLED_MESSAGE.format(
                boss.name,
                winner.clan.name_with_emoji,
                winner_characters,
                drop_text,
            ),
        )
    await boss.characters.aclear()
