import random

from character.models import (
    Character,
    CharacterEffect,
    CharacterItem,
    CharacterSkill,
)
from item.models import (
    Bag,
    BagItem,
    Equipment,
    Item,
    ItemType,
    Potion,
    Recipe,
)

from bot.backpack.messages import ITEM_GET_MESSAGE


async def remove_item(character: Character, item: Item, amount: int):
    """Метод удаление предметов у персонажа."""
    exists = await character.items.filter(pk=item.pk).aexists()
    if not exists:
        return False
    character_items = await CharacterItem.objects.aget(
        character=character, item=item
    )
    character_items.amount -= amount
    if character_items.amount == 0:
        await character_items.adelete()
        return True
    await character_items.asave(update_fields=("amount",))
    return True


async def add_item(character: Character, item: Item, amount: int = 1):
    """Метод добавления предмета персонажу."""
    exists = await character.items.filter(pk=item.pk).aexists()
    if not exists:
        await character.items.aadd(item)
    character_items = await CharacterItem.objects.aget(
        character=character, item=item
    )
    character_items.amount += amount
    await character_items.asave(update_fields=("amount",))
    return True


async def get_gold_amount(character: Character):
    """Получение количества золота у персонажа."""
    exists = await CharacterItem.objects.filter(
        character=character, item__name__contains="Золото"
    ).aexists()
    if exists:
        gold = await CharacterItem.objects.aget(
            character=character, item__name__contains="Золото"
        )
        return gold.amount
    return 0


async def get_character_item_info_text(character_item: CharacterItem):
    """Метод получения текста информации о товаре."""
    additional_info = ""
    if await character_item.item.effect.aexists():
        additional_info = "\nЭффекты:\n"
        async for effect in character_item.item.effect.all():
            additional_info += (
                f"{effect.get_property_display()} - {effect.amount}"
            )
            if effect.in_percent:
                additional_info += "%"
            additional_info += "\n"
    if character_item.item.type == ItemType.BAG:
        additional_info += "\nВозможные трофеи:\n"
        async for drop in BagItem.objects.select_related("item").filter(
            bag=character_item.item
        ):
            additional_info += f"{drop.item.name_with_type}\n"
    description = character_item.item.description
    if character_item.equipped:
        description += "\n<b>Надето</b>"
    shop_text = ""
    if character_item.item.buy_price:
        shop_text += f"Покупка: {character_item.item.buy_price} золота."
    if character_item.item.sell_price:
        shop_text += f"\nПродажа: {character_item.item.sell_price} золота."
    return ITEM_GET_MESSAGE.format(
        character_item.item.name_with_type,
        character_item.amount,
        description,
        additional_info,
        shop_text,
    )


async def equip_item(item: CharacterItem):
    """Метод надевания, снятия предмета."""
    equipment = await Equipment.objects.aget(pk=item.item.pk)
    if equipment.equipment_type not in [
        x.type async for x in item.character.character_class.equip.all()
    ]:
        return False
    if item.equipped:
        item.equipped = False
        async for effect in item.item.effect.all():
            await CharacterEffect.objects.filter(
                character=item.character, effect=effect
            ).adelete()
        await item.asave(update_fields=("equipped",))
        return True
    type_equipped = await item.character.items.filter(
        characteritem__equipped=True, type=item.item.type
    ).aexists()
    if type_equipped:
        equipped_item = await CharacterItem.objects.select_related(
            "item"
        ).aget(
            character=item.character, item__type=item.item.type, equipped=True
        )
        async for effect in equipped_item.item.effect.all():
            await CharacterEffect.objects.filter(
                character=item.character, effect=effect
            ).adelete()
        equipped_item.equipped = False
        await equipped_item.asave(update_fields=("equipped",))
    item.equipped = True
    async for effect in item.item.effect.all():
        await CharacterEffect.objects.acreate(
            character=item.character,
            effect=effect,
            permanent=True,
            hunting_amount=0,
        )
    await item.asave(update_fields=("equipped",))
    return True


async def use_potion(character: Character, item: Item):
    """Метод использования предмета."""
    potion = await Potion.objects.aget(pk=item.pk)
    async for effect in potion.effect.all():
        character_effect, created = (
            await CharacterEffect.objects.aget_or_create(
                character=character, effect=effect
            )
        )
        if not created:
            character_effect.hunting_amount += 1
            await character_effect.asave(update_fields=("hunting_amount",))
    await remove_item(item=item, character=character, amount=1)


async def use_recipe(character: Character, item: Item):
    """Метод использования рецепта."""
    if character.character_class.name != "Мастер":
        return False
    recipe = await Recipe.objects.aget(pk=item.pk)
    character_skill = await CharacterSkill.objects.select_related(
        "skill"
    ).aget(character=character, skill__name="Мастер Создания")
    if character_skill.skill.level < recipe.level:
        return False
    if await character.recipes.filter(name=recipe.name).aexists():
        return False
    await character.recipes.aadd(recipe)
    await remove_item(item=item, character=character, amount=1)
    return True


async def open_bag(character: Character, item: Item):
    """Метод использования предмета."""
    bag = await Bag.objects.aget(pk=item.pk)
    chance = random.uniform(0.01, 100)
    bag_item = (
        await BagItem.objects.select_related("item")
        .filter(bag=bag, chance__lte=chance)
        .order_by("?")
        .afirst()
    )
    if not bag_item:
        bag_item = (
            await BagItem.objects.select_related("item")
            .filter(bag=bag, chance__gte=chance)
            .order_by("?")
            .afirst()
        )
    await add_item(item=bag_item.item, character=character, amount=1)
    await remove_item(item=item, character=character, amount=1)
    return bag_item
