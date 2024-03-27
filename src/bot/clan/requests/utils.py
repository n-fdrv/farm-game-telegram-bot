from character.models import Character
from clan.models import Clan, ClanRequest

from bot.clan.requests.messages import (
    CREATE_REQUEST_MESSAGE_TO_LEADER,
    ERROR_IN_ACCEPTING_REQUEST_MESSAGE,
    ERROR_IN_CREATING_REQUEST_MESSAGE,
    NO_PLACE_IN_CLAN_MESSAGE,
    SUCCESS_ACCEPTING_REQUEST_MESSAGE,
    SUCCESS_ACCEPTING_REQUEST_MESSAGE_TO_USER,
    SUCCESS_CREATING_REQUEST_MESSAGE,
    SUCCESS_DECLINE_REQUEST_MESSAGE_TO_USER,
    SUCCESS_DECLINING_REQUEST_MESSAGE,
)
from bot.models import User
from bot.utils.schedulers import send_message_to_user


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


async def accept_request(character: Character, clan: Clan):
    """Принятие заявки в клан."""
    if character.clan:
        return False, ERROR_IN_ACCEPTING_REQUEST_MESSAGE
    characters_in_clan = await Character.objects.filter(clan=clan).acount()
    if clan.place <= characters_in_clan:
        return False, NO_PLACE_IN_CLAN_MESSAGE
    character.clan = clan
    await character.asave(update_fields=("clan",))
    await ClanRequest.objects.filter(character=character).adelete()
    character_user = await User.objects.aget(character=character)
    await send_message_to_user(
        character_user.telegram_id,
        SUCCESS_ACCEPTING_REQUEST_MESSAGE_TO_USER.format(clan.name_with_emoji),
    )
    return True, SUCCESS_ACCEPTING_REQUEST_MESSAGE.format(
        character.name_with_class
    )


async def decline_request(character: Character, clan: Clan):
    """Принятие заявки в клан."""
    await ClanRequest.objects.filter(character=character).adelete()
    character_user = await User.objects.aget(character=character)
    await send_message_to_user(
        character_user.telegram_id,
        SUCCESS_DECLINE_REQUEST_MESSAGE_TO_USER.format(clan.name_with_emoji),
    )
    return True, SUCCESS_DECLINING_REQUEST_MESSAGE.format(
        character.name_with_class
    )
