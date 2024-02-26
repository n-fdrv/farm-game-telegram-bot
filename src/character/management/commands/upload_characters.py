import csv

from django.core.management.base import BaseCommand
from item.models import Item
from location.models import Location
from loguru import logger

from character.models import Character, CharacterClass, CharacterItem


class Command(BaseCommand):
    """Команда заполнения баззы данных."""

    help = "Заполняет базу данных записями"

    def handle(self, *args, **kwargs):
        """Метод при вызове команды."""
        logger.info("Characters upload started")
        with open("data/characters/classes.csv", encoding="utf-8") as f:
            logger.info("Characters upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    CharacterClass.objects.get_or_create(
                        name=row[0],
                        description=row[1],
                        attack=row[2],
                        defence=row[3],
                        attack_level_increase=row[4],
                        defence_level_increase=row[5],
                        armor_type=row[6],
                        weapon_type=row[7],
                    )
                except Exception as e:
                    logger.error(
                        f"error in uploading: Character - {row[0]}: {e}"
                    )
                    raise e
        with open("data/characters/characters.csv", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    character_class = CharacterClass.objects.get(name=row[6])
                    character, created = Character.objects.get_or_create(
                        name=row[0],
                        level=row[1],
                        exp=row[2],
                        exp_for_level_up=row[3],
                        attack=row[4],
                        defence=row[5],
                        character_class=character_class,
                        job_id=row[11],
                    )
                    if row[7]:
                        location = Location.objects.get(name=row[7])
                        character.current_location = location
                        character.hunting_begin = row[8]
                        character.hunting_end = row[9]
                        character.max_hunting_time = row[10]
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
        with open(
            "data/characters/character_items.csv", encoding="utf-8"
        ) as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    character = Character.objects.get(name=row[1])
                    item = Item.objects.get(name=row[0])
                    CharacterItem.objects.get_or_create(
                        character=character,
                        item=item,
                        amount=row[2],
                    )
                except Exception as e:
                    logger.error(
                        f"error in uploading: Character Item - {row[0]}: {e}"
                    )
            logger.info("Character upload ended")
