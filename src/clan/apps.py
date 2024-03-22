from django.apps import AppConfig


class ClanConfig(AppConfig):
    """Конфигурация приложения кланов."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "clan"
    verbose_name = "Кланы"
