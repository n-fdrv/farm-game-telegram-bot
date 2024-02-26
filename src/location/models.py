from django.db import models
from item.models import Item


class BaseLocationModel(models.Model):
    """Базовая модель для моделей игры."""

    name = models.CharField(max_length=16, verbose_name="Имя")
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )


class Location(BaseLocationModel):
    """Модель для хранения локаций."""

    attack = models.IntegerField(verbose_name="Требуемая атака персонажа")
    defence = models.IntegerField(verbose_name="Требуемая защита персонажа")
    exp = models.IntegerField(
        default=1, verbose_name="Количество опыта в минуту"
    )
    drop = models.ManyToManyField(
        Item, through="LocationDrop", related_name="drop"
    )

    class Meta:
        verbose_name = "Локация"
        verbose_name_plural = "Локации"

    def __str__(self):
        return f"{self.name} | Attack: {self.attack} | Defence: {self.defence}"


class LocationDrop(models.Model):
    """Модель для хранения дроп листа в локациях."""

    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, verbose_name="Локация"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, verbose_name="Предмет"
    )
    min_amount = models.IntegerField(
        default=1, verbose_name="Минимальное количество"
    )
    max_amount = models.IntegerField(
        default=1, verbose_name="Максимальное количество"
    )
    chance = models.FloatField(
        default=1, verbose_name="Шанс в процентах в минуту"
    )

    class Meta:
        verbose_name = "Дроп в локации"
        verbose_name_plural = "Дроп в локациях"

    def __str__(self):
        return (
            f"Item: {self.item} | "
            f"Location: {self.location} | "
            f"Amount: {self.min_amount} - {self.max_amount} | "
            f"Chance: {self.chance}"
        )
