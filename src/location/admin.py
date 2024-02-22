import csv

from django.contrib import admin
from django_object_actions import DjangoObjectActions

from location.models import Location, LocationDrop


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
            "data/locations/locations.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in queryset:
                spamwriter.writerow(
                    [
                        row.name,
                        row.attack,
                        row.defence,
                        row.exp,
                    ]
                )
        with open(
            "data/locations/location_drop.csv",
            "w",
            newline="",
            encoding="utf-8",
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
        "attack",
        "defence",
        "exp",
    )
    list_display_links = ("name",)
    search_fields = ("name",)
    inlines = (LocationDropInline,)
