from django.db import models


class Clan(models.Model):
    """Модель хранения кланов."""

    name = models.CharField(
        max_length=16, unique=True, verbose_name="Название"
    )
    emoji = models.CharField(
        max_length=4, null=True, blank=True, verbose_name="Эмоджи"
    )
    description = models.TextField(
        max_length=128, default="Нет описания", verbose_name="Описание"
    )
    leader = models.ForeignKey(
        to="character.Character",
        on_delete=models.RESTRICT,
        verbose_name="Лидер",
        related_name="clan_leader",
    )
    level = models.IntegerField(default=1, verbose_name="Уровень")
    reputation = models.IntegerField(default=0, verbose_name="Репутация")
    place = models.IntegerField(default=10, verbose_name="Мест в клане")
    by_request = models.BooleanField(
        default=True, verbose_name="Вход по заявкам"
    )
    requests = models.ManyToManyField(
        to="character.Character",
        through="ClanRequest",
        verbose_name="Заявки",
        related_name="clan_request",
    )
    wars = models.ManyToManyField(
        to="Clan", through="ClanWar", verbose_name="Войны"
    )

    class Meta:
        verbose_name = "Клан"
        verbose_name_plural = "Кланы"

    def __str__(self):
        return f"{self.name} Ур. {self.level}"

    @property
    def name_with_emoji(self):
        """Имя с эмоджи."""
        if self.emoji:
            return f"{self.emoji}{self.name}"
        return f"{self.name}"


class ClanRequest(models.Model):
    """Модель хранения заявок в клан."""

    character = models.OneToOneField(
        to="character.Character",
        on_delete=models.CASCADE,
        verbose_name="Персонаж",
    )
    clan = models.ForeignKey(
        Clan, on_delete=models.CASCADE, verbose_name="Клан"
    )
    text = models.TextField(
        max_length=256, null=True, blank=True, verbose_name="Текст заявки"
    )

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return f"{self.character} | {self.clan}"


class ClanWar(models.Model):
    """Модель воин клана."""

    clan = models.ForeignKey(
        Clan,
        on_delete=models.CASCADE,
        verbose_name="Клан",
        related_name="war_sent",
    )
    enemy = models.ForeignKey(
        Clan,
        on_delete=models.SET_NULL,
        verbose_name="Враг",
        related_name="war_request",
        null=True,
    )
    accepted = models.BooleanField(default=False, verbose_name="Война принята")

    class Meta:
        verbose_name = "Клановая война"
        verbose_name_plural = "Клановые войны"

    def __str__(self):
        return f"{self.clan.name} против {self.enemy.name}"
