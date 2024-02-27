import csv

from django.core.management.base import BaseCommand
from loguru import logger

from item.models import Item, ItemEffect


class Command(BaseCommand):
    """Команда заполнения баззы данных."""

    help = "Заполняет базу данных записями"

    def handle(self, *args, **kwargs):
        """Метод при вызове команды."""
        with open("data/items/effects.csv", encoding="utf-8") as f:
            logger.info("Effects upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    item = Item.objects.get(name=row[3])
                    ItemEffect.objects.get_or_create(
                        property=row[0],
                        amount=row[1],
                        in_percent=row[2],
                        item=item,
                    )
                except Exception as e:
                    logger.error(f"error in uploading: Effect - {row[0]}: {e}")
