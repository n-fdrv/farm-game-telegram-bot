from character.models import Character
from clan.models import Clan

from bot.clan.members.messages import (
    ERROR_IN_KICK_MEMBER_MESSAGE,
    SUCCESS_KICKING_MEMBER_MESSAGE,
    SUCCESS_KICKING_MEMBER_MESSAGE_TO_USER,
)
from bot.clan.settings.messages import (
    NOT_EMPTY_REMOVING_CLAN_MESSAGE,
    NOT_LEADER_REMOVING_CLAN_MESSAGE,
    SUCCESS_REMOVE_CLAN_MESSAGE,
)
from bot.models import User
from bot.utils.schedulers import send_message_to_user

EMOJI_DATA = [
    '🐶', '🐱', '🐭', '🐹',
    '🐰', '🦊', '🐻', '🐼',
    '🐻', '‍❄️', '🐨', '🐯',
    '🦁', '🐮', '🐷', '🐽',
    '🐸', '🐵', '🐒', '🐔',
    '🐥', '🐤', '🪿', '🦆',
    '🐦', '🦅', '🦉', '🦇',
    '🐺', '🐗', '🐴', '🦄',
    '🫎', '🐝', '🪱', '🐛',
    '🦋', '🐌', '🐞', '🐜',
    '🪰', '🪲', '🪳', '🦟',
    '🦗', '🕷', '🕸', '🦂',
    '🐢', '🐍', '🦎', '🦖',
    '🦕', '🐙', '🦑', '🪼',
    '🦐', '🦞', '🦀'
]


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


async def remove_clan(character: Character, clan: Clan):
    """Удаление клана."""
    if character != clan.leader:
        return False, NOT_LEADER_REMOVING_CLAN_MESSAGE
    characters_in_clan = await Character.objects.filter(
        clan=clan
    ).exclude(pk=character.pk).acount()
    if characters_in_clan:
        return False, NOT_EMPTY_REMOVING_CLAN_MESSAGE
    character.clan = None
    await character.asave(update_fields=('clan',))
    await clan.adelete()
    return True, SUCCESS_REMOVE_CLAN_MESSAGE
