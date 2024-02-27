# Generated by Django 4.2.10 on 2024-02-27 09:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("character", "0003_characterclass_armor_type_characterclass_weapon_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="Skill",
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
                ("name", models.CharField(max_length=32, verbose_name="Название")),
                ("description", models.TextField(verbose_name="Описание")),
                ("level", models.IntegerField(default=1, verbose_name="Уровень")),
            ],
            options={
                "verbose_name": "Умение",
                "verbose_name_plural": "Умения",
            },
        ),
        migrations.AlterField(
            model_name="character",
            name="exp_for_level_up",
            field=models.IntegerField(
                default=500, verbose_name="Опыт для достижения уровня"
            ),
        ),
        migrations.CreateModel(
            name="SkillEffect",
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
                    "property",
                    models.CharField(
                        choices=[
                            ("attack", "️Атака"),
                            ("defence", "Защита"),
                            ("exp", "Опыт"),
                            ("drop", "Выпадение предметов"),
                            ("hunting_time", "Время охоты"),
                        ],
                        default="attack",
                        max_length=16,
                        verbose_name="Свойство",
                    ),
                ),
                ("amount", models.IntegerField(default=0, verbose_name="Количество")),
                (
                    "in_percent",
                    models.BooleanField(default=False, verbose_name="В процентах"),
                ),
                (
                    "skill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="effect",
                        to="character.skill",
                        verbose_name="Умение",
                    ),
                ),
            ],
            options={
                "verbose_name": "Эффект",
                "verbose_name_plural": "Эффекты",
            },
        ),
        migrations.CreateModel(
            name="CharacterSkill",
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
                    "character",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.character",
                        verbose_name="Класс",
                    ),
                ),
                (
                    "skill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="character.skill",
                        verbose_name="Умение",
                    ),
                ),
            ],
            options={
                "verbose_name": "Умение персонажа",
                "verbose_name_plural": "Умения персонажей",
            },
        ),
        migrations.CreateModel(
            name="CharacterClassSkill",
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
                    "character_class",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.characterclass",
                        verbose_name="Класс",
                    ),
                ),
                (
                    "skill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="character.skill",
                        verbose_name="Умение",
                    ),
                ),
            ],
            options={
                "verbose_name": "Умение класса",
                "verbose_name_plural": "Умения классов",
            },
        ),
        migrations.AddField(
            model_name="character",
            name="skills",
            field=models.ManyToManyField(
                related_name="character_skills",
                through="character.CharacterSkill",
                to="character.skill",
            ),
        ),
        migrations.AddField(
            model_name="characterclass",
            name="skills",
            field=models.ManyToManyField(
                related_name="class_skills",
                through="character.CharacterClassSkill",
                to="character.skill",
            ),
        ),
    ]
