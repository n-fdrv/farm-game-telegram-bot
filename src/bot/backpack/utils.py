import datetime

from character.models import Character, CharacterEffect, CharacterItem
from django.utils import timezone
from item.models import Item, Potion

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
        character=character, item__name="Золото"
    ).aexists()
    if exists:
        gold = await CharacterItem.objects.aget(
            character=character, item__name="Золото"
        )
        return gold.amount
    return 0


async def get_character_item_info_text(character_item: CharacterItem):
    """Метод получения текста информации о товаре."""
    effects = ""
    if await character_item.item.effect.aexists():
        effects = "\nЭффекты:\n"
        async for effect in character_item.item.effect.all():
            effects += f"{effect.get_property_display()} - {effect.amount}"
            if effect.in_percent:
                effects += "%"
            effects += "\n"
    description = character_item.item.description
    if character_item.equipped:
        description += "\n<b>Надето</b>"
    shop_text = ""
    if character_item.item.buy_price:
        shop_text += f"Покупка: {character_item.item.buy_price} золота."
    if character_item.item.sell_price:
        shop_text += f"\nПродажа: {character_item.item.sell_price} золота."
    return ITEM_GET_MESSAGE.format(
        character_item.item.name_with_grade,
        character_item.amount,
        description,
        effects,
        shop_text,
    )


async def equip_item(item: CharacterItem):
    """Метод надевания, снятия предмета."""
    if item.equipped:
        item.equipped = False
        async for effect in item.item.effect.all():
            await CharacterEffect.objects.filter(
                character=item.character, effect=effect
            ).adelete()
        await item.asave(update_fields=("equipped",))
        return
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
        await item.character.effects.aadd(effect)
    await item.asave(update_fields=("equipped",))


async def use_potion(character: Character, item: Item):
    """Метод использования предмета."""
    potion = await Potion.objects.aget(pk=item.pk)
    async for effect in potion.effect.all():
        character_effect, created = (
            await CharacterEffect.objects.aget_or_create(
                character=character, effect=effect
            )
        )
        character_effect.expired = timezone.now() + datetime.timedelta(
            hours=potion.effect_time.hour,
            minutes=potion.effect_time.minute,
            seconds=potion.effect_time.second,
        )
        await character_effect.asave(update_fields=("expired",))
    await remove_item(item=item, character=character, amount=1)
