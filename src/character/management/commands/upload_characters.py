import csv

from django.core.management.base import BaseCommand
from item.models import Effect, Item
from location.models import Location
from loguru import logger

from character.models import (
    Character,
    CharacterClass,
    CharacterEffect,
    CharacterItem,
    CharacterSkill,
    Skill,
)


class Command(BaseCommand):
    """Команда заполнения баззы данных."""

    help = "Заполняет базу данных записями"

    def handle(self, *args, **kwargs):
        """Метод при вызове команды."""
        logger.info("Characters upload started")
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
                        equipped=row[3],
                    )
                except Exception as e:
                    logger.error(
                        f"error in uploading: Character Item - {row[0]}: {e}"
                    )
            logger.info("Character upload ended")
        with open(
            "data/characters/character_skills.csv", encoding="utf-8"
        ) as f:
            logger.info("Character Skills upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    skill = Skill.objects.get(name=row[1], level=row[2])
                    character = Character.objects.get(name=row[0])
                    CharacterSkill.objects.get_or_create(
                        character=character,
                        skill=skill,
                    )
                except Exception as e:
                    logger.error(
                        "error in uploading: "
                        f"Character Skills  - {row[0]}: {e}"
                    )
                    raise e

        with open(
            "data/characters/character_effects.csv", encoding="utf-8"
        ) as f:
            logger.info("Character Effects upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    effect, created = Effect.objects.get_or_create(
                        property=row[1], amount=row[2], in_percent=row[3]
                    )
                    character = Character.objects.get(name=row[0])
                    CharacterEffect.objects.get_or_create(
                        character=character, effect=effect, expired=row[4]
                    )
                except Exception as e:
                    logger.error(
                        "error in uploading: "
                        f"Character Effect  - {row[0]}: {e}"
                    )
                    raise e
