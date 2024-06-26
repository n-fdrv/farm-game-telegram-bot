# Generated by Django 4.2.10 on 2024-04-18 10:27

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("character", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Effect",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "property",
                    models.CharField(
                        choices=[
                            ("attack", "️⚔️Атака"),
                            ("defence", "🛡Защита"),
                            ("health", "❤️Пополнение Здоровья"),
                            ("max_health", "❤️Увеличение Здоровья"),
                            ("mana", "🔷Пополнение Маны"),
                            ("max_mana", "🔷Увеличение Маны"),
                            ("exp", "🔮Опыт"),
                            ("drop", "🍀Выпадение предметов"),
                            ("pvp", "🩸Урон в PvP"),
                            ("talisman_amount", "⭐️Количество Талисманов"),
                            ("mass_attack", "⚡️Массовая Атака"),
                            ("no_death_exp", "🪦Без потери опыта при смерти"),
                            ("evasion", "🥾Уклонение"),
                            ("accuracy", "🎯Точность"),
                            ("crit_race", "🎲Шанс Критического Удара"),
                            ("crit_power", "♦️Сила Критического Удара"),
                            ("invisible", "💨Невидимость"),
                        ],
                        default="attack",
                        max_length=16,
                        verbose_name="Свойство",
                    ),
                ),
                ("amount", models.IntegerField(default=0, verbose_name="Количество")),
                (
                    "in_percent",
                    models.BooleanField(default=False, verbose_name="В процентах"),
                ),
                (
                    "slug",
                    models.CharField(
                        choices=[
                            ("potion", "🌡Эликсир"),
                            ("skill", "↗️Способность"),
                            ("item", "🎒Предмет"),
                            ("fatigue", "♦️Усталость"),
                            ("power", "⚡️Сила"),
                        ],
                        default="potion",
                        max_length=16,
                        verbose_name="Вид эффекта",
                    ),
                ),
            ],
            options={
                "verbose_name": "Эффект",
                "verbose_name_plural": "Эффекты",
            },
        ),
        migrations.CreateModel(
            name="Item",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=32, verbose_name="Имя")),
                (
                    "description",
                    models.CharField(
                        default="Нет описания предмета",
                        max_length=256,
                        verbose_name="Описание",
                    ),
                ),
                (
                    "buy_price",
                    models.IntegerField(default=0, verbose_name="Стоимость покупки"),
                ),
                (
                    "sell_price",
                    models.IntegerField(default=0, verbose_name="Стоимость продажи"),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("armor", "🛡Броня"),
                            ("bracelet", "💍Браслет"),
                            ("book", "📕Книга"),
                            ("weapon", "⚔️Оружие"),
                            ("potion", "🌡Эликсир"),
                            ("talisman", "⭐️Талисман"),
                            ("recipe", "📕Рецепт"),
                            ("material", "🪵Ресурс"),
                            ("scroll", "📜Свиток"),
                            ("bag", "📦Мешок"),
                            ("etc", "Разное"),
                        ],
                        default="etc",
                        max_length=16,
                        verbose_name="Тип",
                    ),
                ),
            ],
            options={
                "verbose_name": "Предмет",
                "verbose_name_plural": "Предметы",
            },
        ),
        migrations.CreateModel(
            name="Bag",
            fields=[
                (
                    "item_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="item.item",
                    ),
                ),
            ],
            options={
                "verbose_name": "Мешок",
                "verbose_name_plural": "Мешки",
            },
            bases=("item.item",),
        ),
        migrations.CreateModel(
            name="Equipment",
            fields=[
                (
                    "item_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="item.item",
                    ),
                ),
                (
                    "equipment_type",
                    models.CharField(
                        choices=[
                            ("heavy_armor", "Тяжелая Броня"),
                            ("light_armor", "Легкая Броня"),
                            ("robe", "Мантия"),
                            ("sword", "Меч"),
                            ("staff", "Посох"),
                            ("blunt", "Дубина"),
                            ("dagger", "Кинжал"),
                            ("bracelet", "Браслет"),
                        ],
                        default="heavy_armor",
                        max_length=16,
                        verbose_name="Вид экипировки",
                    ),
                ),
            ],
            options={
                "verbose_name": "Броня",
                "verbose_name_plural": "Броня",
            },
            bases=("item.item",),
        ),
        migrations.CreateModel(
            name="Etc",
            fields=[
                (
                    "item_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="item.item",
                    ),
                ),
            ],
            options={
                "verbose_name": "Разное",
                "verbose_name_plural": "Разное",
            },
            bases=("item.item",),
        ),
        migrations.CreateModel(
            name="Material",
            fields=[
                (
                    "item_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="item.item",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ресурс",
                "verbose_name_plural": "Ресурсы",
            },
            bases=("item.item",),
        ),
        migrations.CreateModel(
            name="Potion",
            fields=[
                (
                    "item_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="item.item",
                    ),
                ),
                (
                    "effect_time",
                    models.TimeField(
                        default=datetime.time(12, 0), verbose_name="Время действия"
                    ),
                ),
            ],
            options={
                "verbose_name": "Эликсир",
                "verbose_name_plural": "Эликсиры",
            },
            bases=("item.item",),
        ),
        migrations.CreateModel(
            name="Scroll",
            fields=[
                (
                    "item_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="item.item",
                    ),
                ),
                (
                    "enhance_type",
                    models.CharField(
                        choices=[
                            ("armor", "🛡Броня"),
                            ("bracelet", "💍Браслет"),
                            ("book", "📕Книга"),
                            ("weapon", "⚔️Оружие"),
                            ("potion", "🌡Эликсир"),
                            ("talisman", "⭐️Талисман"),
                            ("recipe", "📕Рецепт"),
                            ("material", "🪵Ресурс"),
                            ("scroll", "📜Свиток"),
                            ("bag", "📦Мешок"),
                            ("etc", "Разное"),
                        ],
                        default="weapon",
                        max_length=16,
                        verbose_name="Улучшаемый тип",
                    ),
                ),
            ],
            options={
                "verbose_name": "Свиток",
                "verbose_name_plural": "Свитки",
            },
            bases=("item.item",),
        ),
        migrations.CreateModel(
            name="Talisman",
            fields=[
                (
                    "item_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="item.item",
                    ),
                ),
                (
                    "talisman_type",
                    models.CharField(
                        choices=[
                            ("attack", "️⚔️Атака"),
                            ("defence", "🛡Защита"),
                            ("health", "❤️Пополнение Здоровья"),
                            ("max_health", "❤️Увеличение Здоровья"),
                            ("mana", "🔷Пополнение Маны"),
                            ("max_mana", "🔷Увеличение Маны"),
                            ("exp", "🔮Опыт"),
                            ("drop", "🍀Выпадение предметов"),
                            ("pvp", "🩸Урон в PvP"),
                            ("talisman_amount", "⭐️Количество Талисманов"),
                            ("mass_attack", "⚡️Массовая Атака"),
                            ("no_death_exp", "🪦Без потери опыта при смерти"),
                            ("evasion", "🥾Уклонение"),
                            ("accuracy", "🎯Точность"),
                            ("crit_race", "🎲Шанс Критического Удара"),
                            ("crit_power", "♦️Сила Критического Удара"),
                            ("invisible", "💨Невидимость"),
                        ],
                        default="attack",
                        max_length=16,
                        verbose_name="Вид талисмана",
                    ),
                ),
            ],
            options={
                "verbose_name": "Талисман",
                "verbose_name_plural": "Талисманы",
            },
            bases=("item.item",),
        ),
        migrations.CreateModel(
            name="ItemEffect",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "effect",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="item.effect",
                        verbose_name="Эффект",
                    ),
                ),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="item.item",
                        verbose_name="Предмет",
                    ),
                ),
            ],
            options={
                "verbose_name": "Эффект предмета",
                "verbose_name_plural": "Эффекты предметов",
            },
        ),
        migrations.AddField(
            model_name="item",
            name="effects",
            field=models.ManyToManyField(
                through="item.ItemEffect",
                to="item.effect",
                verbose_name="Эффекты предметов",
            ),
        ),
        migrations.CreateModel(
            name="Armor",
            fields=[
                (
                    "equipment_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="item.equipment",
                    ),
                ),
            ],
            options={
                "verbose_name": "Броня",
                "verbose_name_plural": "Броня",
            },
            bases=("item.equipment",),
        ),
        migrations.CreateModel(
            name="Bracelet",
            fields=[
                (
                    "equipment_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="item.equipment",
                    ),
                ),
            ],
            options={
                "verbose_name": "Браслет",
                "verbose_name_plural": "Браслеты",
            },
            bases=("item.equipment",),
        ),
        migrations.CreateModel(
            name="Weapon",
            fields=[
                (
                    "equipment_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="item.equipment",
                    ),
                ),
            ],
            options={
                "verbose_name": "Оружие",
                "verbose_name_plural": "Оружия",
            },
            bases=("item.equipment",),
        ),
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "item_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="item.item",
                    ),
                ),
                ("level", models.IntegerField(default=1, verbose_name="Уровень")),
                (
                    "chance",
                    models.IntegerField(default=100, verbose_name="Шанс изготовления"),
                ),
                (
                    "create",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipe_create",
                        to="item.item",
                        verbose_name="Изготавливает",
                    ),
                ),
            ],
            options={
                "verbose_name": "Рецепт",
                "verbose_name_plural": "Рецепты",
            },
            bases=("item.item",),
        ),
        migrations.CreateModel(
            name="CraftingItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.IntegerField(default=1, verbose_name="Количество")),
                (
                    "material",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="recipes",
                        to="item.item",
                        verbose_name="Предмет",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="materials",
                        to="item.recipe",
                        verbose_name="Рецепт",
                    ),
                ),
            ],
            options={
                "verbose_name": "Предмет изготовлени",
                "verbose_name_plural": "Предметы изготовления",
            },
        ),
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "item_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="item.item",
                    ),
                ),
                (
                    "required_level",
                    models.IntegerField(default=1, verbose_name="Требуемый уровень"),
                ),
                (
                    "character_class",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.characterclass",
                        verbose_name="Требуемый класс",
                    ),
                ),
                (
                    "required_skill",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="book_required",
                        to="character.skill",
                        verbose_name="Требуемое умение",
                    ),
                ),
                (
                    "skill",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="book_give",
                        to="character.skill",
                        verbose_name="Получаемое умение",
                    ),
                ),
            ],
            options={
                "verbose_name": "Книга",
                "verbose_name_plural": "Книги",
            },
            bases=("item.item",),
        ),
        migrations.CreateModel(
            name="BagItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("chance", models.IntegerField(default=1, verbose_name="Шанс")),
                ("amount", models.IntegerField(default=1, verbose_name="Количество")),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="item_in_bag",
                        to="item.item",
                        verbose_name="Возможный предмет",
                    ),
                ),
                (
                    "bag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bag_items",
                        to="item.bag",
                        verbose_name="Мешок",
                    ),
                ),
            ],
            options={
                "verbose_name": "Предмет в мешке",
                "verbose_name_plural": "Предметы в мешке",
            },
        ),
    ]
