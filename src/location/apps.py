from django.apps import AppConfig


class LocationConfig(AppConfig):
    """Конфигурация приложения локаций."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "location"
    verbose_name = "Локации"
