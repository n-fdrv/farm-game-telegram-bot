import csv

from django.core.management.base import BaseCommand
from loguru import logger

from character.models import Skill, SkillEffect


class Command(BaseCommand):
    """Команда заполнения баззы данных."""

    help = "Заполняет базу данных записями"

    def handle(self, *args, **kwargs):
        """Метод при вызове команды."""
        logger.info("Skills upload started")
        with open("data/characters/skills.csv", encoding="utf-8") as f:
            logger.info("Skills upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    Skill.objects.get_or_create(
                        name=row[0], description=row[1], level=row[2]
                    )
                except Exception as e:
                    logger.error(f"error in uploading: Skill - {row[0]}: {e}")
                    raise e
        with open("data/characters/effects.csv", encoding="utf-8") as f:
            logger.info("Effects upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    skill = Skill.objects.get(name=row[3])
                    SkillEffect.objects.get_or_create(
                        property=row[0],
                        amount=row[1],
                        in_percent=row[2],
                        skill=skill,
                    )
                except Exception as e:
                    logger.error(f"error in uploading: Effect - {row[0]}: {e}")
