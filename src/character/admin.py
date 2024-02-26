import csv

from django.contrib import admin
from django_object_actions import DjangoObjectActions

from character.models import Character, CharacterClass, CharacterItem


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
                        row.attack_level_increase,
                        row.defence_level_increase,
                    ]
                )

    download_csv.short_description = "Download selected as csv"
    changelist_actions = ("download_csv",)

    list_display = (
        "name",
        "attack",
        "defence",
    )


class CharacterItemInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = Character.items.through
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
                        row.character_class,
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
    )
    list_display_links = ("name",)
    list_filter = ("level",)
    search_fields = ("name",)
    inlines = (CharacterItemInline,)

    def exp_percent(self, obj):
        """Получения опыта в процентах."""
        return f"{obj.exp / obj.exp_for_level_up * 100}%"
