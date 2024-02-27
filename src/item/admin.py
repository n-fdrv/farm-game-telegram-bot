import csv

from django.contrib import admin
from django_object_actions import DjangoObjectActions

from item.models import (
    Armor,
    CraftingItem,
    Etc,
    Item,
    ItemEffect,
    Material,
    Scroll,
    Talisman,
    Weapon,
)


class ItemEffectInline(admin.TabularInline):
    """Инлайн модель эффектов предметов."""

    model = ItemEffect
    extra = 1


class CraftingItemInline(admin.TabularInline):
    """Инлайн модель предметов для изготовления."""

    model = Item.crafting_items.through
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
    inlines = (ItemEffectInline, CraftingItemInline)
    list_display = (
        "name",
        "sell_price",
        "buy_price",
        "armor_type",
        "grade",
        "crafting_level",
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
                        row.crafting_level,
                    ]
                )
        with open(
            "data/items/weapons_crafts.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in CraftingItem.objects.all():
                spamwriter.writerow(
                    [
                        row.crafting_item.name,
                        row.used_item.name,
                        row.amount,
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
    inlines = (ItemEffectInline, CraftingItemInline)
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
    inlines = (ItemEffectInline,)
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
