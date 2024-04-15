from django.contrib import admin
from django_object_actions import DjangoObjectActions

from item.models import (
    Armor,
    Bag,
    BagItem,
    Book,
    Bracelet,
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
    fk_name = "recipe"
    extra = 1


class BagItemInline(admin.TabularInline):
    """Инлайн модель предметов в мешке."""

    model = BagItem
    fk_name = "bag"
    extra = 1
    ordering = ("item__type",)


class BaseItemAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Базовая админ-панель для предметов."""

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


@admin.register(Bracelet)
class BraceletAdmin(BaseEquipmentAdmin):
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

    list_display = (
        "name_with_chance",
        "level",
        "sell_price",
        "buy_price",
        "type",
    )
    inlines = (CraftingItemInline,)
    list_filter = ("level", "chance")
    list_display_links = ("name_with_chance",)
    search_fields = ("name",)


@admin.register(Book)
class BookAdmin(BaseItemAdmin):
    """Управление моделью предметов."""

    list_display = (
        "name_with_type",
        "character_class",
        "required_level",
        "required_skill",
        "skill",
    )
    list_filter = ("required_level", "character_class")
    list_display_links = ("name_with_type",)
    search_fields = ("name",)


@admin.register(Bag)
class BagAdmin(BaseItemAdmin):
    """Управление моделью мешков."""

    inlines = (BagItemInline,)


@admin.register(Effect)
class EffectAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью мешков."""

    list_display = (
        "property",
        "amount",
        "in_percent",
    )
    list_filter = ("property", "in_percent")
    list_display_links = ("property",)
    search_fields = ("property",)
