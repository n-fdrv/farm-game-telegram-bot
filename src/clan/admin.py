from django.contrib import admin
from django_object_actions import DjangoObjectActions

from clan.models import Clan, ClanBoss


class ClanRequestInline(admin.TabularInline):
    """Инлайн модель предметов крафта."""

    model = Clan.requests.through
    extra = 1


class ClanWarehouseInline(admin.TabularInline):
    """Инлайн модель предметов крафта."""

    model = Clan.warehouse.through
    extra = 1


class ClanBossDropInline(admin.TabularInline):
    """Инлайн модель предметов крафта."""

    model = ClanBoss.drop.through
    extra = 1


class ClanBossClanInline(admin.TabularInline):
    """Инлайн модель предметов крафта."""

    model = ClanBoss.clans.through
    extra = 1


class ClanBossCharacterInline(admin.TabularInline):
    """Инлайн модель предметов крафта."""

    model = ClanBoss.characters.through
    extra = 1


class ClanAttackInline(admin.TabularInline):
    """Инлайн модель предметов крафта."""

    model = Clan.wars.through
    fk_name = "clan"
    extra = 1
    verbose_name = "Заявка на войну"
    verbose_name_plural = "Заявки на войну"


class ClanDefenceInline(admin.TabularInline):
    """Инлайн модель предметов крафта."""

    model = Clan.wars.through
    fk_name = "enemy"
    extra = 1
    verbose_name = "Атакующий клан"
    verbose_name_plural = "Атакующие кланы"


@admin.register(Clan)
class ClanAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью пользователя."""

    list_display = (
        "name",
        "level",
        "leader",
        "reputation",
        "by_request",
    )
    list_filter = ("level", "by_request")
    search_fields = ("name", "leader")
    inlines = (
        ClanRequestInline,
        ClanAttackInline,
        ClanDefenceInline,
        ClanWarehouseInline,
    )


@admin.register(ClanBoss)
class ClanBossAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью пользователя."""

    list_display = (
        "name_with_power",
        "respawn",
    )
    list_filter = ("required_power",)
    search_fields = ("name",)
    inlines = (ClanBossDropInline, ClanBossClanInline, ClanBossCharacterInline)
