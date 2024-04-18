import datetime
import re

from character.models import Character, CharacterItem, MarketplaceItem
from clan.models import ClanWarehouse
from django.conf import settings
from django.db.models import F
from item.models import BagItem, Book, Item, ItemType

from bot.utils.messages import BOOK_INFO_MESSAGE, ITEM_GET_MESSAGE
from core.config import game_config


async def check_correct_amount(message: str):
    """Метод проверки правильности ввода количества товаров."""
    if not re.search("^[0-9]{1,16}$", message):
        return False
    if int(message) == 0:
        return False
    return True


async def remove_item(
    character: Character, item: Item, amount: int, enhancement_level: int = 0
):
    """Метод удаление предмета у персонажа."""
    exists = await CharacterItem.objects.filter(
        character=character, item=item, enhancement_level=enhancement_level
    ).aexists()
    if not exists:
        return False, 0
    character_item = await CharacterItem.objects.aget(
        character=character, item=item, enhancement_level=enhancement_level
    )
    if character_item.amount < amount:
        return False, character_item.amount
    character_item.amount -= amount
    if character_item.amount == 0:
        await character_item.adelete()
        return True, 0
    await character_item.asave(update_fields=("amount",))
    return True, character_item.amount


async def add_item(
    character: Character,
    item: Item,
    amount: int = 1,
    enhancement_level: int = 0,
    equipped: bool = False,
):
    """Метод добавления предмета персонажу."""
    exists = await CharacterItem.objects.filter(
        character=character, item=item, enhancement_level=enhancement_level
    ).aexists()
    if not exists:
        character_item = await CharacterItem.objects.select_related(
            "item", "character"
        ).acreate(
            character=character,
            item=item,
            amount=amount,
            enhancement_level=enhancement_level,
            equipped=equipped,
        )
        return character_item
    character_item = await CharacterItem.objects.select_related(
        "item", "character"
    ).aget(character=character, item=item, enhancement_level=enhancement_level)
    character_item.amount += amount
    await character_item.asave(update_fields=("amount",))
    return character_item


async def get_item_amount(
    character: Character, name: str, enhancement_level: int = 0
):
    """Получение количества золота у персонажа."""
    exists = await CharacterItem.objects.filter(
        character=character,
        item__name=name,
        enhancement_level=enhancement_level,
    ).aexists()
    if exists:
        item = await CharacterItem.objects.aget(
            character=character,
            item__name=name,
            enhancement_level=enhancement_level,
        )
        return item.amount
    return 0


async def get_expired_text(time_left: datetime.timedelta):
    """Получения остатка времени действия эликсира."""
    if time_left > datetime.timedelta(days=1):
        return f"более {time_left.days} суток"
    return str(time_left).split(".")[0]


async def get_item_effects(
    item_with_enhance: [CharacterItem, MarketplaceItem, ClanWarehouse, Item]
) -> str:
    """Метод получения эффектов предмета."""
    effects = ""
    item = item_with_enhance
    if type(item_with_enhance) is not Item:
        item = item.item
    if not await item.effects.aexists():
        return effects
    effects = "\n<i>Эффекты:</i>\n"
    async for effect in item.effects.all():
        amount = effect.amount
        if type(item) is not Item:
            enhance_type = game_config.ENHANCE_INCREASE
            if effect.in_percent:
                enhance_type = game_config.ENHANCE_IN_PERCENT_INCREASE
            amount = effect.amount + (enhance_type * item.enhancement_level)
        effects += f"{effect.get_property_display()} - {amount}"
        if effect.in_percent:
            effects += "%"
        effects += "\n"
    return effects


async def get_bag_loot(item: Item) -> str:
    """Метод получения дропа из мешков."""
    text = "\nВозможные трофеи:\n"
    all_chance = sum(
        [
            x
            async for x in BagItem.objects.values_list(
                "chance", flat=True
            ).filter(bag=item)
        ]
    )
    async for drop in BagItem.objects.select_related("item").filter(bag=item):
        chance = round(drop.chance / all_chance * 100, 2)
        amount = ""
        if drop.amount > 1:
            amount = f" ({drop.amount} шт.) "
        text += (
            f"<i>{drop.item.name_with_type} {amount}</i> - <b>{chance}%</b>\n"
        )
    return text


async def get_book_info(item: Item) -> str:
    """Метод получения дропа из мешков."""
    book = await Book.objects.select_related(
        "character_class",
        "required_skill",
    ).aget(pk=item.pk)
    required_skill = "Нет"
    if book.required_skill:
        required_skill = book.required_skill
    return BOOK_INFO_MESSAGE.format(
        book.character_class, book.required_level, required_skill
    )


async def get_lots_info(
    item: [CharacterItem, MarketplaceItem, ClanWarehouse], currency_name: str
):
    """Получение информации о выставленных лотах."""
    return " | ".join(
        [
            f"{x.price // x.amount}{x.sell_currency.emoji}"
            async for x in MarketplaceItem.objects.select_related(
                "sell_currency"
            )
            .annotate(price_per_item=F("price") / F("amount"))
            .filter(
                item=item.item,
                sell_currency__name=currency_name,
                enhancement_level=item.enhancement_level,
            )
            .order_by("price_per_item")[:5]
        ]
    )


async def get_item_info_text(
    item_data: [CharacterItem, MarketplaceItem, ClanWarehouse, Item]
):
    """Метод получения текста информации о товаре."""
    add_info_data = {ItemType.BAG: get_bag_loot, ItemType.BOOK: get_book_info}
    additional_info = await get_item_effects(item_data)
    name = item_data
    amount = 1
    gold_lots = ""
    diamonds_lots = ""
    item = item_data
    if type(item_data) is not Item:
        name = item_data.name_with_enhance
        amount = item_data.amount
        item = item_data.item
        gold_lots = await get_lots_info(item_data, settings.GOLD_NAME)
        diamonds_lots = await get_lots_info(item_data, settings.DIAMOND_NAME)
    if item.type in add_info_data.keys():
        additional_info += await add_info_data[item.type](item)
    equipped = ""

    if type(item_data) is CharacterItem:
        if item_data.equipped:
            equipped = "\n⤴️Экипировано"
    shop_text = ""
    if item.buy_price:
        shop_text += f"<i>Покупка:</i> <b>{item.buy_price}🟡</b> | "
    if item.sell_price:
        shop_text += f"<i>Продажа:</i> <b>{item.sell_price}🟡</b>"
    return ITEM_GET_MESSAGE.format(
        name,
        amount,
        equipped,
        item.description,
        additional_info,
        shop_text,
        gold_lots,
        diamonds_lots,
    )
