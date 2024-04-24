from character.models import CharacterSkill
from item.models import Item

from bot.character.utils import regen_health_or_mana
from bot.utils.game_utils import add_item


async def regeneration(character_skill: CharacterSkill):
    """Использование умения регенерации здоровья или маны."""
    text = "<i>Восстановлено:</i>"
    async for effect in character_skill.skill.effects.all():
        text += f"\n<i>{effect.get_property_display()}:</i> {effect.amount}"
        await regen_health_or_mana(
            character_skill.character, effect.property, effect.amount
        )
    return text


async def create_elixir(character_skill: CharacterSkill):
    """Использование умения Создание Эликсира."""
    bag_data = {1: "Эликсиры Мастера Ур. 1"}

    bag = await Item.objects.aget(name=bag_data[character_skill.skill.level])
    await add_item(character_skill.character, bag)
    return "<i>Получено:</i>\n" f"<b>{bag.name_with_type}</b>"
