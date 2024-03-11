import csv
import os

from django.core.management.base import BaseCommand
from loguru import logger

from item.models import ITEM_DATA, Bag, BagItem, Item


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
                        ITEM_DATA[row[4]].objects.get_or_create(
                            name=row[0],
                            description=row[1],
                            sell_price=row[2],
                            buy_price=row[3],
                            type=row[4],
                        )
                    except Exception as e:
                        logger.error(
                            f"error in uploading: Base item - {row[0]}: {e}"
                        )
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
                    logger.error(
                        f"error in uploading: Base item - {row[0]}: {e}"
                    )
        logger.info("Base items upload started")
