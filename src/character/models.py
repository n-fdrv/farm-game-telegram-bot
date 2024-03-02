import datetime

from django.db import models
from item.models import (
    EffectProperty,
    EquipmentType,
    Item,
    ItemEffect,
    Recipe,
)
from location.models import Location


class BaseCharacterModel(models.Model):
    """Базовая модель для моделей игры."""

    name = models.CharField(max_length=16, verbose_name="Имя")
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )


class Skill(models.Model):
    """Модель для хранения умений персонажей."""

    name = models.CharField(max_length=32, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    level = models.IntegerField(default=1, verbose_name="Уровень")

    class Meta:
        verbose_name = "Умение"
        verbose_name_plural = "Умения"

    def __str__(self):
        return f"{self.name} Ур. {self.level}"

    @property
    def name_with_level(self):
        """Возвращает имя умения с уровнем."""
        return f"{self.name} Ур. {self.level}"


class SkillEffect(models.Model):
    """Модель хранения эффектов."""

    property = models.CharField(
        max_length=16,
        choices=EffectProperty.choices,
        default=EffectProperty.ATTACK,
        verbose_name="Свойство",
    )
    amount = models.IntegerField(default=0, verbose_name="Количество")
    in_percent = models.BooleanField(default=False, verbose_name="В процентах")
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        verbose_name="Умение",
        related_name="effect",
    )

    class Meta:
        verbose_name = "Эффект"
        verbose_name_plural = "Эффекты"

    def __str__(self):
        text = f"{self.get_property_display()}: {self.amount}"
        if self.in_percent:
            text += "%"
        return text


class CharacterClass(BaseCharacterModel):
    """модель хранения классов персонаже."""

    emoji = models.CharField(max_length=8, null=True, verbose_name="Эмоджи")
    description = models.TextField(verbose_name="Описание")
    attack = models.IntegerField(default=0, verbose_name="Атака")
    defence = models.IntegerField(default=0, verbose_name="Защита")
    skills = models.ManyToManyField(
        Skill, through="CharacterClassSkill", related_name="class_skills"
    )

    class Meta:
        verbose_name = "Класс"
        verbose_name_plural = "Классы"

    def __str__(self):
        return f"{self.emoji} {self.name}"

    @property
    def emoji_name(self):
        """Возвращает название класса с эмоджи."""
        return f"{self.emoji} {self.name}"


class ClassEquipment(models.Model):
    """Модель для хранения умений классов."""

    type = models.CharField(
        max_length=16,
        choices=EquipmentType.choices,
        null=True,
        verbose_name="Вид экипировки",
    )
    character_class = models.ForeignKey(
        CharacterClass,
        on_delete=models.CASCADE,
        verbose_name="Класс",
        related_name="equip",
    )

    class Meta:
        verbose_name = "Классовая экипировка"
        verbose_name_plural = "Классовые экипировки"

    def __str__(self):
        return f"{self.type} {self.character_class}"


class CharacterClassSkill(models.Model):
    """Модель для хранения умений классов."""

    skill = models.ForeignKey(
        Skill, on_delete=models.RESTRICT, verbose_name="Умение"
    )
    character_class = models.ForeignKey(
        CharacterClass, on_delete=models.CASCADE, verbose_name="Класс"
    )

    class Meta:
        verbose_name = "Умение класса"
        verbose_name_plural = "Умения классов"

    def __str__(self):
        return f"{self.skill} {self.character_class}"


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
        default=500, verbose_name="Опыт для достижения уровня"
    )
    attack = models.IntegerField(default=0, verbose_name="Атака")
    defence = models.IntegerField(default=0, verbose_name="Защита")
    exp_modifier = models.IntegerField(
        default=1, verbose_name="Модмфикатор опыта"
    )
    drop_modifier = models.IntegerField(
        default=1, verbose_name="Модификатор дропа"
    )
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
    skills = models.ManyToManyField(
        Skill, through="CharacterSkill", related_name="character_skills"
    )
    effects = models.ManyToManyField(
        ItemEffect, through="CharacterEffect", related_name="character_effects"
    )
    recipes = models.ManyToManyField(
        Recipe, through="CharacterRecipe", related_name="character_recipes"
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


class CharacterSkill(models.Model):
    """Модель для хранения умений персонажей."""

    skill = models.ForeignKey(
        Skill, on_delete=models.RESTRICT, verbose_name="Умение"
    )
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, verbose_name="Класс"
    )

    class Meta:
        verbose_name = "Умение персонажа"
        verbose_name_plural = "Умения персонажей"

    def __str__(self):
        return f"{self.skill} {self.character}"


class CharacterItem(models.Model):
    """Модель для хранения предметов персонажа."""

    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, verbose_name="Персонаж"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, verbose_name="Предмет"
    )
    amount = models.IntegerField(default=0, verbose_name="Количество")
    equipped = models.BooleanField(default=False, verbose_name="Надето")

    class Meta:
        verbose_name = "Предмет персонажа"
        verbose_name_plural = "Предметы персонажа"

    def __str__(self):
        return (
            f"Character: {self.character} | "
            f"Item: {self.item} | "
            f"Amount: {self.amount}"
        )


class CharacterRecipe(models.Model):
    """Модель для хранения рецептов персонажа."""

    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, verbose_name="Персонаж"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = "Рецепт персонажа"
        verbose_name_plural = "Рецепты персонажа"

    def __str__(self):
        return f"Character: {self.character} | " f"Item: {self.recipe}"


class CharacterEffect(models.Model):
    """Модель для хранения эффектов персонажа."""

    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, verbose_name="Персонаж"
    )
    effect = models.ForeignKey(
        ItemEffect, on_delete=models.RESTRICT, verbose_name="Эффект"
    )
    expired = models.DateTimeField(
        default=datetime.datetime(year=2100, month=12, day=31),
        verbose_name="Дата окончания эффекта",
    )

    class Meta:
        verbose_name = "Эффект персонажа"
        verbose_name_plural = "Эффекты персонажа"

    def __str__(self):
        return f"Character: {self.character} | " f"Effect: {self.effect}"
