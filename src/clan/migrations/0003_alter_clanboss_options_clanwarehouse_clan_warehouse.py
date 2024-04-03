# Generated by Django 4.2.10 on 2024-04-03 10:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("item", "0006_alter_effect_property_alter_talisman_talisman_type"),
        ("clan", "0002_clanboss_clanbossdrop_clanboss_drop"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="clanboss",
            options={
                "verbose_name": "Клановый босс",
                "verbose_name_plural": "Клановые боссы",
            },
        ),
        migrations.CreateModel(
            name="ClanWarehouse",
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
                ("amount", models.IntegerField(default=0, verbose_name="Количество")),
                ("equipped", models.BooleanField(default=False, verbose_name="Надето")),
                (
                    "enhancement_level",
                    models.IntegerField(default=0, verbose_name="Уровень улучшения"),
                ),
                (
                    "clan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="clan.clan",
                        verbose_name="Клан",
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
                "verbose_name": "Предмет Клана",
                "verbose_name_plural": "Предметы Клана",
            },
        ),
        migrations.AddField(
            model_name="clan",
            name="warehouse",
            field=models.ManyToManyField(
                related_name="clan_warehouse",
                through="clan.ClanWarehouse",
                to="item.item",
            ),
        ),
    ]