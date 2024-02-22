import datetime

from django.db import models
from item.models import ArmorType, Item, WeaponType
from location.models import Location


class BaseCharacterModel(models.Model):
    """Базовая модель для моделей игры."""

    name = models.CharField(max_length=16, verbose_name="Имя")
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )


class CharacterClass(BaseCharacterModel):
    """модель хранения классов персонаже."""

    description = models.TextField(verbose_name="Описание")
    attack = models.IntegerField(default=0, verbose_name="Атака")
    defence = models.IntegerField(default=0, verbose_name="Защита")
    attack_level_increase = models.IntegerField(
        default=1, verbose_name="Прирост атаки за уровень"
    )
    defence_level_increase = models.IntegerField(
        default=1, verbose_name="Прирост защиты за уровень"
    )
    armor_type = models.CharField(
        max_length=16,
        choices=ArmorType.choices,
        default=ArmorType.HEAVY,
        verbose_name="Вид брони",
    )
    weapon_type = models.CharField(
        max_length=16,
        choices=WeaponType.choices,
        default=WeaponType.SWORD,
        verbose_name="Вид оружия",
    )

    class Meta:
        verbose_name = "Класс"
        verbose_name_plural = "Классы"

    def __str__(self):
        return f"{self.name}"


class Character(BaseCharacterModel):
    """Модель для хранения персонажей."""

    character_class = models.ForeignKey(
        CharacterClass,
        on_delete=models.CASCADE,
        verbose_name="Класс персонажа",
    )
    level = models.IntegerField(default=1, verbose_name="Уровень")
    exp = models.IntegerField(default=0, verbose_name="Опыт")
    exp_for_level_up = models.IntegerField(
        default=100, verbose_name="Опыт для достижения уровня"
    )
    attack = models.IntegerField(default=0, verbose_name="Атака")
    defence = models.IntegerField(default=0, verbose_name="Защита")
    current_location = models.ForeignKey(
        to=Location,
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
        return (
            f"{self.name} | "
            f"Level: {self.level} | "
            f"Attack : {self.attack} | "
            f"Defence: {self.defence}"
        )


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
