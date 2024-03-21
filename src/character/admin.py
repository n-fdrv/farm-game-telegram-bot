import csv

from django.contrib import admin
from django_object_actions import DjangoObjectActions

from character.models import (
    Character,
    CharacterClass,
    CharacterClassSkill,
    CharacterEffect,
    CharacterItem,
    CharacterSkill,
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

    def download_csv(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/characters/characters.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in queryset:
                location = None
                hunting_begin = None
                hunting_end = None
                job_id = None
                if row.current_location:
                    location = row.current_location.name
                    hunting_begin = row.hunting_begin
                    hunting_end = row.hunting_end
                    job_id = row.job_id
                spamwriter.writerow(
                    [
                        row.name,
                        row.level,
                        row.exp,
                        row.exp_for_level_up,
                        row.attack,
                        row.defence,
                        row.character_class.name,
                        location,
                        hunting_begin,
                        hunting_end,
                        row.max_hunting_time,
                        job_id,
                    ]
                )
        with open(
            "data/characters/character_items.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for character_item in CharacterItem.objects.all():
                spamwriter.writerow(
                    [
                        character_item.item.name,
                        character_item.character.name,
                        character_item.amount,
                        character_item.equipped,
                    ]
                )
        with open(
            "data/characters/character_skills.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in CharacterSkill.objects.all():
                spamwriter.writerow(
                    [
                        row.character.name,
                        row.skill.name,
                        row.skill.level,
                    ]
                )
        with open(
            "data/characters/character_effects.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in CharacterEffect.objects.all():
                spamwriter.writerow(
                    [
                        row.character.name,
                        row.effect.name,
                        row.permanent,
                        row.hunting_amount,
                    ]
                )

    download_csv.short_description = "Download selected as csv"
    changelist_actions = ("download_csv",)
    list_display = (
        "name",
        "level",
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
        return f"{obj.exp / obj.exp_for_level_up * 100}%"


@admin.register(MarketplaceItem)
class MarketplaceItemAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление торговой площадкой."""

    def download_csv(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/characters/marketplace.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in queryset:
                spamwriter.writerow(
                    [
                        row.seller.name,
                        row.item.name,
                        row.amount,
                        row.enhancement_level,
                        row.sell_currency.name,
                        row.price,
                    ]
                )

    download_csv.short_description = "Download selected as csv"
    changelist_actions = ("download_csv",)
    list_display = ("seller", "item", "sell_currency", "price")
