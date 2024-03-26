import re

from character.models import Character
from clan.models import Clan, ClanRequest
from item.models import EffectProperty

from bot.character.utils import get_character_property
from bot.clan.messages import (
    CREATE_REQUEST_MESSAGE_TO_LEADER,
    ERROR_IN_CREATING_REQUEST_MESSAGE,
    GET_CLAN_MESSAGE,
    SUCCESS_CREATING_REQUEST_MESSAGE,
)
from bot.models import User
from bot.utils.schedulers import send_message_to_user


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
            sum(
                (
                    await get_character_property(x, EffectProperty.ATTACK),
                    await get_character_property(x, EffectProperty.DEFENCE),
                )
            )
            async for x in Character.objects.filter(clan=clan)
        ]
    )


async def get_clan_info(clan: Clan) -> str:
    """Получение информации о клане."""
    clan_members_amount = await Character.objects.filter(clan=clan).acount()
    await get_clan_power(clan)
    return GET_CLAN_MESSAGE.format(
        clan.name_with_emoji,
        clan.level,
        await get_clan_power(clan),
        clan.leader.name_with_class,
        clan.description,
        clan_members_amount,
        clan.place,
        clan.reputation,
    )


async def create_request(character: Character, clan: Clan):
    """Создание заявки в клан."""
    if character.clan:
        return False, ERROR_IN_CREATING_REQUEST_MESSAGE
    await ClanRequest.objects.filter(character=character).adelete()
    await ClanRequest.objects.acreate(character=character, clan=clan)
    leader_user = await User.objects.aget(character=clan.leader)
    await send_message_to_user(
        leader_user.telegram_id,
        CREATE_REQUEST_MESSAGE_TO_LEADER.format(character.name_with_class),
    )
    return True, SUCCESS_CREATING_REQUEST_MESSAGE
