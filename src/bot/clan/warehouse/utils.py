from character.models import Character
from clan.models import ClanWarehouse

from bot.clan.warehouse.messages import SUCCESS_SEND_MESSAGE
from bot.utils.game_utils import add_item


async def send_item_from_warehouse(
    item: ClanWarehouse, character: Character, amount: int = 1
):
    """Отправка предмета с хранилища клана персонажу."""
    if item.amount < amount:
        amount = item.amount
    item.amount -= amount
    await add_item(
        character=character,
        item=item.item,
        amount=amount,
        enhancement_level=item.enhancement_level,
    )
    if item.amount == 0:
        await item.adelete()
    else:
        await item.asave(update_fields=("amount",))
    return True, SUCCESS_SEND_MESSAGE.format(
        item.name_with_enhance, amount, character.name_with_class
    )
