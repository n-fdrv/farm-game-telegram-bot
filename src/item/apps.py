from django.apps import AppConfig


class ItemConfig(AppConfig):
    """Конфигурация приложения предметов."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "item"
    verbose_name = "Предметы"
