# Generated by Django 4.2.10 on 2024-04-25 08:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("character", "0002_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="character",
            name="auto_use_hp_potion",
        ),
        migrations.RemoveField(
            model_name="character",
            name="auto_use_mp_potion",
        ),
    ]
