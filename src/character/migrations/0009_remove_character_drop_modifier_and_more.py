# Generated by Django 4.2.10 on 2024-03-31 16:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("character", "0008_characterskill_cooldown"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="character",
            name="drop_modifier",
        ),
        migrations.RemoveField(
            model_name="character",
            name="exp_modifier",
        ),
    ]
