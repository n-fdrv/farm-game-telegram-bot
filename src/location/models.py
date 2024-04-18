import datetime

from django.db import models
from django.utils import timezone
from item.models import Item


class HuntingZone(models.Model):
    """Базовая модель для моделей игры."""

    name = models.CharField(max_length=32, verbose_name="Имя")
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    exp = models.IntegerField(
        default=1, verbose_name="Количество опыта в минуту"
    )
    drop = models.ManyToManyField(
        Item, through="HuntingZoneDrop", related_name="drop"
    )


class Location(HuntingZone):
    """Модель для хранения локаций."""

    place = models.IntegerField(default=10, verbose_name="Мест в локации")
    required_power = models.IntegerField(
        default=100, verbose_name="Требуемая сила персонажа"
    )

    class Meta:
        verbose_name = "Локация"
        verbose_name_plural = "Локации"

    def __str__(self):
        return f"{self.name} | Power: {self.required_power}"

    @property
    def name_with_power(self):
        """Имя с необходимой силой клана."""
        return f"{self.name} ⚔️{self.required_power}"


class HuntingZoneDrop(models.Model):
    """Модель для хранения дроп листа в локациях."""

    hunting_zone = models.ForeignKey(
        HuntingZone, on_delete=models.CASCADE, verbose_name="Зона Охоты"
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
        verbose_name = "Дроп в зоне охоты"
        verbose_name_plural = "Дроп в зонах охоты"

    def __str__(self):
        return (
            f"Item: {self.item} | "
            f"Location: {self.hunting_zone} | "
            f"Amount: {self.min_amount} - {self.max_amount} | "
            f"Chance: {self.chance}"
        )


class LocationBoss(models.Model):
    """Модель боссов локаций."""

    name = models.CharField(max_length=16, verbose_name="Имя")
    respawn = models.DateTimeField(
        default=timezone.now, verbose_name="Время Респауна"
    )
    required_power = models.IntegerField(
        default=100, verbose_name="Необходимая сила персонажа"
    )
    drop = models.ManyToManyField(
        Item, through="LocationBossDrop", related_name="location_boss_drop"
    )
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, verbose_name="Локация"
    )
    characters = models.ManyToManyField(
        to="character.Character", through="LocationBossCharacter"
    )

    class Meta:
        verbose_name = "Босс Локации"
        verbose_name_plural = "Боссы Локации"

    def __str__(self):
        return (
            f"Name: {self.name} | "
            f"Required Power: {self.required_power} | "
            f"Respawn: {self.respawn}"
        )

    @property
    def name_with_power(self):
        """Имя с необходимой силой клана."""
        return f"{self.name} ⚔️{self.required_power}"


class LocationBossCharacter(models.Model):
    """Модель хранения персонажей участвующих в рейде."""

    character = models.ForeignKey(
        to="character.Character",
        on_delete=models.CASCADE,
        verbose_name="Персонаж в рейде",
    )
    boss = models.ForeignKey(
        LocationBoss, on_delete=models.CASCADE, verbose_name="Босс локации"
    )

    class Meta:
        verbose_name = "Персонаж в рейде"
        verbose_name_plural = "Персонажи в рейде"

    def __str__(self):
        return f"Character: {self.character} | " f"Boss: {self.boss}"


class LocationBossDrop(models.Model):
    """Модель для хранения дроп листа боссов локации."""

    boss = models.ForeignKey(
        LocationBoss, on_delete=models.CASCADE, verbose_name="Босс локации"
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
        verbose_name = "Трофей с босса"
        verbose_name_plural = "Трофеи с босса"

    def __str__(self):
        return f"{self.item.name_with_type} {self.chance}"


class Dungeon(HuntingZone):
    """Модель для хранения локаций."""

    min_level = models.IntegerField(
        default=1, verbose_name="Минимальный Уровень Персонажа"
    )
    max_level = models.IntegerField(
        default=1, verbose_name="Максимальный Уровень Персонажа"
    )
    cooldown_hours = models.IntegerField(
        default=24, verbose_name="Ожидание часов для повторного входа"
    )
    hunting_hours = models.IntegerField(
        default=4, verbose_name="Часов максимальной охоты"
    )
    required_items = models.ManyToManyField(
        Item,
        through="DungeonRequiredItem",
        related_name="dungeon_required_items",
    )
    characters = models.ManyToManyField(
        to="character.Character",
        through="DungeonCharacter",
        related_name="dungeon_characters",
    )

    class Meta:
        verbose_name = "Подземелье"
        verbose_name_plural = "Подземелья"

    def __str__(self):
        return f"{self.name} | Level: {self.min_level} - {self.max_level}"

    @property
    def name_with_level(self):
        """Имя с необходимой силой клана."""
        return f"{self.name} Ур. {self.min_level}-{self.max_level}"


class DungeonCharacter(models.Model):
    """Модель для хранения предметов персонажа."""

    dungeon = models.ForeignKey(
        Dungeon, on_delete=models.CASCADE, verbose_name="Подземелье"
    )
    character = models.ForeignKey(
        to="character.Character",
        on_delete=models.CASCADE,
        verbose_name="Персонаж",
    )
    hunting_begin = models.DateTimeField(
        default=timezone.now() - datetime.timedelta(days=364),
        verbose_name="Начало охоты",
    )


class DungeonRequiredItem(models.Model):
    """Модель для хранения предметов персонажа."""

    dungeon = models.ForeignKey(
        Dungeon, on_delete=models.CASCADE, verbose_name="Подземелье"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, verbose_name="Предмет"
    )
    amount = models.IntegerField(default=0, verbose_name="Количество")
