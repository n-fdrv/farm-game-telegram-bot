from character.models import Character, CharacterPower, Power
from django.conf import settings
from item.models import EffectProperty

from bot.character.powers.messages import (
    NOT_ENOUGH_SKILL_POINTS_MESSAGE,
    POWER_GET_MESSAGE,
    POWER_LIST_MESSAGE,
    SUCCESS_POWER_ADD_MESSAGE,
    SUCCESS_POWER_RESET_MESSAGE,
)
from bot.utils.game_utils import get_item_amount
from bot.utils.messages import NOT_ENOUGH_DIAMOND_MESSAGE
from core.config.game_config import RESET_POWER_DIAMOND_COST


async def get_character_power_added_amount(
    character: Character, effect_property: EffectProperty
):
    """Получение прибавки к силе."""
    return sum(
        [
            x
            async for x in CharacterPower.objects.values_list(
                "power__effect__amount", flat=True
            ).filter(
                character=character, power__effect__property=effect_property
            )
        ]
    )


async def get_character_power_info(character: Character):
    """Получение информации о силе персонажа."""
    return POWER_LIST_MESSAGE.format(
        character.skill_points,
        await get_character_power_added_amount(
            character, EffectProperty.MAX_HEALTH
        ),
        await get_character_power_added_amount(
            character, EffectProperty.MAX_MANA
        ),
        await get_character_power_added_amount(
            character, EffectProperty.ATTACK
        ),
        await get_character_power_added_amount(
            character, EffectProperty.DEFENCE
        ),
        await get_character_power_added_amount(
            character, EffectProperty.ACCURACY
        ),
        await get_character_power_added_amount(
            character, EffectProperty.EVASION
        ),
        round(
            await get_character_power_added_amount(
                character, EffectProperty.CRIT_RATE
            )
            / 10,
            2,
        ),
        await get_character_power_added_amount(
            character, EffectProperty.CRIT_POWER
        ),
    )


async def power_reset(character: Character):
    """Сброс распределения сил персонажа."""
    diamond_amount = await get_item_amount(character, settings.DIAMOND_NAME)
    if diamond_amount < RESET_POWER_DIAMOND_COST:
        return False, NOT_ENOUGH_DIAMOND_MESSAGE
    async for power in character.powers.all():
        character.skill_points += power.price
    await character.powers.aclear()
    await character.asave(update_fields=("skill_points",))
    return True, SUCCESS_POWER_RESET_MESSAGE


async def get_power_info(power: Power):
    """Получение информации о силе."""
    return POWER_GET_MESSAGE.format(
        power.name,
        power.effect.get_property_display(),
        power.effect.amount,
        power.price,
    )


async def power_add(character: Character, power: Power):
    """Добавление силы персонажу."""
    if character.skill_points < power.price:
        return False, NOT_ENOUGH_SKILL_POINTS_MESSAGE
    character.skill_points -= power.price
    await character.asave(update_fields=("skill_points",))
    await CharacterPower.objects.acreate(power=power, character=character)
    return True, SUCCESS_POWER_ADD_MESSAGE.format(power.name)
