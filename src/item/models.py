from django.db import models


class BaseItemModel(models.Model):
    """Базовая модель для моделей предметов."""


class ItemType(models.TextChoices):
    """Типы информационных карт."""

    ARMOR = "armor", "🛡Броня"
    WEAPON = "weapon", "⚔️Оружие"
    POTION = "potion", "🌡Эликсир"
    TALISMAN = "talisman", "⭐️Талисман"
    RECIPE = "recipe", "📕Рецепт"
    MATERIAL = "material", "🪵Ресурс"
    SCROLL = "scroll", "📜Свиток"
    BAG = "bag", "📦Мешок"
    ETC = "etc", "Разное"


class EquipmentType(models.TextChoices):
    """Типы экипировки."""

    HEAVY_ARMOR = "heavy_armor", "Тяжелая Броня"
    LIGHT_ARMOR = "light_armor", "Легкая Броня"
    ROBE_ARMOR = "robe", "Мантия"

    SWORD = "sword", "Меч"
    STAFF = "staff", "Посох"
    BLUNT = "blunt", "Дубина"
    DAGGER = "dagger", "Кинжал"


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
    buy_price = models.IntegerField(
        default=0, verbose_name="Стоимость покупки"
    )
    sell_price = models.IntegerField(
        default=0, verbose_name="Стоимость продажи"
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
    def name_with_type(self):
        """Возвращает полное имя пользователя."""
        if self.type == ItemType.ETC:
            return f"{self.name}"
        return f"{self.get_type_display()[:1]}{self.name}"


class Equipment(Item):
    """Модель хранения предметов которые можно надевать."""

    equipment_type = models.CharField(
        max_length=16,
        choices=EquipmentType.choices,
        default=EquipmentType.HEAVY_ARMOR,
        verbose_name="Вид экипировки",
    )

    class Meta:
        verbose_name = "Броня"
        verbose_name_plural = "Броня"


class Armor(Equipment):
    """Модель хранения брони."""

    pass

    class Meta:
        verbose_name = "Броня"
        verbose_name_plural = "Броня"


class Weapon(Equipment):
    """Модель хранения оружия."""

    pass

    class Meta:
        verbose_name = "Оружие"
        verbose_name_plural = "Оружия"


class Talisman(Item):
    """Модель хранения талисманов."""

    talisman_type = models.CharField(
        max_length=16,
        choices=EffectProperty.choices,
        default=EffectProperty.ATTACK,
        verbose_name="Вид талисмана",
    )

    class Meta:
        verbose_name = "Талисман"
        verbose_name_plural = "Талисманы"


class Potion(Item):
    """Модель хранения свитков."""

    pass

    class Meta:
        verbose_name = "Эликсир"
        verbose_name_plural = "Эликсиры"


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
        return f"{self.name_with_type} ({self.chance}%)"


class Etc(Item):
    """Модель хранения других предметов."""

    pass

    class Meta:
        verbose_name = "Разное"
        verbose_name_plural = "Разное"


class Bag(Item):
    """Модель хранения мешков."""

    pass

    class Meta:
        verbose_name = "Мешок"
        verbose_name_plural = "Мешки"


class BagItem(models.Model):
    """Модель хранения предметов в мешке."""

    item = models.ForeignKey(
        Item,
        on_delete=models.RESTRICT,
        verbose_name="Возможный предмет",
        related_name="item_in_bag",
    )
    bag = models.ForeignKey(
        Bag,
        on_delete=models.RESTRICT,
        verbose_name="Мешок",
        related_name="bag_items",
    )
    chance = models.FloatField(default=1, verbose_name="Шанс")

    class Meta:
        verbose_name = "Предмет в мешке"
        verbose_name_plural = "Предметы в мешке"


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
        text = (
            f"{self.item.name_with_type} | "
            f"{self.get_property_display()}: {self.amount}"
        )
        if self.in_percent:
            text += "%"
        return text

    def get_property_with_amount(self):
        """Получение свойства с количеством."""
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


ITEM_DATA = {
    ItemType.TALISMAN: Talisman,
    ItemType.ETC: Etc,
    ItemType.MATERIAL: Material,
    ItemType.SCROLL: Scroll,
    ItemType.ARMOR: Armor,
    ItemType.WEAPON: Weapon,
    ItemType.RECIPE: Recipe,
}
