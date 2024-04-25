from django.contrib import admin
from item.models import Item

from premium_shop.models import PremiumLot


class PremiumLotReceivedItemInline(admin.TabularInline):
    """Инлайн модель получаемых предметов премиум лота."""

    model = PremiumLot.received_items.through
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Изменение списка формы инлайн модели."""
        kwargs["queryset"] = Item.objects.order_by("type")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class PremiumLotRequiredItemInline(admin.TabularInline):
    """Инлайн модель необходимых предметов премиум лота."""

    model = PremiumLot.required_items.through
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Изменение списка формы инлайн модели."""
        kwargs["queryset"] = Item.objects.order_by("type")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(PremiumLot)
class PremiumLotAdmin(admin.ModelAdmin):
    """Админ панель премиум лотов.."""

    list_display = (
        "name",
        "amount",
    )
    list_display_links = ("name",)
    search_fields = ("name",)
    inlines = (PremiumLotRequiredItemInline, PremiumLotReceivedItemInline)
