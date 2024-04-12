import datetime
import random

from character.models import (
    Character,
    CharacterEffect,
    CharacterItem,
    CharacterSkill,
)
from django.db.models import Q
from django.utils import timezone
from item.models import (
    Bag,
    BagItem,
    Book,
    EffectProperty,
    Equipment,
    Item,
    ItemType,
    Potion,
    Recipe,
    Scroll,
    Talisman,
)

from bot.character.backpack.messages import (
    ALREADY_KNOWN_RECIPE,
    ALREADY_KNOWN_SKILL_MESSAGE,
    ENHANCE_GET_MESSAGE,
    EQUIP_IN_LOCATION_MESSAGE,
    EQUIP_MESSAGE,
    FAILURE_ENCHANT,
    NO_BRACELET_MESSAGE,
    NOT_CORRECT_CHARACTER_CLASS_MESSAGE,
    NOT_CORRECT_CHARACTER_SKILL_MESSAGE,
    NOT_CORRECT_EQUIPMENT_TYPE_MESSAGE,
    NOT_CORRECT_SCROLL_TYPE_MESSAGE,
    NOT_ENOUGH_BRACELET_LEVEL_MESSAGE,
    NOT_ENOUGH_CHARACTER_LEVEL_MESSAGE,
    NOT_ENOUGH_SKILL_LEVEL_MESSAGE,
    NOT_MASTER_CLASS_MESSAGE,
    SUCCESS_ENCHANT,
    SUCCESS_PUT_MESSAGE,
    SUCCESS_PUT_MESSAGE_TO_USER,
    SUCCESS_USE_MESSAGE,
    UNEQUIP_MESSAGE,
)
from bot.character.utils import get_character_property, regen_health_or_mana
from bot.clan.warehouse.utils import add_clan_item
from bot.models import User
from bot.utils.game_utils import (
    add_item,
    get_item_effects,
    remove_item,
)
from core.config import game_config


async def get_character_item_enhance_text(character_item: CharacterItem):
    """Метод получения текста информации о товаре."""
    additional_info = await get_item_effects(character_item)
    description = ""
    if character_item.equipped:
        description += "Надето"
    return ENHANCE_GET_MESSAGE.format(
        character_item.name_with_enhance,
        description,
        additional_info,
        game_config.ENHANCE_CHANCE[character_item.enhancement_level],
        game_config.ENHANCE_INCREASE,
        game_config.ENHANCE_IN_PERCENT_INCREASE,
    )


async def equip_item(item: CharacterItem):
    """Метод надевания, снятия предмета."""
    if item.character.current_location:
        return False, EQUIP_IN_LOCATION_MESSAGE
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

    if await potion.effects.filter(
        Q(property=EffectProperty.HEALTH) | Q(property=EffectProperty.MANA)
    ).aexists():
        property_max_data = {
            EffectProperty.HEALTH: await get_character_property(
                character, EffectProperty.MAX_HEALTH
            ),
            EffectProperty.MANA: await get_character_property(
                character, EffectProperty.MAX_MANA
            ),
        }
        async for effect in potion.effects.all():
            amount = effect.amount
            if effect.in_percent:
                amount = (
                    property_max_data[effect.property] / 100 * effect.amount
                )
            await regen_health_or_mana(character, effect.property, amount)
        success, amount = await remove_item(
            item=item, character=character, amount=1
        )
        return True, SUCCESS_USE_MESSAGE.format(item.name_with_type, amount)
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
    success, amount = await remove_item(
        item=item, character=character, amount=1
    )
    return True, SUCCESS_USE_MESSAGE.format(item.name_with_type, amount)


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
    success, amount = await remove_item(
        item=item, character=character, amount=1
    )
    return True, SUCCESS_USE_MESSAGE.format(item.name_with_type, amount)


async def use_scroll(
    scroll_item: CharacterItem, character_item: CharacterItem
):
    """Метод использования свитка."""
    scroll = await Scroll.objects.aget(pk=scroll_item.item.pk)
    if scroll.enhance_type != character_item.item.type:
        return False, NOT_CORRECT_SCROLL_TYPE_MESSAGE
    enhance_chance = game_config.ENHANCE_CHANCE[
        character_item.enhancement_level
    ]
    success = random.randint(1, 100) <= enhance_chance
    remove, scroll_amount = await remove_item(
        character_item.character, scroll, 1
    )
    if not success:
        return character_item, FAILURE_ENCHANT.format(
            game_config.ENHANCE_CHANCE[character_item.enhancement_level],
            f"{scroll_amount} {scroll.name_with_type}",
        )
    await remove_item(
        character_item.character,
        character_item.item,
        amount=1,
        enhancement_level=character_item.enhancement_level,
    )
    new_item = await add_item(
        character_item.character,
        character_item.item,
        amount=1,
        enhancement_level=character_item.enhancement_level + 1,
        equipped=character_item.equipped,
    )
    return new_item, SUCCESS_ENCHANT.format(
        new_item.name_with_enhance,
        game_config.ENHANCE_CHANCE[new_item.enhancement_level],
        f"{scroll_amount} {scroll.name_with_type}",
    )


async def use_book(character: Character, item: Item):
    """Метод использования книги."""
    book = await Book.objects.select_related(
        "character_class", "required_skill", "skill"
    ).aget(pk=item.pk)
    if character.character_class != book.character_class:
        return False, NOT_CORRECT_CHARACTER_CLASS_MESSAGE
    if character.level < book.required_level:
        return False, NOT_ENOUGH_CHARACTER_LEVEL_MESSAGE
    if book.required_skill:
        if not await character.skills.filter(
            name=book.required_skill.name, level=book.required_skill.level
        ).aexists():
            return False, NOT_CORRECT_CHARACTER_SKILL_MESSAGE
    if await character.skills.filter(
        name=book.skill.name, level=book.skill.level
    ).aexists():
        return False, ALREADY_KNOWN_SKILL_MESSAGE
    await character.skills.aadd(book.skill)
    await CharacterSkill.objects.filter(
        skill__name=book.required_skill.name,
        skill__level=book.required_skill.level,
    ).adelete()
    success, amount = await remove_item(
        item=item, character=character, amount=1
    )
    return True, SUCCESS_USE_MESSAGE.format(item.name_with_type, amount)


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


async def send_item_to_clan_warehouse(
    character_item: CharacterItem, bot, amount
):
    """Передача предмета клану."""
    if character_item.amount < amount:
        amount = character_item.amount
    await add_clan_item(
        clan=character_item.character.clan,
        item=character_item.item,
        amount=amount,
        enhancement_level=character_item.enhancement_level,
    )
    leader_telegram_id = await User.objects.values_list(
        "telegram_id", flat=True
    ).aget(character=character_item.character.clan.leader)
    await bot.send_message(
        leader_telegram_id,
        SUCCESS_PUT_MESSAGE_TO_USER.format(
            character_item.character.name_with_clan,
            character_item.name_with_enhance,
            amount,
        ),
    )
    await remove_item(
        character=character_item.character,
        item=character_item.item,
        amount=amount,
        enhancement_level=character_item.enhancement_level,
    )
    return True, SUCCESS_PUT_MESSAGE.format(
        character_item.name_with_enhance,
        amount,
        character_item.character.clan.name_with_emoji,
    )
