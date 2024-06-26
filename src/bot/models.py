from character.models import Character
from django.db import models


class User(models.Model):
    """Модель для хранения пользователей."""

    telegram_id = models.BigIntegerField(
        verbose_name="Telegram User ID", unique=True
    )
    first_name = models.CharField(
        max_length=255, verbose_name="Имя", null=True, blank=True
    )
    last_name = models.CharField(
        max_length=255, verbose_name="Фамилия", null=True, blank=True
    )
    telegram_username = models.CharField(
        max_length=255,
        verbose_name="Ник в телеграмме",
        null=True,
        blank=True,
    )
    registration_date = models.DateField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )
    is_admin = models.BooleanField(
        default=False, verbose_name="Права администратора"
    )
    character = models.ForeignKey(
        Character,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user",
        verbose_name="Персонаж",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    @property
    def full_name(self):
        """Возвращает полное имя пользователя."""
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        if self.first_name and self.last_name:
            return (
                f"{self.first_name} {self.last_name} | id: {self.telegram_id}"
            )
        return f"{self.telegram_username} | id: {self.telegram_id}"
