import re

from character.models import Character
from clan.models import Clan, ClanRequest

from bot.character.utils import get_character_power
from bot.clan.messages import (
    ERROR_IN_ENTER_CLAN_MESSAGE,
    GET_CLAN_MESSAGE,
    SUCCESS_ENTER_CLAN_MESSAGE,
)
from bot.clan.requests.messages import NO_PLACE_IN_CLAN_MESSAGE


async def check_clan_name_exist(name: str) -> bool:
    """Проверка занято ли имя клана."""
    return await Clan.objects.filter(name=name).aexists()


def check_clan_name_correct(nickname: str) -> bool:
    """Валидатор проверки корректности ввода имени клана."""
    if not re.search("^[А-Яа-яA-Za-z0-9]{1,16}$", nickname):
        return False
    return True


async def get_clan_power(clan: Clan) -> int:
    """Получение силы клана."""
    return sum(
        [
            await get_character_power(x)
            async for x in Character.objects.filter(clan=clan)
        ]
    )


async def get_clan_info(clan: Clan) -> str:
    """Получение информации о клане."""
    clan_members_amount = await Character.objects.filter(clan=clan).acount()
    access = "🔓Открытый"
    if clan.by_request:
        access = "🔒По заявкам"
    await get_clan_power(clan)
    return GET_CLAN_MESSAGE.format(
        clan.name_with_emoji,
        clan.level,
        int(await get_clan_power(clan)),
        clan.clan_leader,
        clan.description,
        clan_members_amount,
        clan.place,
        access,
        clan.reputation,
    )


async def enter_clan(character: Character, clan: Clan):
    """Вход в клан."""
    if character.clan or clan.by_request:
        return False, ERROR_IN_ENTER_CLAN_MESSAGE
    characters_in_clan = await Character.objects.filter(clan=clan).acount()
    if clan.place <= characters_in_clan:
        return False, NO_PLACE_IN_CLAN_MESSAGE
    await ClanRequest.objects.filter(character=character).adelete()
    character.clan = clan
    await character.asave(update_fields=("clan",))
    return True, SUCCESS_ENTER_CLAN_MESSAGE.format(clan.name_with_emoji)
