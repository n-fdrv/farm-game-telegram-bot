# Generated by Django 4.2.10 on 2024-02-21 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("game", "0007_alter_characteritem_amount"),
    ]

    operations = [
        migrations.AddField(
            model_name="character",
            name="job_id",
            field=models.IntegerField(
                blank=True,
                null=True,
                verbose_name="ID шедулера напоминания об окончании охоты",
            ),
        ),
    ]
