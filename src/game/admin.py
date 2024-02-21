from django.contrib import admin

from game.models import Character, Item, Location


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Управление моделью предметов."""

    list_display = (
        "name",
        "description",
        "type",
    )
    list_filter = ("type",)
    list_display_links = ("name",)
    search_fields = ("name",)


class CharacterItemInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = Character.items.through
    extra = 1


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    """Управление моделью персонажей."""

    list_display = (
        "name",
        "level",
        "power",
        "exp",
    )
    list_display_links = ("name",)
    list_filter = ("level",)
    search_fields = ("name",)
    inlines = (CharacterItemInline,)


class LocationDropInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = Location.drop.through
    extra = 1


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Управление моделью локаций."""

    list_display = (
        "name",
        "required_power",
    )
    list_display_links = ("name",)
    search_fields = ("name",)
    inlines = (LocationDropInline,)
