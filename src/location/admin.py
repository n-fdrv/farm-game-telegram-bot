from django.contrib import admin
from django_object_actions import DjangoObjectActions

from location.models import Location, LocationBoss


class LocationDropInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = Location.drop.through
    extra = 1
    ordering = ("item__type",)


class LocationBossDropInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = LocationBoss.drop.through
    extra = 1
    ordering = ("item__type",)


class LocationBossCharacterInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = LocationBoss.characters.through
    extra = 1


@admin.register(Location)
class LocationAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью локаций."""

    list_display = (
        "name",
        "attack",
        "defence",
        "exp",
    )
    list_display_links = ("name",)
    search_fields = ("name",)
    inlines = (LocationDropInline,)
    ordering = ("-attack", "-defence")


@admin.register(LocationBoss)
class LocationBossAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью боссов локаций."""

    list_display = ("name_with_power", "respawn", "location")
    list_display_links = ("name_with_power",)
    list_filter = ("location",)
    search_fields = ("name",)
    inlines = (LocationBossDropInline, LocationBossCharacterInline)
