# Generated by Django 4.2.10 on 2024-04-18 12:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("location", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="huntingzone",
            name="type",
            field=models.CharField(
                choices=[("location", "📍Локация"), ("dungeon", "☠️Подземелье")],
                default="location",
                max_length=16,
                verbose_name="Тип",
            ),
        ),
        migrations.AlterField(
            model_name="dungeoncharacter",
            name="hunting_begin",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2023, 4, 20, 12, 3, 6, 873826, tzinfo=datetime.timezone.utc
                ),
                verbose_name="Начало охоты",
            ),
        ),
    ]
