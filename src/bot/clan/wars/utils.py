from character.models import Character
from clan.models import Clan, ClanWar
from django.db.models import Q

from bot.clan.wars.messages import (
    ALERT_END_WAR_MESSAGE,
    ALERT_NEW_WAR_MESSAGE,
    NOT_ENOUGH_REPUTATION_MESSAGE,
    SUCCESS_ENDING_WAR_MESSAGE,
)
from bot.models import User
from bot.utils.schedulers import send_message_to_user
from core.config import game_config


async def accept_war(clan_war: ClanWar):
    """Принять войну кланов."""
    clan_war.accepted = True
    await clan_war.asave(update_fields=("accepted",))
    async for character in Character.objects.filter(
        Q(clan=clan_war.clan) | Q(clan=clan_war.enemy)
    ):
        telegram_id = await User.objects.values_list(
            "telegram_id", flat=True
        ).aget(character=character)
        await send_message_to_user(
            telegram_id,
            ALERT_NEW_WAR_MESSAGE.format(
                clan_war.clan.name_with_emoji, clan_war.enemy.name_with_emoji
            ),
        )


async def end_war(surrender_clan: Clan, clan_war: ClanWar):
    """Окончить войну кланов."""
    if surrender_clan.reputation < game_config.WAR_END_REPUTATION_COST:
        return False, NOT_ENOUGH_REPUTATION_MESSAGE
    surrender_clan.reputation -= game_config.WAR_END_REPUTATION_COST
    await surrender_clan.asave(update_fields=("reputation",))
    winner = clan_war.enemy
    if winner == surrender_clan:
        winner = clan_war.clan
    winner.reputation += game_config.WAR_END_REPUTATION_COST
    await winner.asave(update_fields=("reputation",))
    async for character in Character.objects.filter(
        Q(clan=clan_war.clan) | Q(clan=clan_war.enemy)
    ):
        telegram_id = await User.objects.values_list(
            "telegram_id", flat=True
        ).aget(character=character)
        await send_message_to_user(
            telegram_id,
            ALERT_END_WAR_MESSAGE.format(
                surrender_clan.name_with_emoji, winner.name_with_emoji
            ),
        )
    await clan_war.adelete()
    return True, SUCCESS_ENDING_WAR_MESSAGE.format(winner)
