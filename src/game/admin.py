from django.contrib import admin

from game.models import Character, Item, Location


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Управление моделью предметов."""

    list_display = (
        "name",
        "sell_price",
        "buy_price",
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
class LocationAdmin(admin.ModelAdmin):
    """Управление моделью локаций."""

    list_display = (
        "name",
        "exp",
        "required_power",
    )
    list_display_links = ("name",)
    search_fields = ("name",)
    inlines = (LocationDropInline,)
