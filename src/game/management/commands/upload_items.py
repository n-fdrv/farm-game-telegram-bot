import csv

from django.core.management.base import BaseCommand
from loguru import logger

from game.models import Item


class Command(BaseCommand):
    """Команда заполнения баззы данных."""

    help = "Заполняет базу данных записями"

    def handle(self, *args, **kwargs):
        """Метод при вызове команды."""
        with open("data/items.csv", encoding="utf-8") as f:
            logger.info("Items upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    Item.objects.get_or_create(
                        name=row[0],
                        description=row[1],
                        sell_price=row[2],
                        buy_price=row[3],
                        type=row[4],
                        grade=row[5],
                    )
                except Exception as e:
                    logger.error(f"error in uploading: Item - {row[0]}: {e}")
            logger.info("Item upload ended")
