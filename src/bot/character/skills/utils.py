from character.models import (
    Skill,
)


async def get_skill_effects_info(skill: Skill):
    """Метод получения текста эффектов умения."""
    text = ""
    async for effect in skill.effects.all():
        text += f"- {effect.get_property_display()}: <b>{effect.amount}</b>"
        if effect.in_percent:
            text += "<b>%</b>"
        text += "\n"
    return text
