from character.models import Character, CharacterItem
from premium_shop.models import (
    PremiumLot,
    PremiumLotReceivedItem,
    PremiumLotRequiredItem,
)

from bot.premium_shop.messages import (
    PREMIUM_LOT_GET_MESSAGE,
    SUCCESS_BUY_MESSAGE,
)
from bot.utils.game_utils import add_item, remove_item
from bot.utils.messages import NOT_ENOUGH_REQUIRED_ITEMS_MESSAGE


async def premium_lot_get_info(premium_lot: PremiumLot):
    """Получение информации о лоте."""
    return PREMIUM_LOT_GET_MESSAGE.format(
        premium_lot.name,
        premium_lot.amount,
        premium_lot.description,
        "\n".join(
            [
                f"<b>{x.item.name_with_type}</b> - <i>{x.amount} шт.</i>"
                async for x in PremiumLotReceivedItem.objects.select_related(
                    "item"
                ).filter(premium_lot=premium_lot)
            ]
        ),
        "\n".join(
            [
                f"<b>{x.item.name_with_type}</b> - <i>{x.amount} шт.</i>"
                async for x in PremiumLotRequiredItem.objects.select_related(
                    "item"
                ).filter(premium_lot=premium_lot)
            ]
        ),
    )


async def check_premium_lot_required_items(
    character: Character, premium_lot: PremiumLot
):
    """Метод проверки наличия предмета для крафта."""
    async for required_item in PremiumLotRequiredItem.objects.select_related(
        "item"
    ).filter(premium_lot=premium_lot):
        is_exist = await character.items.filter(
            pk=required_item.item.pk
        ).aexists()
        if not is_exist:
            return False, NOT_ENOUGH_REQUIRED_ITEMS_MESSAGE
        item = await CharacterItem.objects.aget(
            character=character, item=required_item.item.pk
        )
        if item.amount < required_item.amount:
            return False, NOT_ENOUGH_REQUIRED_ITEMS_MESSAGE
    return True, "Достаточно"


async def get_premium_lot(character: Character, premium_lot: PremiumLot):
    """Покупка лота."""
    success, text = await check_premium_lot_required_items(
        character, premium_lot
    )
    if not success:
        return success, text

    async for received_item in PremiumLotReceivedItem.objects.select_related(
        "item"
    ).filter(premium_lot=premium_lot):
        await add_item(
            character=character,
            item=received_item.item,
            amount=received_item.amount,
        )
    async for required_item in PremiumLotRequiredItem.objects.select_related(
        "item"
    ).filter(premium_lot=premium_lot):
        await remove_item(
            character=character,
            item=required_item.item,
            amount=required_item.amount,
        )
    return True, SUCCESS_BUY_MESSAGE.format(premium_lot.name)
