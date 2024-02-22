from django.apps import AppConfig


class CharacterConfig(AppConfig):
    """Конфигурация приложения персонажей."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "character"
    verbose_name = "Персонажи"
