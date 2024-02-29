import csv

from django.core.management.base import BaseCommand
from loguru import logger

from item.models import CraftingItem, Item, Recipe


class Command(BaseCommand):
    """Команда заполнения баззы данных."""

    help = "Заполняет базу данных записями"

    def handle(self, *args, **kwargs):
        """Метод при вызове команды."""
        with open("data/items/recipes.csv", encoding="utf-8") as f:
            logger.info("Recipes upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    create = Item.objects.get(name=row[8])
                    Recipe.objects.get_or_create(
                        name=row[0],
                        description=row[1],
                        sell_price=row[2],
                        buy_price=row[3],
                        type=row[4],
                        grade=row[5],
                        level=row[6],
                        chance=row[7],
                        create=create,
                    )
                except Exception as e:
                    logger.error(f"error in uploading: Recipe - {row[0]}: {e}")
        with open("data/items/recipes_items.csv", encoding="utf-8") as f:
            logger.info("Recipes Items upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    material = Item.objects.get(name=row[0])
                    recipe = Recipe.objects.get(name=row[1])
                    CraftingItem.objects.get_or_create(
                        material=material,
                        recipe=recipe,
                        amount=row[2],
                    )
                except Exception as e:
                    logger.error(
                        f"error in uploading: Recipe item - {row[0]}: {e}"
                    )