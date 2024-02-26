# Generated by Django 4.2.10 on 2024-02-26 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("character", "0003_characterclass_armor_type_characterclass_weapon_type"),
        ("bot", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
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
