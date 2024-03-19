import csv

from django.core.management.base import BaseCommand
from loguru import logger

from item.models import Bag, BagItem, Item


class Command(BaseCommand):
    """Команда заполнения баззы данных."""

    help = "Заполняет базу данных записями обычных предметов"

    def handle(self, *args, **kwargs):
        """Метод при вызове команды."""
        logger.info("Loot upload started")
        with open("data/items/bag_items.csv", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    bag = Bag.objects.get(name=row[0])
                    item = Item.objects.get(name=row[1])
                    BagItem.objects.get_or_create(
                        bag=bag,
                        item=item,
                        chance=row[2],
                    )
                except Exception as e:
                    logger.error(f"error in uploading: Loot - {row[0]}: {e}")
