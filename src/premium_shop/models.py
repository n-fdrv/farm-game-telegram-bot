from django.db import models
from item.models import Item


class PremiumLotType(models.TextChoices):
    """Тип премиум лотов."""

    PREMIUM = "premium", "🎟Премиум"
    PACK = "skill", "🎒Наборы"
    EVENT = "event", "🎁Акции"


class PremiumLot(models.Model):
    """Модель для хранения лотов премиум магазина."""

    name = models.CharField(max_length=32, verbose_name="Имя")
    description = models.TextField(max_length=256, verbose_name="Описание")
    type = models.CharField(
        max_length=16,
        choices=PremiumLotType.choices,
        default=PremiumLotType.EVENT,
        verbose_name="Тип",
    )
    received_items = models.ManyToManyField(
        to=Item,
        through="PremiumLotReceivedItem",
        verbose_name="Получаемые предметы",
        related_name="premium_lot_received_items",
    )
    required_items = models.ManyToManyField(
        to=Item,
        through="PremiumLotRequiredItem",
        verbose_name="Необходимые предметы",
        related_name="premium_lot_required_items",
    )
    amount = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Премиум Лот"
        verbose_name_plural = "Премиум Лоты"

    def __str__(self):
        return f"{self.name} ({self.amount} шт.)"


class PremiumLotReceivedItem(models.Model):
    """Модель для хранения получаемых предметов лота."""

    premium_lot = models.ForeignKey(
        PremiumLot, on_delete=models.CASCADE, verbose_name="Премиум Лот"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, verbose_name="Предмет"
    )
    amount = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Получаемый Предмет"
        verbose_name_plural = "Получаемые Предметы"

    def __str__(self):
        return f"{self.item.name_with_type}"


class PremiumLotRequiredItem(models.Model):
    """Модель для хранения получаемых предметов лота."""

    premium_lot = models.ForeignKey(
        PremiumLot, on_delete=models.CASCADE, verbose_name="Премиум Лот"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, verbose_name="Предмет"
    )
    amount = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Необходимый Предмет"
        verbose_name_plural = "Необходимые Предметы"

    def __str__(self):
        return f"{self.item.name_with_type}"
