import csv

from django.core.management.base import BaseCommand
from loguru import logger

from item.models import CraftingItem, Item


class Command(BaseCommand):
    """Команда заполнения баззы данных."""

    help = "Заполняет базу данных записями"

    def handle(self, *args, **kwargs):
        """Метод при вызове команды."""
        with open("data/items/weapons_crafts.csv", encoding="utf-8") as f:
            logger.info("Effects upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    used_item = Item.objects.get(name=row[1])
                    crafting_item = Item.objects.get(name=row[0])
                    CraftingItem.objects.get_or_create(
                        used_item=used_item,
                        crafting_item=crafting_item,
                        amount=row[2],
                    )
                except Exception as e:
                    logger.error(f"error in uploading: Effect - {row[0]}: {e}")
