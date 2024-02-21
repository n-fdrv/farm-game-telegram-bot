import csv

from django.core.management.base import BaseCommand
from loguru import logger

from game.models import Character, CharacterItem, Item, Location


class Command(BaseCommand):
    """Команда заполнения баззы данных."""

    help = "Заполняет базу данных записями"

    def handle(self, *args, **kwargs):
        """Метод при вызове команды."""
        with open("data/characters.csv", encoding="utf-8") as f:
            logger.info("Characters upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    character, created = Character.objects.get_or_create(
                        name=row[0],
                        level=row[1],
                        exp=row[2],
                        exp_for_level_up=row[3],
                        power=row[4],
                        job_id=row[9],
                    )
                    if row[5]:
                        location = Location.objects.get(id=row[5])
                        character.current_location = location
                        character.hunting_begin = row[6]
                        character.hunting_end = row[7]
                        character.max_hunting_time = row[8]
                        character.save(
                            update_fields=(
                                "current_location",
                                "hunting_begin",
                                "hunting_end",
                                "max_hunting_time",
                            )
                        )
                except Exception as e:
                    logger.error(
                        f"error in uploading: Character - {row[0]}: {e}"
                    )
                    raise e
            logger.info("Characters upload ended")
        with open("data/character_items.csv", encoding="utf-8") as f:
            logger.info("Characters Items upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    character = Character.objects.get(id=row[1])
                    item = Item.objects.get(id=row[0])
                    CharacterItem.objects.get_or_create(
                        character=character,
                        item=item,
                        amount=row[2],
                    )
                except Exception as e:
                    logger.error(
                        f"error in uploading: Character Item - {row[0]}: {e}"
                    )
            logger.info("Character Items upload ended")
