import csv

from django.contrib import admin
from django_object_actions import DjangoObjectActions

from item.models import (
    Armor,
    CraftingItem,
    Etc,
    ItemEffect,
    Material,
    Potion,
    Recipe,
    Scroll,
    Talisman,
    Weapon,
)


class ItemEffectInline(admin.TabularInline):
    """Инлайн модель эффектов предметов."""

    model = ItemEffect
    extra = 1


class CraftingItemInline(admin.TabularInline):
    """Инлайн модель предметов крафта."""

    model = CraftingItem
    extra = 1


class BaseItemAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Базовая админ-панель для предметов."""

    def download_data(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        file_name = str(modeladmin.model._meta).split(".")[1]
        with open(
            f"data/items/base/{file_name}.csv",
            "w",
            newline="",
            encoding="utf-8",
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

    def download_effects(self, request, queryset):
        """Сформировать файл с эффектами."""
        with open(
            "data/items/effects.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in ItemEffect.objects.all():
                spamwriter.writerow(
                    [
                        row.property,
                        row.amount,
                        row.in_percent,
                        row.item.name,
                    ]
                )

    download_data.short_description = "Загрузить данные"
    download_effects.short_description = "Загрузить эффекты"
    changelist_actions = ("download_data", "download_effects")
    list_display = (
        "name",
        "buy_price",
        "sell_price",
        "grade",
    )
    list_filter = ("grade",)
    list_display_links = ("name",)
    search_fields = ("name",)
    inlines = (ItemEffectInline,)


class BaseEquipmentAdmin(BaseItemAdmin):
    """Базовая админ-панель для предметов."""

    def download_data(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        file_name = str(modeladmin.model._meta).split(".")[1]
        with open(
            f"data/items/equipment/{file_name}.csv",
            "w",
            newline="",
            encoding="utf-8",
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
                        row.equipment_type,
                    ]
                )

    list_display = (
        "name",
        "buy_price",
        "sell_price",
        "equipment_type",
        "grade",
    )
    list_filter = ("grade", "equipment_type")


@admin.register(Armor)
class ArmorAdmin(BaseEquipmentAdmin):
    """Управление моделью предметов."""

    pass


@admin.register(Weapon)
class WeaponAdmin(BaseEquipmentAdmin):
    """Управление моделью предметов."""

    pass


@admin.register(Talisman)
class TalismanAdmin(BaseItemAdmin):
    """Управление моделью предметов."""

    pass


@admin.register(Etc)
class EtcAdmin(BaseItemAdmin):
    """Управление моделью предметов."""

    pass


@admin.register(Material)
class MaterialAdmin(BaseItemAdmin):
    """Управление моделью предметов."""

    pass


@admin.register(Potion)
class PotionAdmin(BaseItemAdmin):
    """Управление моделью эликсиров."""

    pass


@admin.register(Scroll)
class ScrollAdmin(BaseItemAdmin):
    """Управление моделью предметов."""

    pass


@admin.register(Recipe)
class RecipeAdmin(BaseItemAdmin):
    """Управление моделью предметов."""

    def download_csv(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/items/recipes.csv", "w", newline="", encoding="utf-8"
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
                        row.level,
                        row.chance,
                        row.create.name,
                    ]
                )
        with open(
            "data/items/recipes_items.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in CraftingItem.objects.all():
                spamwriter.writerow(
                    [
                        row.material.name,
                        row.recipe.name,
                        row.amount,
                    ]
                )

    download_csv.short_description = "Download selected as csv"
    changelist_actions = ("download_csv", "download_effects")
    list_display = (
        "name",
        "sell_price",
        "buy_price",
        "type",
        "grade",
    )
    inlines = (CraftingItemInline,)
    list_filter = ("type", "grade")
    list_display_links = ("name",)
    search_fields = ("name",)
