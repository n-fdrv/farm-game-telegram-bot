import csv

from django.core.management.base import BaseCommand
from game.models import Character
from loguru import logger

from bot.models import User


class Command(BaseCommand):
    """Команда заполнения баззы данных."""

    help = "Заполняет базу данных записями"

    def handle(self, *args, **kwargs):
        """Метод при вызове команды."""
        with open("data/users.csv", encoding="utf-8") as f:
            logger.info("Users upload started")
            reader = csv.reader(f)
            for row in reader:
                try:
                    user, created = User.objects.get_or_create(
                        telegram_id=row[0],
                        first_name=row[1],
                        last_name=row[2],
                        telegram_username=row[3],
                        registration_date=row[4],
                        is_admin=row[5],
                        is_active=row[7],
                    )
                    if row[6]:
                        character = Character.objects.get(name=row[6])
                        user.character = character
                        user.save(update_fields=("character",))
                except Exception as e:
                    logger.error(f"error in uploading: User - {row[0]}: {e}")
                    raise e
            logger.info("Users upload ended")
