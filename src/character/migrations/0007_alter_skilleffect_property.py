# Generated by Django 4.2.10 on 2024-02-28 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("character", "0006_characterclass_emoji"),
    ]

    operations = [
        migrations.AlterField(
            model_name="skilleffect",
            name="property",
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
                verbose_name="Свойство",
            ),
        ),
    ]
