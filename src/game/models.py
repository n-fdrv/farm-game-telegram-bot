from django.db import models


class BaseGameModel(models.Model):
    """Базовая модель для моделей игры."""

    name = models.CharField(max_length=16, verbose_name="Имя")
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )


class ItemType(models.TextChoices):
    """Типы информационных карт."""

    ARMOR = "armor", "Броня"
    WEAPON = "weapon", "Оружие"
    TALISMAN = "talisman", "Талисман"
    MATERIAL = "material", "Ресурс"
    SCROLL = "scroll", "Свиток"


class Item(BaseGameModel):
    """Модель для хранения предметов."""

    description = models.CharField(max_length=256, verbose_name="Описание")
    type = models.CharField(
        max_length=16,
        choices=ItemType.choices,
        verbose_name="Тип",
    )


class Character(BaseGameModel):
    """Модель для хранения персонажей."""

    level = models.IntegerField(default=1, verbose_name="Уровень")
    exp = models.IntegerField(default=0, verbose_name="Опыт")
    exp_for_level_up = models.IntegerField(
        default=100, verbose_name="Опыт для достижения уровня"
    )
    items = models.ManyToManyField(
        Item, through="CharacterItem", related_name="items"
    )


class CharacterItem(models.Model):
    """Модель для хранения предметов персонажа."""

    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, verbose_name="Персонаж"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, verbose_name="Предмет"
    )
    amount = models.IntegerField(default=1, verbose_name="Количество")


class Location(BaseGameModel):
    """Модель для хранения локаций."""

    name = models.CharField(max_length=16, verbose_name="Имя")
    required_power = models.IntegerField(
        verbose_name="Требуемая сила персонажа"
    )
    drop = models.ManyToManyField(
        Item, through="LocationDrop", related_name="drop"
    )


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
    chance = models.IntegerField(default=1, verbose_name="Шанс в процентах")
