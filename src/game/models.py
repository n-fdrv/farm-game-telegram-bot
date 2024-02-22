import datetime

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
    ETC = "etc", "Разное"


class ItemGrade(models.TextChoices):
    """Типы информационных карт."""

    COMMON = "common", "️⚪️ Обычный"
    UNCOMMON = "uncommon", "🟤 Необычный"
    RARE = "rare", "🔵 Редкий"
    LEGENDARY = "legendary", "🟠 Легендарный"
    EPIC = "epic", "🔴 Эпический"


class Item(BaseGameModel):
    """Модель для хранения предметов."""

    description = models.CharField(max_length=256, verbose_name="Описание")
    sell_price = models.IntegerField(
        default=0, verbose_name="Стоимость продажи"
    )
    buy_price = models.IntegerField(
        default=0, verbose_name="Стоимость покупки"
    )
    type = models.CharField(
        max_length=16,
        choices=ItemType.choices,
        verbose_name="Тип",
    )
    grade = models.CharField(
        max_length=16,
        choices=ItemGrade.choices,
        default=ItemGrade.COMMON,
        verbose_name="Ранг",
    )

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

    def __str__(self):
        return f"{self.name} | Type: {self.type}"

    @property
    def name_with_grade(self):
        """Возвращает полное имя пользователя."""
        return f"{self.get_grade_display()[:2]} {self.name}"


class Character(BaseGameModel):
    """Модель для хранения персонажей."""

    level = models.IntegerField(default=1, verbose_name="Уровень")
    exp = models.IntegerField(default=0, verbose_name="Опыт")
    exp_for_level_up = models.IntegerField(
        default=100, verbose_name="Опыт для достижения уровня"
    )
    power = models.IntegerField(default=100, verbose_name="Боевая мощь")
    current_location = models.ForeignKey(
        to="Location",
        on_delete=models.SET_NULL,
        verbose_name="Текущая локация",
        null=True,
        blank=True,
    )
    hunting_begin = models.DateTimeField(
        null=True, blank=True, verbose_name="Начало охоты"
    )
    hunting_end = models.DateTimeField(
        null=True, blank=True, verbose_name="Конец охоты"
    )
    max_hunting_time = models.TimeField(
        default=datetime.time(hour=4), verbose_name="Максимальное время охоты"
    )
    items = models.ManyToManyField(
        Item, through="CharacterItem", related_name="items"
    )
    job_id = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        verbose_name="ID шедулера напоминания об окончании охоты",
    )

    class Meta:
        verbose_name = "Персонаж"
        verbose_name_plural = "Персонажи"

    def __str__(self):
        return f"{self.name} | Level: {self.level} | Power : {self.power}"


class CharacterItem(models.Model):
    """Модель для хранения предметов персонажа."""

    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, verbose_name="Персонаж"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, verbose_name="Предмет"
    )
    amount = models.IntegerField(default=0, verbose_name="Количество")

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
    exp = models.IntegerField(
        default=100, verbose_name="Количество опыта в час"
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
        default=1, verbose_name="Минимальное количество в час"
    )
    max_amount = models.IntegerField(
        default=1, verbose_name="Максимальное количество в час"
    )
    chance = models.IntegerField(
        default=1, verbose_name="Шанс в процентах в час"
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
