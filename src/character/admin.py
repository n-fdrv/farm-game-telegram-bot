import datetime

from django.apps import apps
from django.contrib import admin
from django_object_actions import DjangoObjectActions
from item.models import Effect, EffectSlug, Item

from character.models import (
    Character,
    CharacterClass,
    ClassEquipment,
    MarketplaceItem,
    Power,
    RecipeShare,
    Skill,
)

from bot.hunting.utils import end_hunting
from bot.models import User
from core.config import game_config


class CharacterSkillInline(admin.TabularInline):
    """Инлайн модель умений персонажа."""

    model = Character.skills.through
    extra = 1
    classes = ("collapse",)


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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Изменение списка формы инлайн модели."""
        kwargs["queryset"] = Effect.objects.filter(slug=EffectSlug.SKILL)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Skill)
class SkillAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление классами персонажа."""

    inlines = (SkillEffectInline,)
    list_display = (
        "name_with_level",
        "type",
    )
    list_filter = (
        "type",
        "level",
        "name",
    )


@admin.register(Power)
class PowerAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление классами персонажа."""

    list_display = ("name", "effect", "price")
    list_filter = (
        "price",
        "effect__property",
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Изменение списка формы инлайн модели."""
        kwargs["queryset"] = Effect.objects.filter(slug=EffectSlug.POWER)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
    classes = ("collapse",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Изменение списка формы инлайн модели."""
        kwargs["queryset"] = Item.objects.order_by("type")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CharacterRecipeInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = Character.recipes.through
    extra = 1
    classes = ("collapse",)


class CharacterPowerInline(admin.TabularInline):
    """Инлайн модель предметов персонажа."""

    model = Character.powers.through
    extra = 1
    classes = ("collapse",)


class CharacterEffectInline(admin.TabularInline):
    """Инлайн модель эффектов персонажа."""

    model = Character.effects.through
    extra = 1
    classes = ("collapse",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Изменение списка формы инлайн модели."""
        kwargs["queryset"] = Effect.objects.filter(slug=EffectSlug.POTION)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Character)
class CharacterAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью персонажей."""

    def end_hunting(self, request, queryset):
        """Окончить охоту персонажей."""
        app_config = apps.get_app_config("bot")
        app = app_config.bot
        scheduler = app.get_scheduler()
        bot = app.get_bot()
        for character in queryset:
            user = User.objects.get(character=character)
            if character.current_place:
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

    def reset_character_characteristics(self, request, queryset):
        """Окончить охоту персонажей."""
        for character in queryset:
            character.attack = (
                character.character_class.attack
                + game_config.ATTACK_INCREASE_LEVEL_UP * (character.level - 1)
            )
            character.defence = (
                character.character_class.defence
                + game_config.DEFENCE_INCREASE_LEVEL_UP * (character.level - 1)
            )
            character.accuracy = (
                game_config.ACCURACY_DEFAULT
                + game_config.ACCURACY_INCREASE_LEVEL_UP
                * (character.level - 1)
            )
            character.evasion = (
                game_config.EVASION_DEFAULT
                + game_config.EVASION_INCREASE_LEVEL_UP * (character.level - 1)
            )
            character.max_health = (
                game_config.MAX_HEALTH_DEFAULT
                + game_config.HEALTH_INCREASE_LEVEL_UP * (character.level - 1)
            )
            character.max_mana = (
                game_config.MAX_MANA_DEFAULT
                + game_config.MANA_INCREASE_LEVEL_UP * (character.level - 1)
            )
            character.health = character.max_health
            character.mana = character.max_mana
            character.crit_rate = game_config.CRIT_RATE_DEFAULT
            character.crit_power = game_config.CRIT_POWER_DEFAULT
            character.save()

    reset_character_characteristics.short_description = (
        "Сброс характеристик персонажей"
    )
    changelist_actions = ("end_hunting", "reset_character_characteristics")

    list_display = (
        "name_with_level",
        "exp_percent",
        "hp",
        "mp",
        "clan",
        "kills",
        "attack",
        "defence",
        "current_place",
        "premium_expired",
    )
    list_display_links = ("name_with_level",)
    list_filter = (
        "level",
        "character_class",
    )
    search_fields = ("name",)
    inlines = (
        CharacterSkillInline,
        CharacterPowerInline,
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


@admin.register(RecipeShare)
class RecipeShareAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление общими рецептами."""

    list_display = (
        "character_recipe",
        "price",
    )
