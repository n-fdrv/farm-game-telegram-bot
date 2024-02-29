# Generated by Django 4.2.10 on 2024-02-27 13:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("item", "0002_itemeffect"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="crafting_level",
            field=models.IntegerField(default=0, verbose_name="Уровень создания"),
        ),
        migrations.CreateModel(
            name="CraftingItems",
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
                    "crafting_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="crafting",
                        to="item.material",
                        verbose_name="Изготовленный предмет",
                    ),
                ),
                (
                    "used_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="used_in_craft",
                        to="item.item",
                        verbose_name="Необходимый предмет",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="item",
            name="crafting_items",
            field=models.ManyToManyField(
                through="item.CraftingItems",
                to="item.item",
                verbose_name="Предметы для крафта",
            ),
        ),
    ]