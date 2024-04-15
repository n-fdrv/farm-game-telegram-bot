import datetime

from django.db import models


class ItemType(models.TextChoices):
    """Типы информационных карт."""

    ARMOR = "armor", "🛡Броня"
    BRACELET = "bracelet", "💍Браслет"
    BOOK = "book", "📕Книга"
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

    BRACELET = "bracelet", "Браслет"


class EffectProperty(models.TextChoices):
    """Типы эффектов."""

    ATTACK = "attack", "️⚔️Атака"
    DEFENCE = "defence", "🛡Защита"
    HEALTH = "health", "❤️Пополнение Здоровья"
    MAX_HEALTH = "max_health", "❤️Увеличение Здоровья"
    MANA = "mana", "🔷Пополнение Маны"
    MAX_MANA = "max_mana", "🔷Увеличение Маны"
    EXP = "exp", "🔮Опыт"
    DROP = "drop", "🍀Выпадение предметов"
    HUNTING_TIME = "hunting_time", "⏳Время охоты"
    PVP = "pvp", "🩸Урон в PvP"
    TALISMAN_AMOUNT = "talisman_amount", "⭐️Количество Талисманов"
    MASS_ATTACK = "mass_attack", "⚡️Массовая Атака"
    NO_DEATH_EXP = "no_death_exp", "🪦Без потери опыта при смерти"
    EVASION = "evasion", "🥾Уклонение"
    INVISIBLE = "invisible", "💨Невидимость"


class EffectSlug(models.TextChoices):
    """Slug эффектов."""

    POTION = "potion", "🌡Эликсир"
    SKILL = "skill", "↗️Способность"
    ITEM = "item", "🎒Предмет"
    FATIGUE = "fatigue", "♦️Усталость"


class Item(models.Model):
    """Модель для хранения предметов."""

    name = models.CharField(max_length=32, verbose_name="Имя")
    description = models.CharField(
        max_length=256,
        default="Нет описания предмета",
        verbose_name="Описание",
    )
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
    effects = models.ManyToManyField(
        "Effect", through="ItemEffect", verbose_name="Эффекты предметов"
    )

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

    def __str__(self):
        if self.type == ItemType.ETC:
            return f"{self.name}"
        return f"{self.get_type_display()[:1]}{self.name}"

    @property
    def name_with_type(self):
        """Возвращает полное имя пользователя."""
        if self.type == ItemType.ETC:
            return f"{self.name}"
        return f"{self.get_type_display()[:1]}{self.name}"

    @property
    def emoji(self):
        """Возвращает полное имя пользователя."""
        if self.type == ItemType.ETC:
            return f"{self.name[:1]}"
        return f"{self.get_type_display()[:1]}"


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


class Bracelet(Equipment):
    """Модель хранения оружия."""

    pass

    class Meta:
        verbose_name = "Браслет"
        verbose_name_plural = "Браслеты"


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

    effect_time = models.TimeField(
        default=datetime.time(hour=12), verbose_name="Время действия"
    )

    class Meta:
        verbose_name = "Эликсир"
        verbose_name_plural = "Эликсиры"


class Scroll(Item):
    """Модель хранения свитков."""

    enhance_type = models.CharField(
        max_length=16,
        choices=ItemType.choices,
        default=ItemType.WEAPON,
        verbose_name="Улучшаемый тип",
    )

    class Meta:
        verbose_name = "Свиток"
        verbose_name_plural = "Свитки"


class Material(Item):
    """Модель хранения ресурсов."""

    pass

    class Meta:
        verbose_name = "Ресурс"
        verbose_name_plural = "Ресурсы"


class Book(Item):
    """Модель хранения книг."""

    character_class = models.ForeignKey(
        to="character.CharacterClass",
        on_delete=models.CASCADE,
        verbose_name="Требуемый класс",
        null=True,
        blank=True,
    )
    required_level = models.IntegerField(
        default=1, verbose_name="Требуемый уровень"
    )
    required_skill = models.ForeignKey(
        to="character.Skill",
        on_delete=models.CASCADE,
        verbose_name="Требуемое умение",
        null=True,
        blank=True,
        related_name="book_required",
    )
    skill = models.ForeignKey(
        to="character.Skill",
        on_delete=models.CASCADE,
        verbose_name="Получаемое умение",
        null=True,
        blank=True,
        related_name="book_give",
    )

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"


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

    @property
    def name_with_chance(self):
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
    chance = models.IntegerField(default=1, verbose_name="Шанс")
    amount = models.IntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Предмет в мешке"
        verbose_name_plural = "Предметы в мешке"

    def __str__(self):
        return f"Bag: {self.bag} | Item: {self.item} | Chance: {self.chance}%"


class Effect(models.Model):
    """Модель хранения эффектов."""

    property = models.CharField(
        max_length=16,
        choices=EffectProperty.choices,
        default=EffectProperty.ATTACK,
        verbose_name="Свойство",
    )
    amount = models.IntegerField(default=0, verbose_name="Количество")
    in_percent = models.BooleanField(default=False, verbose_name="В процентах")
    slug = models.CharField(
        max_length=16,
        choices=EffectSlug.choices,
        default=EffectSlug.POTION,
        verbose_name="Вид эффекта",
    )

    class Meta:
        verbose_name = "Эффект"
        verbose_name_plural = "Эффекты"

    def __str__(self):
        item = (
            Item.objects.values_list("name", flat=True)
            .filter(effects=self)
            .all()
        )
        text = (
            f"{' | '.join(item)} -"
            f" {self.get_property_display()}: {self.amount}"
        )
        if self.in_percent:
            text += "%"
        return text

    def get_property_with_amount(self):
        """Получение свойства с количеством."""
        amount = f": <b>{self.amount}</b>"
        if not self.amount and self.in_percent:
            amount = ""
        text = f"{self.get_property_display()} {amount}"
        if self.in_percent and amount:
            text += "%"
        return text


class ItemEffect(models.Model):
    """Модель хранения эффектов предметов."""

    item = models.ForeignKey(
        Item, on_delete=models.RESTRICT, verbose_name="Предмет"
    )
    effect = models.ForeignKey(
        Effect, on_delete=models.RESTRICT, verbose_name="Эффект"
    )

    class Meta:
        verbose_name = "Эффект предмета"
        verbose_name_plural = "Эффекты предметов"

    def __str__(self):
        return f"{self.item} {self.effect}"


class CraftingItem(models.Model):
    """Модель хранения предметов рецепта."""

    material = models.ForeignKey(
        to=Item,
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
