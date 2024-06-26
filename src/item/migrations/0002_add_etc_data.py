# Generated by Django 4.2.6 on 2023-10-11 13:46

from django.db import migrations
from django.conf import settings


def create_gold(apps, schema_editor):
    """Create Gold."""
    Etc = apps.get_model("item", "Etc")
    Etc.objects.create(
        name=settings.GOLD_NAME,
        description="Золото можно тратить в магазине и торговой площадке на различные полезные предметы",
    )


def remove_gold(apps, schema_editor):
    """Remove Gold instance."""
    Etc = apps.get_model("item", "Etc")
    gold = Etc.objects.get(name=settings.GOLD_NAME)
    gold.delete()


def create_diamond(apps, schema_editor):
    """Create Diamond."""
    Etc = apps.get_model("item", "Etc")
    Etc.objects.create(
        name=settings.DIAMOND_NAME,
        description="Алмазы можно тратить в премиум магазине и на торговой площадке",
    )


def remove_diamond(apps, schema_editor):
    """Remove Diamond instance."""
    Etc = apps.get_model("item", "Etc")
    diamond = Etc.objects.get(name=settings.DIAMOND_NAME)
    diamond.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("item", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            create_gold, reverse_code=remove_gold
        ),
        migrations.RunPython(create_diamond, reverse_code=remove_diamond),
    ]
