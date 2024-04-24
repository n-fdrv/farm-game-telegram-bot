from clan.models import Clan
from django.db import models
from django.utils import timezone
from item.models import (
    Effect,
    EquipmentType,
    Etc,
    Item,
    Recipe,
)
from location.models import HuntingZone

from core.config import game_config


class SkillType(models.TextChoices):
    """Типы способностей."""

    PASSIVE = "passive", "Пассивная"
    TOGGLE = "toggle", "Переключаемая"
    ACTIVE = "active", "Активная"


class Skill(models.Model):
    """Модель для хранения умений персонажей."""

    name = models.CharField(max_length=32, verbose_name="Название")
    emoji = models.CharField(
        max_length=16, null=True, blank=True, verbose_name="Эмоджи"
    )
    description = models.TextField(verbose_name="Описание")
    level = models.IntegerField(default=1, verbose_name="Уровень")
    effects = models.ManyToManyField(
        Effect, through="SkillEffect", verbose_name="Эффекты способностей"
    )
    mana_cost = models.IntegerField(default=0, verbose_name="Мана кост")
    effect_time = models.TimeField(
        null=True, blank=True, verbose_name="Время действия"
    )
    cooldown = models.TimeField(
        null=True, blank=True, verbose_name="Перезарядка"
    )
    type = models.CharField(
        max_length=16,
        choices=SkillType.choices,
        default=SkillType.PASSIVE,
        verbose_name="Тип",
    )

    class Meta:
        verbose_name = "Умение"
        verbose_name_plural = "Умения"

    def __str__(self):
        return f"{self.emoji}{self.name} Ур. {self.level}"

    @property
    def name_with_level(self):
        """Возвращает имя умения с уровнем."""
        if self.emoji:
            return f"{self.emoji}{self.name} Ур. {self.level}"
        return f"{self.name} Ур. {self.level}"


class SkillEffect(models.Model):
    """Модель хранения эффектов предметов."""

    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, verbose_name="Способность"
    )
    effect = models.ForeignKey(
        to=Effect, on_delete=models.CASCADE, verbose_name="Эффект"
    )

    class Meta:
        verbose_name = "Эффект способности"
        verbose_name_plural = "Эффекты способностей"

    def __str__(self):
        return f"{self.skill} {self.effect}"


class Power(models.Model):
    """Модель хранения силы."""

    name = models.CharField(max_length=32, verbose_name="Название")
    effect = models.ForeignKey(
        Effect, on_delete=models.CASCADE, verbose_name="Эффект"
    )
    price = models.IntegerField(default=0, verbose_name="Цена")

    class Meta:
        verbose_name = "Сила"
        verbose_name_plural = "Силы"

    def __str__(self):
        return f"{self.name} ({self.price} SP) | {self.effect}"


class CharacterClass(models.Model):
    """модель хранения классов персонаже."""

    name = models.CharField(max_length=16, verbose_name="Имя")
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
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


class Character(models.Model):
    """Модель для хранения персонажей."""

    name = models.CharField(max_length=16, verbose_name="Имя")
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    character_class = models.ForeignKey(
        CharacterClass,
        on_delete=models.CASCADE,
        verbose_name="Класс персонажа",
    )
    level = models.IntegerField(default=1, verbose_name="Уровень")
    exp = models.IntegerField(default=0, verbose_name="Опыт")
    clan = models.ForeignKey(
        Clan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Клан",
    )
    exp_for_level_up = models.IntegerField(
        default=500, verbose_name="Опыт для достижения уровня"
    )
    attack = models.IntegerField(default=10, verbose_name="Атака")
    defence = models.IntegerField(default=10, verbose_name="Защита")
    crit_rate = models.IntegerField(
        default=game_config.CRIT_RATE_DEFAULT, verbose_name="Шанс Крита"
    )
    crit_power = models.IntegerField(
        default=game_config.CRIT_POWER_DEFAULT, verbose_name="Сила Крита"
    )
    evasion = models.IntegerField(
        default=game_config.EVASION_DEFAULT, verbose_name="Уклонение"
    )
    accuracy = models.IntegerField(
        default=game_config.ACCURACY_DEFAULT, verbose_name="Точность"
    )
    health = models.IntegerField(
        default=game_config.MAX_HEALTH_DEFAULT, verbose_name="Здоровье"
    )
    max_health = models.IntegerField(
        default=game_config.MAX_HEALTH_DEFAULT, verbose_name="Макс здоровье"
    )
    mana = models.IntegerField(
        default=game_config.MAX_MANA_DEFAULT, verbose_name="Мана"
    )
    max_mana = models.IntegerField(
        default=game_config.MAX_MANA_DEFAULT, verbose_name="Макс мана"
    )
    skill_points = models.IntegerField(
        default=0, verbose_name="Очки Характеристик"
    )
    premium_expired = models.DateTimeField(
        default=timezone.now, verbose_name="Окончание Премиума"
    )
    current_place = models.ForeignKey(
        to=HuntingZone,
        on_delete=models.SET_NULL,
        verbose_name="Текущая локация",
        null=True,
        blank=True,
    )
    hunting_begin = models.DateTimeField(
        null=True, blank=True, verbose_name="Начало охоты"
    )
    items = models.ManyToManyField(
        Item, through="CharacterItem", related_name="items"
    )
    skills = models.ManyToManyField(
        Skill, through="CharacterSkill", related_name="character_skills"
    )
    powers = models.ManyToManyField(
        Power, through="CharacterPower", related_name="character_power"
    )
    effects = models.ManyToManyField(
        Effect, through="CharacterEffect", related_name="character_effects"
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
    kills = models.IntegerField(default=0, verbose_name="Убийств")
    auto_use_hp_potion = models.BooleanField(
        default=False, verbose_name="Автоиспользование эликсиров здоровья"
    )
    auto_use_mp_potion = models.BooleanField(
        default=False, verbose_name="Автоиспользование эликсиров маны"
    )
    pvp_mode_expired = models.DateTimeField(
        default=timezone.now, verbose_name="Окончание PvP режима"
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

    @property
    def name_with_clan(self):
        """Метод получения имени персонажа с кланом."""
        text = ""
        if self.clan:
            if self.clan.emoji:
                text += f"{self.clan.emoji}"
        text += f"{self.name}"
        return text

    @property
    def name_with_class(self):
        """Метод получения имени персонажа с классом и премиумом."""
        text = ""
        if self.premium_expired > timezone.now():
            text += "🔸"
        text += f"{self.name}{self.character_class.emoji}"
        return text

    @property
    def name_with_level(self):
        """Метод получения имени персонажа с уровнем."""
        text = ""
        if self.clan:
            if self.clan.emoji:
                text += f"{self.clan.emoji}"
        text += f"{self.name} Ур. {self.level}"
        return text

    @property
    def name_with_kills(self):
        """Метод получения имени персонажа с убийствами."""
        text = ""
        if self.clan:
            if self.clan.emoji:
                text += f"{self.clan.emoji}"
        text += f"{self.name} 🩸{self.kills}"
        return text

    @property
    def hp(self):
        """Получения здоровье/максимальное здоровье."""
        return f"{self.health}/{self.max_health}"

    @property
    def mp(self):
        """Получения здоровье/максимальное здоровье."""
        return f"{self.mana}/{self.max_mana}"


class CharacterPower(models.Model):
    """Модель для хранения характеристик персонажей."""

    power = models.ForeignKey(
        Power, on_delete=models.CASCADE, verbose_name="Сила"
    )
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, verbose_name="Класс"
    )

    class Meta:
        verbose_name = "Сила персонажа"
        verbose_name_plural = "Силы персонажей"


class CharacterSkill(models.Model):
    """Модель для хранения умений персонажей."""

    skill = models.ForeignKey(
        Skill, on_delete=models.RESTRICT, verbose_name="Умение"
    )
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, verbose_name="Класс"
    )
    turn_on = models.BooleanField(
        default=False, verbose_name="Активирован (Для переключаемых)"
    )
    cooldown = models.DateTimeField(
        default=timezone.now, verbose_name="Перезарядкаа"
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
    enhancement_level = models.IntegerField(
        default=0, verbose_name="Уровень улучшения"
    )

    @property
    def name_with_enhance(self):
        """Возвращает название с уровнем улучшения."""
        if self.enhancement_level:
            return f"{self.item.name_with_type} +{self.enhancement_level}"
        return f"{self.item.name_with_type}"

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
        Effect, on_delete=models.RESTRICT, verbose_name="Эффект"
    )
    expired = models.DateTimeField(
        default=timezone.now, verbose_name="Окончание Эффекта"
    )

    class Meta:
        verbose_name = "Эффект персонажа"
        verbose_name_plural = "Эффекты персонажа"

    def __str__(self):
        return f"Character: {self.character} | " f"Effect: {self.effect}"


class MarketplaceItem(models.Model):
    """Модель для хранения предметов персонажа."""

    seller = models.ForeignKey(
        Character, on_delete=models.CASCADE, verbose_name="Продавец"
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name="Предмет",
        related_name="marketplace_item",
    )
    amount = models.IntegerField(default=0, verbose_name="Количество")
    enhancement_level = models.IntegerField(
        default=0, verbose_name="Уровень улучшения"
    )
    sell_currency = models.ForeignKey(
        Etc,
        on_delete=models.PROTECT,
        default=1,
        verbose_name="Валюта продажи",
        related_name="marketplace_currency",
    )
    price = models.IntegerField(default=1, verbose_name="Стоимость")

    @property
    def name_with_enhance(self):
        """Возвращает название с уровнем улучшения."""
        if self.enhancement_level:
            return f"{self.item.name_with_type} +{self.enhancement_level}"
        return f"{self.item.name_with_type}"

    @property
    def name_with_price_and_amount(self):
        """Возвращает название предмета с ценой и количеством."""
        amount = ""
        price_per_item = int(self.price / self.amount)
        price = f"{price_per_item}{self.sell_currency.emoji}"
        if self.amount > 1:
            amount = f"{self.amount} шт."
            price += " за шт."
        return f"{self.name_with_enhance} {amount} ({price})"

    class Meta:
        verbose_name = "Предмет на Торговой Площадке"
        verbose_name_plural = "Предметы на Торговой Площадке"

    def __str__(self):
        return (
            f"Seller: {self.seller} | "
            f"Item: {self.name_with_enhance} | "
            f"Amount: {self.amount} |"
            f"Price: {self.price}"
        )


class RecipeShare(models.Model):
    """Модель хранения общих рецептов."""

    character_recipe = models.ForeignKey(
        CharacterRecipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт Персонажа",
    )
    price = models.IntegerField(default=0, verbose_name="Цена")

    class Meta:
        verbose_name = "Рецепт на Торговой Площадке"
        verbose_name_plural = "Рецпты на Торговой Площадке"

    def __str__(self):
        return (
            f"Seller: {self.character_recipe.character} | "
            f"Recipe: {self.character_recipe.recipe} | "
            f"Price: {self.price}"
        )
