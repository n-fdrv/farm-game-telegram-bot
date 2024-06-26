# Generated by Django 4.2.10 on 2024-04-25 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("premium_shop", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="premiumlot",
            options={
                "verbose_name": "Премиум Лот",
                "verbose_name_plural": "Премиум Лоты",
            },
        ),
        migrations.AlterModelOptions(
            name="premiumlotreceiveditem",
            options={
                "verbose_name": "Получаемый Предмет",
                "verbose_name_plural": "Получаемые Предметы",
            },
        ),
        migrations.AlterModelOptions(
            name="premiumlotrequireditem",
            options={
                "verbose_name": "Необходимый Предмет",
                "verbose_name_plural": "Необходимые Предметы",
            },
        ),
        migrations.AddField(
            model_name="premiumlot",
            name="type",
            field=models.CharField(
                choices=[
                    ("premium", "🎟Премиум"),
                    ("skill", "🎒Наборы"),
                    ("event", "🎁Акции"),
                ],
                default="event",
                max_length=16,
                verbose_name="Тип",
            ),
        ),
    ]
