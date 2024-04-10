from django.db import models
from django.utils import timezone
from item.models import Item


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
    warehouse = models.ManyToManyField(
        Item, through="ClanWarehouse", related_name="clan_warehouse"
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

    @property
    def clan_leader(self):
        """Метод получения имени персонажа с уровнем."""
        if self.emoji:
            return f"{self.emoji}{self.leader.name} Ур. {self.level}"
        return f"{self.leader.name} Ур. {self.level}"


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


class ClanWarehouse(models.Model):
    """Модель кланового хранилища."""

    clan = models.ForeignKey(
        Clan, on_delete=models.CASCADE, verbose_name="Клан"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, verbose_name="Предмет"
    )
    amount = models.IntegerField(default=0, verbose_name="Количество")
    equipped = models.BooleanField(default=False, verbose_name="Надето")
    enhancement_level = models.IntegerField(
        default=0, verbose_name="Уровень улучшения"
    )

    @property
    def name_with_enhance(self):
        """Возвращает название с уровнем улучшения."""
        if self.enhancement_level:
            return f"{self.item.name_with_type} +{self.enhancement_level}"
        return f"{self.item.name_with_type}"

    class Meta:
        verbose_name = "Предмет Клана"
        verbose_name_plural = "Предметы Клана"

    def __str__(self):
        return (
            f"Clan: {self.clan} | "
            f"Item: {self.item} | "
            f"Amount: {self.amount}"
        )


class ClanBoss(models.Model):
    """Модель клановых боссов."""

    name = models.CharField(max_length=16, verbose_name="Имя")
    respawn = models.DateTimeField(
        default=timezone.now, verbose_name="Время Респауна"
    )
    required_power = models.IntegerField(
        default=100, verbose_name="Необходимая сила клана"
    )
    drop = models.ManyToManyField(
        Item, through="ClanBossDrop", related_name="clan_boss_drop"
    )
    clans = models.ManyToManyField(to=Clan, through="ClanBossClan")
    characters = models.ManyToManyField(
        to="character.Character", through="ClanBossCharacter"
    )

    class Meta:
        verbose_name = "Клановый босс"
        verbose_name_plural = "Клановые боссы"

    def __str__(self):
        return (
            f"Name: {self.name} | "
            f"Required Power: {self.required_power} | "
            f"Respawn: {self.respawn}"
        )

    @property
    def name_with_power(self):
        """Имя с необходимой силой клана."""
        return f"{self.name} ⚔️{self.required_power}"


class ClanBossClan(models.Model):
    """Модель хранения персонажей участвующих в рейде."""

    clan = models.ForeignKey(
        to=Clan, on_delete=models.CASCADE, verbose_name="Клан в рейде"
    )
    boss = models.ForeignKey(
        ClanBoss, on_delete=models.CASCADE, verbose_name="Клановый босс"
    )

    class Meta:
        verbose_name = "Клан в рейде"
        verbose_name_plural = "Кланы в рейде"

    def __str__(self):
        return f"Clan: {self.clan} | " f"Boss: {self.boss}"


class ClanBossCharacter(models.Model):
    """Модель хранения персонажей участвующих в рейде."""

    character = models.ForeignKey(
        to="character.Character",
        on_delete=models.CASCADE,
        verbose_name="Персонаж в рейде",
    )
    boss = models.ForeignKey(
        ClanBoss, on_delete=models.CASCADE, verbose_name="Клановый босс"
    )

    class Meta:
        verbose_name = "Персонаж в рейде"
        verbose_name_plural = "Персонажи в рейде"

    def __str__(self):
        return f"Character: {self.character} | " f"Boss: {self.boss}"


class ClanBossDrop(models.Model):
    """Модель для хранения дроп листа клановых боссов."""

    clan_boss = models.ForeignKey(
        ClanBoss, on_delete=models.CASCADE, verbose_name="Клановый босс"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, verbose_name="Предмет"
    )
    min_amount = models.IntegerField(
        default=1, verbose_name="Минимальное количество"
    )
    max_amount = models.IntegerField(
        default=1, verbose_name="Максимальное количество"
    )
    chance = models.FloatField(
        default=1, verbose_name="Шанс в процентах в минуту"
    )

    class Meta:
        verbose_name = "Трофей с босса"
        verbose_name_plural = "Трофеи с босса"

    def __str__(self):
        return f"{self.item.name_with_type} {self.chance}"
