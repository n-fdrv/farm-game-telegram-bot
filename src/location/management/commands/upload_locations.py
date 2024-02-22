import csv

from django.core.management.base import BaseCommand
from item.models import Item
from loguru import logger

from location.models import Location, LocationDrop


class Command(BaseCommand):
    """Команда заполнения баззы данных."""

    help = "Заполняет базу данных записями"

    def handle(self, *args, **kwargs):
        """Метод при вызове команды."""
        with open("data/locations/locations.csv", encoding="utf-8") as f:
            logger.info("Locations upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    Location.objects.get_or_create(
                        name=row[0],
                        attack=row[1],
                        defence=row[2],
                        exp=row[3],
                    )
                except Exception as e:
                    logger.error(
                        f"error in uploading: Location - {row[0]}: {e}"
                    )
                    raise e
            logger.info("Locations upload ended")
        with open("data/locations/location_drop.csv", encoding="utf-8") as f:
            logger.info("Location Drop upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    location = Location.objects.get(name=row[0])
                    item = Item.objects.get(name=row[1])
                    LocationDrop.objects.get_or_create(
                        location=location,
                        item=item,
                        min_amount=row[2],
                        max_amount=row[3],
                        chance=row[4],
                    )
                except Exception as e:
                    logger.error(
                        f"error in uploading: Location Drop - {row[0]}: {e}"
                    )
            logger.info("Location Drop upload ended")
