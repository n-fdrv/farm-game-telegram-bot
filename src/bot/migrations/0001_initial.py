# Generated by Django 4.2.10 on 2024-02-20 14:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("game", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "telegram_id",
                    models.BigIntegerField(
                        unique=True, verbose_name="Telegram User ID"
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Имя"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Фамилия"
                    ),
                ),
                (
                    "telegram_username",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Ник в телеграмме",
                    ),
                ),
                (
                    "registration_date",
                    models.DateField(
                        auto_now_add=True, verbose_name="Дата регистрации"
                    ),
                ),
                (
                    "is_admin",
                    models.BooleanField(
                        default=False, verbose_name="Права администратора"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Активен"),
                ),
                (
                    "character",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="game.character",
                        verbose_name="Персонаж",
                    ),
                ),
            ],
            options={
                "verbose_name": "Пользователь",
                "verbose_name_plural": "Пользователи",
            },
        ),
    ]