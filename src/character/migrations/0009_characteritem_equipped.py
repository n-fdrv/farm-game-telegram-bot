# Generated by Django 4.2.10 on 2024-02-29 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("character", "0008_characterrecipe_character_recipes"),
    ]

    operations = [
        migrations.AddField(
            model_name="characteritem",
            name="equipped",
            field=models.BooleanField(default=False, verbose_name="Надето"),
        ),
    ]