# Generated by Django 4.2.10 on 2024-04-18 10:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("character", "0001_initial"),
        ("bot", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="character",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="user",
                to="character.character",
                verbose_name="Персонаж",
            ),
        ),
    ]
