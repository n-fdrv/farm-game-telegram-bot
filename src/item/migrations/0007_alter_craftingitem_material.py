# Generated by Django 4.2.10 on 2024-04-08 13:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("item", "0006_alter_effect_property_alter_talisman_talisman_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="craftingitem",
            name="material",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="recipes",
                to="item.item",
                verbose_name="Предмет",
            ),
        ),
    ]
