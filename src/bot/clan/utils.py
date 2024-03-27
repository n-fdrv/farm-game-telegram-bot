import re

from character.models import Character
from clan.models import Clan, ClanRequest
from item.models import EffectProperty

from bot.character.utils import get_character_property
from bot.clan.messages import (
    ERROR_IN_ENTER_CLAN_MESSAGE,
    ERROR_IN_KICK_MEMBER_MESSAGE,
    GET_CLAN_MESSAGE,
    SUCCESS_ENTER_CLAN_MESSAGE,
    SUCCESS_KICKING_MEMBER_MESSAGE,
    SUCCESS_KICKING_MEMBER_MESSAGE_TO_USER,
)
from bot.clan.requests.messages import NO_PLACE_IN_CLAN_MESSAGE
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


async def kick_member(character: Character, clan: Clan):
    """Кик персонажа из клана."""
    if (
        character.clan != clan
        or not character.clan
        or clan.leader == character
    ):
        return False, ERROR_IN_KICK_MEMBER_MESSAGE
    character.clan = None
    await character.asave(update_fields=("clan",))
    character_user = await User.objects.aget(character=character)
    await send_message_to_user(
        character_user.telegram_id,
        SUCCESS_KICKING_MEMBER_MESSAGE_TO_USER.format(clan.name_with_emoji),
    )
    return True, SUCCESS_KICKING_MEMBER_MESSAGE.format(
        character.name_with_class
    )
