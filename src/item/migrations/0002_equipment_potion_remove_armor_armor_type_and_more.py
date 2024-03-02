# Generated by Django 4.2.10 on 2024-03-02 13:28

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("item", "0001_initial"),
    ]

    operations = [
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
        migrations.RemoveField(
            model_name="armor",
            name="armor_type",
        ),
        migrations.RemoveField(
            model_name="armor",
            name="item_ptr",
        ),
        migrations.RemoveField(
            model_name="armor",
            name="type",
        ),
        migrations.RemoveField(
            model_name="etc",
            name="type",
        ),
        migrations.RemoveField(
            model_name="material",
            name="type",
        ),
        migrations.RemoveField(
            model_name="scroll",
            name="type",
        ),
        migrations.RemoveField(
            model_name="talisman",
            name="type",
        ),
        migrations.RemoveField(
            model_name="weapon",
            name="item_ptr",
        ),
        migrations.RemoveField(
            model_name="weapon",
            name="type",
        ),
        migrations.RemoveField(
            model_name="weapon",
            name="weapon_type",
        ),
        migrations.AddField(
            model_name="item",
            name="type",
            field=models.CharField(
                choices=[
                    ("armor", "Броня"),
                    ("weapon", "Оружие"),
                    ("potion", "Эликсир"),
                    ("talisman", "Талисман"),
                    ("recipe", "Рецепт"),
                    ("material", "Ресурс"),
                    ("scroll", "Свиток"),
                    ("etc", "Разное"),
                ],
                default="etc",
                max_length=16,
                verbose_name="Тип",
            ),
        ),
        migrations.AddField(
            model_name="talisman",
            name="talisman_type",
            field=models.CharField(
                choices=[
                    ("attack", "️⚔️Атака"),
                    ("defence", "🛡Защита"),
                    ("exp", "🔮Опыт"),
                    ("drop", "🍀Выпадение предметов"),
                    ("hunting_time", "⏳Время охоты"),
                ],
                default="attack",
                max_length=16,
                verbose_name="Вид талисмана",
            ),
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
                    "property",
                    models.CharField(
                        choices=[
                            ("attack", "️⚔️Атака"),
                            ("defence", "🛡Защита"),
                            ("exp", "🔮Опыт"),
                            ("drop", "🍀Выпадение предметов"),
                            ("hunting_time", "⏳Время охоты"),
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
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="effect",
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
                        to="item.material",
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
        migrations.AddField(
            model_name="armor",
            name="equipment_ptr",
            field=models.OneToOneField(
                auto_created=True,
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="item.equipment",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="weapon",
            name="equipment_ptr",
            field=models.OneToOneField(
                auto_created=True,
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="item.equipment",
            ),
            preserve_default=False,
        ),
    ]