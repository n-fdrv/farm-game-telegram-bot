# Generated by Django 4.2.10 on 2024-04-25 08:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("location", "0002_huntingzone_type_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dungeoncharacter",
            name="hunting_begin",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2023, 4, 27, 8, 24, 13, 594811, tzinfo=datetime.timezone.utc
                ),
                verbose_name="Начало охоты",
            ),
        ),
    ]
