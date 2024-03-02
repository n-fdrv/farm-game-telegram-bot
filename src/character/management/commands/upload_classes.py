import csv

from django.core.management.base import BaseCommand
from loguru import logger

from character.models import (
    CharacterClass,
    CharacterClassSkill,
    ClassEquipment,
    Skill,
)


class Command(BaseCommand):
    """Команда заполнения баззы данных."""

    help = "Заполняет базу данных записями"

    def handle(self, *args, **kwargs):
        """Метод при вызове команды."""
        with open("data/characters/classes.csv", encoding="utf-8") as f:
            logger.info("Classes upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    CharacterClass.objects.get_or_create(
                        name=row[0],
                        description=row[1],
                        attack=row[2],
                        defence=row[3],
                        emoji=row[4],
                    )
                except Exception as e:
                    logger.error(f"error in uploading: Class - {row[0]}: {e}")
                    raise e
        with open(
            "data/characters/class_equipment.csv", encoding="utf-8"
        ) as f:
            logger.info("Classes upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    character_class = CharacterClass.objects.get(name=row[0])
                    ClassEquipment.objects.get_or_create(
                        character_class=character_class,
                        type=row[1],
                    )
                except Exception as e:
                    logger.error(f"error in uploading: Class - {row[0]}: {e}")
                    raise e
        with open("data/characters/class_skills.csv", encoding="utf-8") as f:
            logger.info("Class Skills upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    skill = Skill.objects.get(name=row[1], level=row[2])
                    character_class = CharacterClass.objects.get(name=row[0])
                    CharacterClassSkill.objects.get_or_create(
                        character_class=character_class,
                        skill=skill,
                    )
                except Exception as e:
                    logger.error(
                        f"error in uploading: Class Skills  - {row[0]}: {e}"
                    )
                    raise e
