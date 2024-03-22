import datetime

from character.models import Character
from django.conf import settings
from django.utils import timezone
from item.models import Armor, Bag, Etc, Weapon

from bot.character.backpack.utils import add_item, remove_item
from bot.premium_shop.buttons import (
    MONTH_PREMIUM_BUTTON,
    START_PACK_BUTTON,
    WEEK_PREMIUM_BUTTON,
)
from bot.premium_shop.messages import NOT_ENOUGH_CURRENCY, SUCCESS_BUY_MESSAGE


async def buy_premium(character: Character, premium_type: str, price: int):
    """Метод покупки премиума."""
    premium_days = {WEEK_PREMIUM_BUTTON: 7, MONTH_PREMIUM_BUTTON: 30}
    diamonds = await Etc.objects.aget(name=settings.DIAMOND_NAME)
    success = await remove_item(character, diamonds, price)
    if not success:
        return False, NOT_ENOUGH_CURRENCY
    premium_expired = timezone.now()
    if character.premium_expired >= premium_expired:
        premium_expired = character.premium_expired
    character.premium_expired = premium_expired + datetime.timedelta(
        days=premium_days[premium_type],
    )
    await character.asave(update_fields=("premium_expired",))
    return True, SUCCESS_BUY_MESSAGE.format(premium_type)


async def buy_start_pack(character: Character, price: int):
    """Метод покупки стартового набора."""
    weapon = (
        await Weapon.objects.filter(
            equipment_type__in=character.character_class.equip.values_list(
                "type", flat=True
            ),
            sell_price__gt=0,
        )
        .order_by("sell_price")
        .afirst()
    )
    armor = (
        await Armor.objects.filter(
            equipment_type__in=character.character_class.equip.values_list(
                "type", flat=True
            ),
            sell_price__gt=0,
        )
        .order_by("sell_price")
        .afirst()
    )
    bag = await Bag.objects.aget(name="Мешок с Эликсирами (Обычный)")
    diamonds = await Etc.objects.aget(name=settings.DIAMOND_NAME)
    success = await remove_item(character, diamonds, price)
    if not success:
        return False, NOT_ENOUGH_CURRENCY
    await add_item(character, weapon)
    await add_item(character, armor)
    await add_item(character, bag, 40)
    return True, SUCCESS_BUY_MESSAGE.format(START_PACK_BUTTON)
