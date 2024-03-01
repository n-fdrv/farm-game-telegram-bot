import csv

from django.core.management.base import BaseCommand
from loguru import logger

from item.models import Weapon


class Command(BaseCommand):
    """Команда заполнения баззы данных."""

    help = "Заполняет базу данных записями"

    def handle(self, *args, **kwargs):
        """Метод при вызове команды."""
        logger.info("Weapons upload started")
        with open("data/items/weapon.csv", encoding="utf-8") as f:

            reader = csv.reader(f)
            for row in reader:
                try:
                    Weapon.objects.get_or_create(
                        name=row[0],
                        description=row[1],
                        sell_price=row[2],
                        buy_price=row[3],
                        type=row[4],
                        grade=row[5],
                        weapon_type=row[6],
                    )
                except Exception as e:
                    logger.error(f"error in uploading: Weapon - {row[0]}: {e}")
        logger.info("Weapons upload ended")
