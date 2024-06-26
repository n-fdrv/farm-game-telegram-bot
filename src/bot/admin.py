import csv

from django.contrib import admin
from django_object_actions import DjangoObjectActions

from bot.models import User


@admin.register(User)
class UserAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Управление моделью пользователя."""

    def download_csv(modeladmin, request, queryset):
        """Сформировать файл с данными базы."""
        with open(
            "data/users.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=",")
            for row in queryset:
                character = None
                if row.character:
                    character = row.character.name
                spamwriter.writerow(
                    [
                        row.telegram_id,
                        row.first_name,
                        row.last_name,
                        row.telegram_username,
                        row.registration_date,
                        row.is_admin,
                        character,
                        row.is_active,
                    ]
                )

    download_csv.short_description = "Download selected as csv"
    changelist_actions = ("download_csv",)
    list_display = (
        "telegram_id",
        "first_name",
        "last_name",
        "telegram_username",
        "character",
        "registration_date",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("telegram_id", "telegram_username")

    # def has_change_permission(self, request, obj=None):
    #     """Запрещает изменять объект."""
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     """Запрещает удалять объект."""
    #     return False

    # def has_add_permission(self, request):
    #     """Запрещает добавлять объект."""
    #     return False
