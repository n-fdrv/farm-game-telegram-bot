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
    EffectSlug,
    Etc,
    Item,
    ItemEffect,
    ItemType,
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Изменение списка формы инлайн модели."""
        kwargs["queryset"] = Effect.objects.filter(slug=EffectSlug.ITEM)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class PotionEffectInline(admin.TabularInline):
    """Инлайн модель эффектов предметов."""

    model = ItemEffect
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Изменение списка формы инлайн модели."""
        kwargs["queryset"] = Effect.objects.filter(slug=EffectSlug.POTION)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CraftingItemInline(admin.TabularInline):
    """Инлайн модель предметов крафта."""

    model = CraftingItem
    fk_name = "recipe"
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Изменение списка формы инлайн модели."""
        kwargs["queryset"] = Item.objects.filter(type=ItemType.MATERIAL)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class BagItemInline(admin.TabularInline):
    """Инлайн модель предметов в мешке."""

    model = BagItem
    fk_name = "bag"
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Изменение списка формы инлайн модели."""
        kwargs["queryset"] = Item.objects.order_by("type")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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

    inlines = (PotionEffectInline,)


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
        "slug",
        "property",
        "amount",
        "in_percent",
    )
    list_filter = ("property", "in_percent", "slug")
    list_display_links = ("property",)
    search_fields = ("property",)
