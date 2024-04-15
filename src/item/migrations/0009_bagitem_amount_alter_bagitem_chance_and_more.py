# Generated by Django 4.2.10 on 2024-04-15 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("item", "0008_bracelet"),
    ]

    operations = [
        migrations.AddField(
            model_name="bagitem",
            name="amount",
            field=models.IntegerField(default=1, verbose_name="Количество"),
        ),
        migrations.AlterField(
            model_name="bagitem",
            name="chance",
            field=models.IntegerField(default=1, verbose_name="Шанс"),
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
                    ("hunting_time", "⏳Время охоты"),
                    ("pvp", "🩸Урон в PvP"),
                    ("talisman_amount", "⭐️Количество Талисманов"),
                    ("mass_attack", "⚡️Массовая Атака"),
                    ("no_death_exp", "🪦Без потери опыта при смерти"),
                    ("evasion", "🥾Уклонение"),
                    ("invisible", "💨Невидимость"),
                ],
                default="attack",
                max_length=16,
                verbose_name="Свойство",
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="type",
            field=models.CharField(
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
        migrations.AlterField(
            model_name="scroll",
            name="enhance_type",
            field=models.CharField(
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
                    ("hunting_time", "⏳Время охоты"),
                    ("pvp", "🩸Урон в PvP"),
                    ("talisman_amount", "⭐️Количество Талисманов"),
                    ("mass_attack", "⚡️Массовая Атака"),
                    ("no_death_exp", "🪦Без потери опыта при смерти"),
                    ("evasion", "🥾Уклонение"),
                    ("invisible", "💨Невидимость"),
                ],
                default="attack",
                max_length=16,
                verbose_name="Вид талисмана",
            ),
        ),
    ]
