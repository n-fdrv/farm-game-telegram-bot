# Generated by Django 4.2.10 on 2024-04-17 07:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("item", "0010_alter_effect_property_alter_talisman_talisman_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bagitem",
            name="bag",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bag_items",
                to="item.bag",
                verbose_name="Мешок",
            ),
        ),
        migrations.AlterField(
            model_name="bagitem",
            name="item",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="item_in_bag",
                to="item.item",
                verbose_name="Возможный предмет",
            ),
        ),
        migrations.AlterField(
            model_name="effect",
            name="property",
            field=models.CharField(
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
        migrations.AlterField(
            model_name="itemeffect",
            name="effect",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="item.effect",
                verbose_name="Эффект",
            ),
        ),
        migrations.AlterField(
            model_name="itemeffect",
            name="item",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="item.item",
                verbose_name="Предмет",
            ),
        ),
        migrations.AlterField(
            model_name="talisman",
            name="talisman_type",
            field=models.CharField(
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
    ]
