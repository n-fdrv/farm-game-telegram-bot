import csv

from django.contrib import admin
from django_object_actions import DjangoObjectActions

from item.models import (
    Armor,
    Bag,
    BagItem,
    CraftingItem,
    Effect,
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


class BagItemInline(admin.TabularInline):
    """Инлайн модель предметов в мешке."""

    model = BagItem
    fk_name = "bag"
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
                    ]
                )
        with open(
            "data/items/effects.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in ItemEffect.objects.all():
                spamwriter.writerow(
                    [
                        row.effect.property,
                        row.effect.amount,
                        row.effect.in_percent,
                        row.item.name,
                    ]
                )

    download_data.short_description = "Загрузить данные"
    changelist_actions = ("download_data",)
    list_display = (
        "name",
        "buy_price",
        "sell_price",
    )
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
                        row.equipment_type,
                    ]
                )
        with open(
            "data/items/effects.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in ItemEffect.objects.all():
                spamwriter.writerow(
                    [
                        row.effect.property,
                        row.effect.amount,
                        row.effect.in_percent,
                        row.item.name,
                    ]
                )

    list_display = (
        "name",
        "buy_price",
        "sell_price",
        "equipment_type",
    )
    list_filter = ("equipment_type",)


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

    def download_data(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/items/talismans.csv",
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
                        row.talisman_type,
                    ]
                )


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

    def download_data(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/items/potions.csv",
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
                        row.effect_time,
                    ]
                )


@admin.register(Scroll)
class ScrollAdmin(BaseItemAdmin):
    """Управление моделью предметов."""

    def download_data(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/items/scrolls.csv",
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
                        row.enhance_type,
                    ]
                )


@admin.register(Recipe)
class RecipeAdmin(BaseItemAdmin):
    """Управление моделью предметов."""

    def download_data(modeladmin, request, queryset):
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

    list_display = (
        "name",
        "sell_price",
        "buy_price",
        "type",
    )
    inlines = (CraftingItemInline,)
    list_filter = ("type",)
    list_display_links = ("name",)
    search_fields = ("name",)


@admin.register(Bag)
class BagAdmin(BaseItemAdmin):
    """Управление моделью мешков."""

    def download_loot(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/items/bag_items.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in BagItem.objects.all():
                spamwriter.writerow(
                    [
                        row.bag.name,
                        row.item.name,
                        row.chance,
                    ]
                )

    changelist_actions = ("download_data", "download_loot")
    inlines = (BagItemInline,)


@admin.register(Effect)
class EffectAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью мешков."""

    def download_data(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        file_name = str(modeladmin.model._meta).split(".")[1]
        with open(
            f"data/items/{file_name}.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in queryset:
                spamwriter.writerow(
                    [
                        row.property,
                        row.amount,
                        row.in_percent,
                    ]
                )

    download_data.short_description = "Download selected as csv"
    changelist_actions = ("download_data",)
    list_display = (
        "property",
        "amount",
        "in_percent",
    )
    list_filter = ("property", "in_percent")
    list_display_links = ("property",)
    search_fields = ("property",)
