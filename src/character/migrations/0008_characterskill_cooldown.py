# Generated by Django 4.2.10 on 2024-03-31 15:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("character", "0007_characterskill_turn_on"),
    ]

    operations = [
        migrations.AddField(
            model_name="characterskill",
            name="cooldown",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="Перезарядкаа"
            ),
        ),
    ]
