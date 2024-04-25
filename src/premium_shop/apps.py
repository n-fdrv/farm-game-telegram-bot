from django.apps import AppConfig


class PremiumShopConfig(AppConfig):
    """Настройки приложения Премиум магазина."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "premium_shop"
    verbose_name = "Премиум Магазин"
