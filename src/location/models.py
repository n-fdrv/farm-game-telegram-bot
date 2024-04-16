from django.db import models
from django.utils import timezone
from item.models import Item


class BaseLocationModel(models.Model):
    """Базовая модель для моделей игры."""

    name = models.CharField(max_length=32, verbose_name="Имя")
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )


class Location(BaseLocationModel):
    """Модель для хранения локаций."""

    exp = models.IntegerField(
        default=1, verbose_name="Количество опыта в минуту"
    )
    drop = models.ManyToManyField(
        Item, through="LocationDrop", related_name="drop"
    )
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
