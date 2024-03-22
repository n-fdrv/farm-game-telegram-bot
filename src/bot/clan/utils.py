import re

from character.models import Character
from clan.models import Clan

from bot.clan.messages import GET_CLAN_MESSAGE


async def check_clan_name_exist(name: str) -> bool:
    """Проверка занято ли имя клана."""
    return await Clan.objects.filter(name=name).aexists()


def check_clan_name_correct(nickname: str) -> bool:
    """Валидатор проверки корректности ввода имени клана."""
    if not re.search("^[А-Яа-яA-Za-z0-9]{1,16}$", nickname):
        return False
    return True


async def get_clan_info(clan: Clan) -> str:
    """Получение информации о клане."""
    clan_members_amount = await Character.objects.filter(clan=clan).acount()
    return GET_CLAN_MESSAGE.format(
        clan.name_with_emoji,
        clan.level,
        clan.leader.name_with_class,
        clan_members_amount,
        clan.place,
        clan.reputation,
    )
