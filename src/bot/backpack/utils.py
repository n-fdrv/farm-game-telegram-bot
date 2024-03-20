import datetime
import random

from character.models import (
    Character,
    CharacterEffect,
    CharacterItem,
    CharacterSkill,
)
from django.conf import settings
from django.utils import timezone
from item.models import (
    Bag,
    BagItem,
    Equipment,
    Item,
    ItemType,
    Potion,
    Recipe,
    Scroll,
    Talisman,
)

from bot.backpack.messages import (
    ALREADY_KNOWN_RECIPE,
    ENHANCE_GET_MESSAGE,
    EQUIP_MESSAGE,
    FAILURE_ENCHANT,
    ITEM_GET_MESSAGE,
    NO_BRACELET_MESSAGE,
    NOT_CORRECT_EQUIPMENT_TYPE_MESSAGE,
    NOT_CORRECT_SCROLL_TYPE_MESSAGE,
    NOT_ENOUGH_BRACELET_LEVEL_MESSAGE,
    NOT_ENOUGH_SKILL_LEVEL_MESSAGE,
    NOT_MASTER_CLASS_MESSAGE,
    SUCCESS_ENCHANT,
    SUCCESS_USE_MESSAGE,
    UNEQUIP_MESSAGE,
)
from core.config import game_config


async def remove_item(
    character: Character, item: Item, amount: int, enhancement_level: int = 0
):
    """Метод удаление предметов у персонажа."""
    exists = await CharacterItem.objects.filter(
        character=character, item=item, enhancement_level=enhancement_level
    ).aexists()
    if not exists:
        return False
    character_item = await CharacterItem.objects.aget(
        character=character, item=item, enhancement_level=enhancement_level
    )
    if character_item.amount < amount:
        return False
    character_item.amount -= amount
    if character_item.amount == 0:
        await character_item.adelete()
        return True
    await character_item.asave(update_fields=("amount",))
    return True


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
        await CharacterItem.objects.acreate(
            character=character,
            item=item,
            amount=amount,
            enhancement_level=enhancement_level,
            equipped=equipped,
        )
        return True
    character_items = await CharacterItem.objects.aget(
        character=character, item=item, enhancement_level=enhancement_level
    )
    character_items.amount += amount
    await character_items.asave(update_fields=("amount",))
    return True


async def get_gold_amount(character: Character):
    """Получение количества золота у персонажа."""
    exists = await CharacterItem.objects.filter(
        character=character, item__name=settings.GOLD_NAME
    ).aexists()
    if exists:
        gold = await CharacterItem.objects.aget(
            character=character, item__name=settings.GOLD_NAME
        )
        return gold.amount
    return 0


async def get_diamond_amount(character: Character):
    """Получение количества алмазов у персонажа."""
    exists = await CharacterItem.objects.filter(
        character=character, item__name=settings.DIAMOND_NAME
    ).aexists()
    if exists:
        diamond = await CharacterItem.objects.aget(
            character=character, item__name=settings.DIAMOND_NAME
        )
        return diamond.amount
    return 0


async def get_character_item_effects(character_item: CharacterItem) -> str:
    """Метод получения эффектов предмета."""
    effects = ""
    if not await character_item.item.effects.aexists():
        return effects
    enhance_type = game_config.ENHANCE_PROPERTY_INCREASE
    if character_item.item.type == ItemType.TALISMAN:
        enhance_type = game_config.ENHANCE_TALISMAN_INCREASE
    effects = "\n<i>Эффекты:</i>\n"
    async for effect in character_item.item.effects.all():
        amount = effect.amount + (
            enhance_type * character_item.enhancement_level
        )
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
        text += f"<b>{drop.item.name_with_type}</b> - {chance}%\n"
    return text


async def get_character_item_info_text(character_item: CharacterItem):
    """Метод получения текста информации о товаре."""
    additional_info = await get_character_item_effects(character_item)
    if character_item.item.type == ItemType.BAG:
        additional_info += await get_bag_loot(character_item.item)
    equipped = ""
    if character_item.equipped:
        equipped = "\n⤴️Экипировано"
    shop_text = ""
    if character_item.item.buy_price:
        shop_text += (
            f"<i>Покупка:</i> <b>{character_item.item.buy_price}🟡</b> | "
        )
    if character_item.item.sell_price:
        shop_text += (
            f"<i>Продажа:</i> <b>{character_item.item.sell_price}🟡</b>"
        )
    return ITEM_GET_MESSAGE.format(
        character_item.name_with_enhance,
        character_item.amount,
        equipped,
        character_item.item.description,
        additional_info,
        shop_text,
    )


async def get_character_item_enhance_text(character_item: CharacterItem):
    """Метод получения текста информации о товаре."""
    additional_info = await get_character_item_effects(character_item)
    description = ""
    if character_item.equipped:
        description += "Надето"
    enhance_increase = game_config.ENHANCE_PROPERTY_INCREASE
    if character_item.item.type == ItemType.TALISMAN:
        enhance_increase = game_config.ENHANCE_TALISMAN_INCREASE
    return ENHANCE_GET_MESSAGE.format(
        character_item.name_with_enhance,
        description,
        additional_info,
        game_config.ENHANCE_CHANCE[character_item.enhancement_level],
        enhance_increase,
    )


async def equip_item(item: CharacterItem):
    """Метод надевания, снятия предмета."""
    equipment = await Equipment.objects.aget(pk=item.item.pk)
    if equipment.equipment_type not in [
        x.type async for x in item.character.character_class.equip.all()
    ]:
        return False, NOT_CORRECT_EQUIPMENT_TYPE_MESSAGE
    if item.equipped:
        item.equipped = False
        await item.asave(update_fields=("equipped",))
        return True, UNEQUIP_MESSAGE
    type_equipped = await item.character.items.filter(
        characteritem__equipped=True, type=item.item.type
    ).aexists()
    if type_equipped:
        equipped_item = await CharacterItem.objects.select_related(
            "item"
        ).aget(
            character=item.character, item__type=item.item.type, equipped=True
        )
        equipped_item.equipped = False
        await equipped_item.asave(update_fields=("equipped",))
    item.equipped = True
    await item.asave(update_fields=("equipped",))
    return True, EQUIP_MESSAGE


async def equip_talisman(item: CharacterItem):
    """Метод надевания, снятия талисмана."""
    if item.equipped:
        item.equipped = False
        await item.asave(update_fields=("equipped",))
        return True, UNEQUIP_MESSAGE
    character = item.character
    bracelet_name = "Браслет"
    if not await CharacterItem.objects.filter(
        character=character, item__name=bracelet_name, equipped=True
    ).aexists():
        return False, NO_BRACELET_MESSAGE

    talisman = await Talisman.objects.aget(pk=item.item.pk)
    type_equipped = await CharacterItem.objects.filter(
        character=character, equipped=True, item=talisman
    ).aexists()
    if type_equipped:
        equipped_item = await CharacterItem.objects.select_related(
            "item"
        ).aget(character=character, item=talisman, equipped=True)
        equipped_item.equipped = False
        await equipped_item.asave(update_fields=("equipped",))
    bracelet = await CharacterItem.objects.aget(
        character=character, item__name=bracelet_name, equipped=True
    )
    talisman_equipped_amount = await CharacterItem.objects.filter(
        character=character, item__type=ItemType.TALISMAN, equipped=True
    ).acount()
    if talisman_equipped_amount == bracelet.enhancement_level + 1:
        return False, NOT_ENOUGH_BRACELET_LEVEL_MESSAGE.format(
            talisman_equipped_amount
        )
    item.equipped = True
    await item.asave(update_fields=("equipped",))
    return True, EQUIP_MESSAGE


async def use_potion(character: Character, item: Item):
    """Метод использования предмета."""
    potion = await Potion.objects.aget(pk=item.pk)
    async for effect in potion.effects.all():
        character_effect, created = (
            await CharacterEffect.objects.aget_or_create(
                character=character, effect=effect
            )
        )
        if character_effect.expired < timezone.now():
            character_effect.expired = timezone.now()
        character_effect.expired += datetime.timedelta(
            hours=potion.effect_time.hour,
            minutes=potion.effect_time.minute,
            seconds=potion.effect_time.second,
        )
        await character_effect.asave(update_fields=("expired",))
    await remove_item(item=item, character=character, amount=1)
    return True, SUCCESS_USE_MESSAGE.format(item.name_with_type)


async def use_recipe(character: Character, item: Item):
    """Метод использования рецепта."""
    if character.character_class.name != "Мастер":
        return False, NOT_MASTER_CLASS_MESSAGE
    recipe = await Recipe.objects.aget(pk=item.pk)
    character_skill = await CharacterSkill.objects.select_related(
        "skill"
    ).aget(character=character, skill__name="Мастер Создания")
    if character_skill.skill.level < recipe.level:
        return False, NOT_ENOUGH_SKILL_LEVEL_MESSAGE
    if await character.recipes.filter(name=recipe.name).aexists():
        return False, ALREADY_KNOWN_RECIPE
    await character.recipes.aadd(recipe)
    await remove_item(item=item, character=character, amount=1)
    return True, SUCCESS_USE_MESSAGE.format(item.name_with_type)


async def use_scroll(scroll: Scroll, character_item: CharacterItem):
    """Метод использования свитка."""
    if scroll.enhance_type != character_item.item.type:
        return False, NOT_CORRECT_SCROLL_TYPE_MESSAGE
    enhance_chance = game_config.ENHANCE_CHANCE[
        character_item.enhancement_level
    ]
    success = random.randint(1, 100) <= enhance_chance
    await remove_item(character_item.character, scroll, 1)
    if not success:
        return False, FAILURE_ENCHANT
    await remove_item(
        character_item.character,
        character_item.item,
        amount=1,
        enhancement_level=character_item.enhancement_level,
    )
    await add_item(
        character_item.character,
        character_item.item,
        amount=1,
        enhancement_level=character_item.enhancement_level + 1,
        equipped=character_item.equipped,
    )
    return True, SUCCESS_ENCHANT


async def open_bag(character: Character, item: Item, amount: int = 1):
    """Метод открытия мешков."""
    bag = await Bag.objects.aget(pk=item.pk)
    drop_data = {}
    item_data = []
    async for bag_item in BagItem.objects.select_related("item").filter(
        bag=bag
    ):
        item_data.extend([bag_item.item] * bag_item.chance)
    for _i in range(amount):
        chance = random.randint(0, len(item_data) - 1)
        loot = item_data[chance]
        await add_item(item=loot, character=character, amount=1)
        if loot.name_with_type not in drop_data:
            drop_data[loot.name_with_type] = 0
        drop_data[loot.name_with_type] += 1
    await remove_item(item=item, character=character, amount=amount)
    return drop_data
