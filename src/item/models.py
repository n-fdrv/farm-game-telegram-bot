from django.db import models


class BaseItemModel(models.Model):
    """Базовая модель для моделей предметов."""


class ItemType(models.TextChoices):
    """Типы информационных карт."""

    ARMOR = "armor", "Броня"
    WEAPON = "weapon", "Оружие"
    TALISMAN = "talisman", "Талисман"
    RECIPE = "recipe", "Рецепт"
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


class EffectProperty(models.TextChoices):
    """Типы эффектов."""

    ATTACK = "attack", "️⚔️Атака"
    DEFENCE = "defence", "🛡Защита"
    EXP = "exp", "🔮Опыт"
    DROP = "drop", "🍀Выпадение предметов"
    HUNTING_TIME = "hunting_time", "⏳Время охоты"


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
    type = models.CharField(
        max_length=16,
        choices=ItemType.choices,
        default=ItemType.ETC,
        verbose_name="Тип",
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

    pass

    class Meta:
        verbose_name = "Свиток"
        verbose_name_plural = "Свитки"


class Material(Item):
    """Модель хранения ресурсов."""

    pass

    class Meta:
        verbose_name = "Ресурс"
        verbose_name_plural = "Ресурсы"


class Talisman(Item):
    """Модель хранения свитков."""

    pass

    class Meta:
        verbose_name = "Талисман"
        verbose_name_plural = "Талисманы"


class Recipe(Item):
    """Модель хранения рецептов."""

    level = models.IntegerField(default=1, verbose_name="Уровень")
    chance = models.IntegerField(default=100, verbose_name="Шанс изготовления")
    create = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name="Изготавливает",
        related_name="recipe_create",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"{self.name} ({self.chance}%) (Ур. {self.level})"

    def get_name(self):
        """Возвращает имя с шансом."""
        return f"{self.name_with_grade} ({self.chance}%)"


class Etc(Item):
    """Модель хранения других предметов."""

    pass

    class Meta:
        verbose_name = "Разное"
        verbose_name_plural = "Разное"


class ItemEffect(models.Model):
    """Модель хранения эффектов предметов."""

    property = models.CharField(
        max_length=16,
        choices=EffectProperty.choices,
        default=EffectProperty.ATTACK,
        verbose_name="Свойство",
    )
    amount = models.IntegerField(default=0, verbose_name="Количество")
    in_percent = models.BooleanField(default=False, verbose_name="В процентах")
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name="Предмет",
        related_name="effect",
    )

    class Meta:
        verbose_name = "Эффект предмета"
        verbose_name_plural = "Эффекты предметов"

    def __str__(self):
        text = f"{self.get_property_display()}: {self.amount}"
        if self.in_percent:
            text += "%"
        return text


class CraftingItem(models.Model):
    """Модель хранения предметов рецепта."""

    material = models.ForeignKey(
        to=Material,
        on_delete=models.RESTRICT,
        verbose_name="Предмет",
        related_name="recipes",
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="materials",
    )
    amount = models.IntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Предмет изготовлени"
        verbose_name_plural = "Предметы изготовления"

    def __str__(self):
        return f"{self.recipe} | {self.material.name}"
