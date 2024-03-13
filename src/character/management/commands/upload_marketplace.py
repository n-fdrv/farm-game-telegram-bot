import csv

from django.core.management.base import BaseCommand
from item.models import Etc, Item
from loguru import logger

from character.models import Character, MarketplaceItem


class Command(BaseCommand):
    """Команда заполнения баззы данных."""

    help = "Заполняет базу данных записями"

    def handle(self, *args, **kwargs):
        """Метод при вызове команды."""
        logger.info("Marketplace upload started")
        with open("data/characters/marketplace.csv", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    seller = Character.objects.get(name=row[0])
                    item = Item.objects.get(name=row[1])
                    sell_currency = Etc.objects.get(name=row[4])
                    MarketplaceItem.objects.get_or_create(
                        seller=seller,
                        item=item,
                        amount=row[2],
                        enhancement_level=row[3],
                        sell_currency=sell_currency,
                        price=row[5],
                    )
                except Exception as e:
                    logger.error(
                        f"error in uploading: Marketplace - {row[0]}: {e}"
                    )
                    raise e
