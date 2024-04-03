from django.contrib import admin
from django_object_actions import DjangoObjectActions

from location.models import Location


class LocationDropInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = Location.drop.through
    extra = 1
    ordering = ("item__type",)


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
