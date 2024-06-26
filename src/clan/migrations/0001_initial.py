# Generated by Django 4.2.10 on 2024-04-18 10:27

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("item", "0001_initial"),
        ("character", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Clan",
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
                    "name",
                    models.CharField(
                        max_length=16, unique=True, verbose_name="Название"
                    ),
                ),
                (
                    "emoji",
                    models.CharField(
                        blank=True, max_length=4, null=True, verbose_name="Эмоджи"
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        default="Нет описания", max_length=128, verbose_name="Описание"
                    ),
                ),
                ("level", models.IntegerField(default=1, verbose_name="Уровень")),
                (
                    "reputation",
                    models.IntegerField(default=0, verbose_name="Репутация"),
                ),
                ("place", models.IntegerField(default=10, verbose_name="Мест в клане")),
                (
                    "by_request",
                    models.BooleanField(default=True, verbose_name="Вход по заявкам"),
                ),
                (
                    "leader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="clan_leader",
                        to="character.character",
                        verbose_name="Лидер",
                    ),
                ),
            ],
            options={
                "verbose_name": "Клан",
                "verbose_name_plural": "Кланы",
            },
        ),
        migrations.CreateModel(
            name="ClanBoss",
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
                ("name", models.CharField(max_length=16, verbose_name="Имя")),
                (
                    "respawn",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="Время Респауна"
                    ),
                ),
                (
                    "required_power",
                    models.IntegerField(
                        default=100, verbose_name="Необходимая сила клана"
                    ),
                ),
            ],
            options={
                "verbose_name": "Клановый босс",
                "verbose_name_plural": "Клановые боссы",
            },
        ),
        migrations.CreateModel(
            name="ClanWarehouse",
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
                ("amount", models.IntegerField(default=0, verbose_name="Количество")),
                ("equipped", models.BooleanField(default=False, verbose_name="Надето")),
                (
                    "enhancement_level",
                    models.IntegerField(default=0, verbose_name="Уровень улучшения"),
                ),
                (
                    "clan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="clan.clan",
                        verbose_name="Клан",
                    ),
                ),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="item.item",
                        verbose_name="Предмет",
                    ),
                ),
            ],
            options={
                "verbose_name": "Предмет Клана",
                "verbose_name_plural": "Предметы Клана",
            },
        ),
        migrations.CreateModel(
            name="ClanWar",
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
                    "accepted",
                    models.BooleanField(default=False, verbose_name="Война принята"),
                ),
                (
                    "clan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="war_sent",
                        to="clan.clan",
                        verbose_name="Клан",
                    ),
                ),
                (
                    "enemy",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="war_request",
                        to="clan.clan",
                        verbose_name="Враг",
                    ),
                ),
            ],
            options={
                "verbose_name": "Клановая война",
                "verbose_name_plural": "Клановые войны",
            },
        ),
        migrations.CreateModel(
            name="ClanRequest",
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
                    "text",
                    models.TextField(
                        blank=True,
                        max_length=256,
                        null=True,
                        verbose_name="Текст заявки",
                    ),
                ),
                (
                    "character",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.character",
                        verbose_name="Персонаж",
                    ),
                ),
                (
                    "clan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="clan.clan",
                        verbose_name="Клан",
                    ),
                ),
            ],
            options={
                "verbose_name": "Заявка",
                "verbose_name_plural": "Заявки",
            },
        ),
        migrations.CreateModel(
            name="ClanBossDrop",
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
                    "min_amount",
                    models.IntegerField(
                        default=1, verbose_name="Минимальное количество"
                    ),
                ),
                (
                    "max_amount",
                    models.IntegerField(
                        default=1, verbose_name="Максимальное количество"
                    ),
                ),
                (
                    "chance",
                    models.FloatField(
                        default=1, verbose_name="Шанс в процентах в минуту"
                    ),
                ),
                (
                    "clan_boss",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="clan.clanboss",
                        verbose_name="Клановый босс",
                    ),
                ),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="item.item",
                        verbose_name="Предмет",
                    ),
                ),
            ],
            options={
                "verbose_name": "Трофей с босса",
                "verbose_name_plural": "Трофеи с босса",
            },
        ),
        migrations.CreateModel(
            name="ClanBossClan",
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
                    "boss",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="clan.clanboss",
                        verbose_name="Клановый босс",
                    ),
                ),
                (
                    "clan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="clan.clan",
                        verbose_name="Клан в рейде",
                    ),
                ),
            ],
            options={
                "verbose_name": "Клан в рейде",
                "verbose_name_plural": "Кланы в рейде",
            },
        ),
        migrations.CreateModel(
            name="ClanBossCharacter",
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
                    "boss",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="clan.clanboss",
                        verbose_name="Клановый босс",
                    ),
                ),
                (
                    "character",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.character",
                        verbose_name="Персонаж в рейде",
                    ),
                ),
            ],
            options={
                "verbose_name": "Персонаж в рейде",
                "verbose_name_plural": "Персонажи в рейде",
            },
        ),
        migrations.AddField(
            model_name="clanboss",
            name="characters",
            field=models.ManyToManyField(
                through="clan.ClanBossCharacter", to="character.character"
            ),
        ),
        migrations.AddField(
            model_name="clanboss",
            name="clans",
            field=models.ManyToManyField(through="clan.ClanBossClan", to="clan.clan"),
        ),
        migrations.AddField(
            model_name="clanboss",
            name="drop",
            field=models.ManyToManyField(
                related_name="clan_boss_drop",
                through="clan.ClanBossDrop",
                to="item.item",
            ),
        ),
        migrations.AddField(
            model_name="clan",
            name="requests",
            field=models.ManyToManyField(
                related_name="clan_request",
                through="clan.ClanRequest",
                to="character.character",
                verbose_name="Заявки",
            ),
        ),
        migrations.AddField(
            model_name="clan",
            name="warehouse",
            field=models.ManyToManyField(
                related_name="clan_warehouse",
                through="clan.ClanWarehouse",
                to="item.item",
            ),
        ),
        migrations.AddField(
            model_name="clan",
            name="wars",
            field=models.ManyToManyField(
                through="clan.ClanWar", to="clan.clan", verbose_name="Войны"
            ),
        ),
    ]
