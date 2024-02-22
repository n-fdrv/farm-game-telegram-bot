from django.db import models


class BaseItemModel(models.Model):
    """Базовая модель для моделей предметов."""


class ItemType(models.TextChoices):
    """Типы информационных карт."""

    ARMOR = "armor", "Броня"
    WEAPON = "weapon", "Оружие"
    TALISMAN = "talisman", "Талисман"
    MATERIAL = "material", "Ресурс"
    SCROLL = "scroll", "Свиток"
    ETC = "etc", "Разное"


class ArmorType(models.TextChoices):
    """Типы брони."""

    HEAVY = "heavy", "Тяжелая"
    LIGHT = "light", "Легкая"
    ROBE = "robe", "Ткань"


class WeaponType(models.TextChoices):
    """Типы брони."""

    SWORD = "sword", "Меч"
    STAFF = "staff", "Посох"
    BLUNT = "blunt", "Дубина"
    DAGGER = "dagger", "Кинжал"


class ItemGrade(models.TextChoices):
    """Типы информационных карт."""

    COMMON = "common", "️⚪️ Обычный"
    UNCOMMON = "uncommon", "🟤 Необычный"
    RARE = "rare", "🔵 Редкий"
    LEGENDARY = "legendary", "🟠 Легендарный"
    EPIC = "epic", "🔴 Эпический"


class Item(models.Model):
    """Модель для хранения предметов."""

    name = models.CharField(max_length=32, verbose_name="Имя")
    description = models.CharField(max_length=256, verbose_name="Описание")
    sell_price = models.IntegerField(
        default=0, verbose_name="Стоимость продажи"
    )
    buy_price = models.IntegerField(
        default=0, verbose_name="Стоимость покупки"
    )
    grade = models.CharField(
        max_length=16,
        choices=ItemGrade.choices,
        default=ItemGrade.COMMON,
        verbose_name="Ранг",
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

    def __str__(self):
        return f"{self.name}"

    @property
    def name_with_grade(self):
        """Возвращает полное имя пользователя."""
        return f"{self.get_grade_display()[:2]} {self.name}"


class Armor(Item):
    """Модель хранения брони."""

    type = models.CharField(
        max_length=16,
        choices=ItemType.choices,
        default=ItemType.ARMOR,
        verbose_name="Тип",
    )
    armor_type = models.CharField(
        max_length=16,
        choices=ArmorType.choices,
        default=ArmorType.HEAVY,
        verbose_name="Вид брони",
    )

    class Meta:
        verbose_name = "Броня"
        verbose_name_plural = "Броня"


class Weapon(Item):
    """Модель хранения оружия."""

    type = models.CharField(
        max_length=16,
        choices=ItemType.choices,
        default=ItemType.WEAPON,
        verbose_name="Тип",
    )
    weapon_type = models.CharField(
        max_length=16,
        choices=WeaponType.choices,
        default=WeaponType.SWORD,
        verbose_name="Вид оружия",
    )

    class Meta:
        verbose_name = "Оружие"
        verbose_name_plural = "Оружия"


class Scroll(Item):
    """Модель хранения свитков."""

    type = models.CharField(
        max_length=16,
        choices=ItemType.choices,
        default=ItemType.SCROLL,
        verbose_name="Тип",
    )

    class Meta:
        verbose_name = "Свиток"
        verbose_name_plural = "Свитки"


class Material(Item):
    """Модель хранения ресурсов."""

    type = models.CharField(
        max_length=16,
        choices=ItemType.choices,
        default=ItemType.MATERIAL,
        verbose_name="Тип",
    )

    class Meta:
        verbose_name = "Ресурс"
        verbose_name_plural = "Ресурсы"


class Talisman(Item):
    """Модель хранения свитков."""

    type = models.CharField(
        max_length=16,
        choices=ItemType.choices,
        default=ItemType.TALISMAN,
        verbose_name="Тип",
    )

    class Meta:
        verbose_name = "Талисман"
        verbose_name_plural = "Талисманы"


class Etc(Item):
    """Модель хранения других предметов."""

    type = models.CharField(
        max_length=16,
        choices=ItemType.choices,
        default=ItemType.ETC,
        verbose_name="Тип",
    )

    class Meta:
        verbose_name = "Разное"
        verbose_name_plural = "Разное"
