import csv

from django.contrib import admin
from django_object_actions import DjangoObjectActions

from game.models import Character, CharacterItem, Item, Location, LocationDrop


@admin.register(Item)
class ItemAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью предметов."""

    def download_csv(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/items.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in queryset:
                spamwriter.writerow(
                    [
                        row.name,
                        row.description,
                        row.sell_price,
                        row.buy_price,
                        row.type,
                        row.grade,
                    ]
                )

    download_csv.short_description = "Download selected as csv"
    changelist_actions = ("download_csv",)

    list_display = (
        "name",
        "sell_price",
        "buy_price",
        "type",
        "grade",
    )
    list_filter = ("type", "grade")
    list_display_links = ("name",)
    search_fields = ("name",)


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
            "data/characters.csv", "w", newline="", encoding="utf-8"
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
                        row.power,
                        location,
                        hunting_begin,
                        hunting_end,
                        row.max_hunting_time,
                        job_id,
                    ]
                )
        with open(
            "data/character_items.csv", "w", newline="", encoding="utf-8"
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
        "power",
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


class LocationDropInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = Location.drop.through
    extra = 1


@admin.register(Location)
class LocationAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью локаций."""

    def download_csv(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/locations.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in queryset:
                spamwriter.writerow(
                    [
                        row.name,
                        row.required_power,
                        row.exp,
                    ]
                )
        with open(
            "data/location_drop.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for location_drop in LocationDrop.objects.all():
                spamwriter.writerow(
                    [
                        location_drop.location.name,
                        location_drop.item.name,
                        location_drop.min_amount,
                        location_drop.max_amount,
                        location_drop.chance,
                    ]
                )

    download_csv.short_description = "Download selected as csv"
    changelist_actions = ("download_csv",)

    list_display = (
        "name",
        "exp",
        "required_power",
    )
    list_display_links = ("name",)
    search_fields = ("name",)
    inlines = (LocationDropInline,)
