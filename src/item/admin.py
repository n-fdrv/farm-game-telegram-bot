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


@admin.register(Armor)
class ArmorAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью предметов."""

    def download_csv(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/items/armors.csv", "w", newline="", encoding="utf-8"
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
                        row.armor_type,
                    ]
                )
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

    download_csv.short_description = "Download selected as csv"
    changelist_actions = ("download_csv",)
    inlines = (ItemEffectInline,)
    list_display = (
        "name",
        "sell_price",
        "buy_price",
        "armor_type",
        "grade",
    )
    list_filter = ("armor_type", "grade")
    list_display_links = ("name",)
    search_fields = ("name",)


@admin.register(Weapon)
class WeaponAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью предметов."""

    def download_csv(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/items/weapons.csv", "w", newline="", encoding="utf-8"
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
                        row.weapon_type,
                    ]
                )

    download_csv.short_description = "Download selected as csv"
    changelist_actions = ("download_csv",)
    list_display = (
        "name",
        "sell_price",
        "buy_price",
        "weapon_type",
        "grade",
    )
    inlines = (ItemEffectInline,)
    list_filter = ("weapon_type", "grade")
    list_display_links = ("name",)
    search_fields = ("name",)


@admin.register(Etc)
class EtcAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью предметов."""

    def download_csv(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/items/etc.csv", "w", newline="", encoding="utf-8"
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


@admin.register(Material)
class MaterialAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью предметов."""

    def download_csv(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/items/material.csv", "w", newline="", encoding="utf-8"
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


@admin.register(Potion)
class PotionAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью эликсиров."""

    def download_csv(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/items/potions.csv", "w", newline="", encoding="utf-8"
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
                        row.effect_time,
                    ]
                )

    download_csv.short_description = "Download selected as csv"
    changelist_actions = ("download_csv",)
    list_display = (
        "name",
        "buy_price",
        "sell_price",
        "effect_time",
        "grade",
    )
    inlines = (ItemEffectInline,)
    list_filter = ("grade",)
    list_display_links = ("name",)
    search_fields = ("name",)


@admin.register(Scroll)
class ScrollAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью предметов."""

    def download_csv(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/items/scrolls.csv", "w", newline="", encoding="utf-8"
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


@admin.register(Talisman)
class TalismanAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью предметов."""

    def download_csv(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/items/talismans.csv", "w", newline="", encoding="utf-8"
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
    inlines = (ItemEffectInline,)
    list_filter = ("type", "grade")
    list_display_links = ("name",)
    search_fields = ("name",)


class CraftingItemInline(admin.TabularInline):
    """Инлайн модель предметов крафта."""

    model = CraftingItem
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(DjangoObjectActions, admin.ModelAdmin):
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
    changelist_actions = ("download_csv",)
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
