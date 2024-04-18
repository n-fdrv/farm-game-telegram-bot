from django.contrib import admin
from django_object_actions import DjangoObjectActions
from item.models import Item

from location.models import Dungeon, Location, LocationBoss


class LocationDropInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = Location.drop.through
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Изменение списка формы инлайн модели."""
        kwargs["queryset"] = Item.objects.order_by("type")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
        "required_power",
        "exp",
    )
    list_display_links = ("name",)
    search_fields = ("name",)
    inlines = (LocationDropInline,)
    ordering = ("-required_power",)


@admin.register(LocationBoss)
class LocationBossAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью боссов локаций."""

    list_display = ("name_with_power", "respawn", "location")
    list_display_links = ("name_with_power",)
    list_filter = ("location",)
    search_fields = ("name",)
    inlines = (LocationBossDropInline, LocationBossCharacterInline)


class DungeonDropInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = Dungeon.drop.through
    extra = 1
    ordering = ("item__type",)
    classes = ("collapse",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Изменение списка формы инлайн модели."""
        kwargs["queryset"] = Item.objects.order_by("type")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class DungeonRequiredItemInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = Dungeon.required_items.through
    extra = 1
    ordering = ("item__type",)
    classes = ("collapse",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Изменение списка формы инлайн модели."""
        kwargs["queryset"] = Item.objects.order_by("type")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class DungeonCharacterInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = Dungeon.characters.through
    extra = 1
    classes = ("collapse",)


@admin.register(Dungeon)
class DungeonAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью локаций."""

    list_display = (
        "name_with_level",
        "exp",
        "hunting_hours",
        "cooldown_hours",
    )
    list_display_links = ("name_with_level",)
    list_filter = ("name", "hunting_hours", "cooldown_hours")
    search_fields = ("name",)
    inlines = (
        DungeonRequiredItemInline,
        DungeonDropInline,
        DungeonCharacterInline,
    )
    ordering = ("-min_level",)
