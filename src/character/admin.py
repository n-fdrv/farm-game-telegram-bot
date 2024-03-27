import datetime

from django.apps import apps
from django.contrib import admin
from django_object_actions import DjangoObjectActions

from character.models import (
    Character,
    CharacterClass,
    ClassEquipment,
    MarketplaceItem,
    Skill,
)

from bot.character.utils import end_hunting
from bot.models import User


class CharacterSkillInline(admin.TabularInline):
    """Инлайн модель умений персонажа."""

    model = Character.skills.through
    extra = 1


class ClassSkillInline(admin.TabularInline):
    """Инлайн модель умений классов."""

    model = CharacterClass.skills.through
    extra = 1


class ClassEquipmentInline(admin.TabularInline):
    """Инлайн модель умений классов."""

    model = ClassEquipment
    extra = 1


class SkillEffectInline(admin.TabularInline):
    """Инлайн модель эффектов предметов."""

    model = Skill.effects.through
    extra = 1


@admin.register(Skill)
class SkillAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление классами персонажа."""

    inlines = (SkillEffectInline,)
    list_display = (
        "name",
        "level",
    )


@admin.register(CharacterClass)
class CharacterClassAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление классами персонажа."""

    inlines = (ClassSkillInline, ClassEquipmentInline)
    list_display = (
        "name",
        "attack",
        "defence",
    )


class CharacterItemInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = Character.items.through
    extra = 1


class CharacterRecipeInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = Character.recipes.through
    extra = 1


class CharacterEffectInline(admin.TabularInline):
    """Инлайн модель эффектов персонажа."""

    model = Character.effects.through
    extra = 1


@admin.register(Character)
class CharacterAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью персонажей."""

    def end_hunting(modeladmin, request, queryset):
        """Окончить охоту персонажей."""
        app_config = apps.get_app_config("bot")
        app = app_config.bot
        scheduler = app.get_scheduler()
        bot = app.get_bot()
        for character in queryset:
            user = User.objects.get(character=character)
            if character.current_location:
                scheduler.add_job(
                    end_hunting,
                    "date",
                    run_date=datetime.datetime.now(),
                    args=[character, bot],
                )
            scheduler.add_job(
                bot.send_message,
                "date",
                run_date=datetime.datetime.now(),
                args=[user.telegram_id, "Сервер отключается на профилактику"],
            )

    end_hunting.short_description = "Окончить охоту всех персонажей"
    changelist_actions = ("end_hunting",)

    list_display = (
        "name",
        "level",
        "clan",
        "kills",
        "attack",
        "defence",
        "exp_percent",
        "current_location",
        "premium_expired",
    )
    list_display_links = ("name",)
    list_filter = ("level",)
    search_fields = ("name",)
    inlines = (
        CharacterSkillInline,
        CharacterItemInline,
        CharacterRecipeInline,
        CharacterEffectInline,
    )

    def exp_percent(self, obj):
        """Получения опыта в процентах."""
        return f"{round(obj.exp / obj.exp_for_level_up * 100, 2)}%"


@admin.register(MarketplaceItem)
class MarketplaceItemAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление торговой площадкой."""

    list_display = ("seller", "item", "sell_currency", "price")
