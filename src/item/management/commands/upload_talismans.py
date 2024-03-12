import csv

from django.core.management.base import BaseCommand
from loguru import logger

from item.models import ITEM_DATA


class Command(BaseCommand):
    """Команда заполнения баззы данных."""

    help = "Заполняет базу данных записями"

    def handle(self, *args, **kwargs):
        """Метод при вызове команды."""
        logger.info("Talismans upload started")
        with open("data/items/talismans.csv", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    ITEM_DATA[row[4]].objects.get_or_create(
                        name=row[0],
                        description=row[1],
                        sell_price=row[2],
                        buy_price=row[3],
                        type=row[4],
                        talisman_type=row[5],
                    )
                except Exception as e:
                    logger.error(
                        f"error in uploading: Talisman - {row[0]}: {e}"
                    )
        logger.info("Talisman upload ended")