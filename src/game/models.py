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

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

    def __str__(self):
        return f"{self.name} | Type: {self.type}"


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

    class Meta:
        verbose_name = "Персонаж"
        verbose_name_plural = "Персонажи"

    def __str__(self):
        return f"{self.name} | Level: {self.level}"


class CharacterItem(models.Model):
    """Модель для хранения предметов персонажа."""

    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, verbose_name="Персонаж"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, verbose_name="Предмет"
    )
    amount = models.IntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Предмет персонажа"
        verbose_name_plural = "Предметы персонажа"

    def __str__(self):
        return (
            f"Character: {self.character} | "
            f"Item: {self.item} | "
            f"Amount: {self.amount}"
        )


class Location(BaseGameModel):
    """Модель для хранения локаций."""

    required_power = models.IntegerField(
        verbose_name="Требуемая сила персонажа"
    )
    drop = models.ManyToManyField(
        Item, through="LocationDrop", related_name="drop"
    )

    class Meta:
        verbose_name = "Локация"
        verbose_name_plural = "Лоакации"

    def __str__(self):
        return f"{self.name} | Power: {self.required_power}"


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

    class Meta:
        verbose_name = "Дроп в локации"
        verbose_name_plural = "Дроп в локациях"

    def __str__(self):
        return (
            f"Item: {self.item} | "
            f"Location: {self.location} | "
            f"Amount: {self.max_amount} - {self.max_amount} | "
            f"Chance: {self.chance}"
        )
