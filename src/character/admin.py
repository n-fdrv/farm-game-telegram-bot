import csv

from django.contrib import admin
from django_object_actions import DjangoObjectActions

from character.models import (
    Character,
    CharacterClass,
    CharacterClassSkill,
    ClassEquipment,
    MarketplaceItem,
    Skill,
    SkillEffect,
)


class CharacterSkillInline(admin.TabularInline):
    """Инлайн модель умений персонажа."""

    model = Character.skills.through
    extra = 1


class ClassSkillInline(admin.TabularInline):
    """Инлайн модель умений классов."""

    model = CharacterClass.skills.through
    extra = 1


class ClassEquipmentInline(admin.TabularInline):
    """Инлайн модель умений классов."""

    model = ClassEquipment
    extra = 1


class SkillEffectInline(admin.TabularInline):
    """Инлайн модель эффектов предметов."""

    model = Skill.effects.through
    extra = 1


@admin.register(Skill)
class SkillAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление классами персонажа."""

    def download_csv(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/characters/skills.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in queryset:
                spamwriter.writerow(
                    [
                        row.name,
                        row.description,
                        row.level,
                    ]
                )
        with open(
            "data/characters/effects.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in SkillEffect.objects.all():
                spamwriter.writerow(
                    [
                        row.effect.property,
                        row.effect.amount,
                        row.effect.in_percent,
                        row.skill.name,
                        row.effect.slug,
                    ]
                )

    download_csv.short_description = "Download selected as csv"
    changelist_actions = ("download_csv",)
    inlines = (SkillEffectInline,)
    list_display = (
        "name",
        "level",
    )


@admin.register(CharacterClass)
class CharacterClassAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление классами персонажа."""

    def download_csv(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/characters/classes.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in queryset:
                spamwriter.writerow(
                    [
                        row.name,
                        row.description,
                        row.attack,
                        row.defence,
                        row.emoji,
                    ]
                )
        with open(
            "data/characters/class_skills.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in CharacterClassSkill.objects.all():
                spamwriter.writerow(
                    [
                        row.character_class.name,
                        row.skill.name,
                        row.skill.level,
                    ]
                )
        with open(
            "data/characters/class_equipment.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in ClassEquipment.objects.all():
                spamwriter.writerow([row.character_class.name, row.type])

    download_csv.short_description = "Download selected as csv"
    changelist_actions = ("download_csv",)
    inlines = (ClassSkillInline, ClassEquipmentInline)
    list_display = (
        "name",
        "attack",
        "defence",
    )


class CharacterItemInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = Character.items.through
    extra = 1


class CharacterRecipeInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = Character.recipes.through
    extra = 1


class CharacterEffectInline(admin.TabularInline):
    """Инлайн модель эффектов персонажа."""

    model = Character.effects.through
    extra = 1


@admin.register(Character)
class CharacterAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью персонажей."""

    list_display = (
        "name",
        "level",
        "clan",
        "kills",
        "attack",
        "defence",
        "exp_percent",
        "current_location",
        "premium_expired",
    )
    list_display_links = ("name",)
    list_filter = ("level",)
    search_fields = ("name",)
    inlines = (
        CharacterSkillInline,
        CharacterItemInline,
        CharacterRecipeInline,
        CharacterEffectInline,
    )

    def exp_percent(self, obj):
        """Получения опыта в процентах."""
        return f"{round(obj.exp / obj.exp_for_level_up * 100, 2)}%"


@admin.register(MarketplaceItem)
class MarketplaceItemAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление торговой площадкой."""

    list_display = ("seller", "item", "sell_currency", "price")
