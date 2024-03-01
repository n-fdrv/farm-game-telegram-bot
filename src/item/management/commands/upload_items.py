import csv
import os

from django.core.management.base import BaseCommand
from loguru import logger

from item.models import Item


class Command(BaseCommand):
    """Команда заполнения баззы данных."""

    help = "Заполняет базу данных записями обычных предметов"

    def handle(self, *args, **kwargs):
        """Метод при вызове команды."""
        logger.info("Base items upload started")
        directory = "data/items/base/"
        files = os.listdir(directory)
        for file in files:
            with open(f"{directory}{file}", encoding="utf-8") as f:

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
                        logger.error(
                            f"error in uploading: Base item - {row[0]}: {e}"
                        )
        logger.info("Base items upload started")
