import csv

from character.models import CharacterClass, Skill
from django.core.management.base import BaseCommand
from loguru import logger

from item.models import ITEM_DATA


class Command(BaseCommand):
    """Команда заполнения баззы данных."""

    help = "Заполняет базу данных записями"

    def handle(self, *args, **kwargs):
        """Метод при вызове команды."""
        logger.info("Books upload started")
        with open("data/items/books.csv", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    character_class = CharacterClass.objects.get(name=row[5])
                    required_skill = Skill.objects.get(
                        name=row[7], level=row[8]
                    )
                    skill = Skill.objects.get(name=row[9], level=row[10])
                    ITEM_DATA[row[4]].objects.get_or_create(
                        name=row[0],
                        description=row[1],
                        sell_price=row[2],
                        buy_price=row[3],
                        type=row[4],
                        character_class=character_class,
                        required_level=row[6],
                        required_skill=required_skill,
                        skill=skill,
                    )
                except Exception as e:
                    logger.error(f"error in uploading: Book - {row[0]}: {e}")
        logger.info("Books upload ended")
