from bot.constants import callback_data


class Action:
    """Базовый класс действий для callback_data."""

    get = "get"
    create = "create"
    remove = "remove"
    list = "list"
    update = "update"

    def __init__(self, callback_name):
        """Добавляет префикс ко всем основным действиям."""
        self.callback = f"{callback_name}-"
        self.get = self.callback + self.get
        self.create = self.callback + self.create
        self.remove = self.callback + self.remove
        self.list = self.callback + self.list
        self.update = self.callback + self.update

    def __str__(self):
        return self.callback


class CharacterAction(Action):
    """Действия для хендлеров персонажа."""

    create_preview = f"{callback_data.CharacterData.__prefix__}-crpv"

    exit_location_confirm = f"{callback_data.CharacterData.__prefix__}-exco"
    exit_location = f"{callback_data.CharacterData.__prefix__}-exlo"


class LocationAction(Action):
    """Действия для хендлеров локаций."""

    enter = f"{callback_data.LocationData.__prefix__}-en"


class BackpackAction(Action):
    """Действия для хендлеров инвентаря."""

    pass


character_action = CharacterAction(callback_data.CharacterData.__prefix__)
location_action = LocationAction(callback_data.LocationData.__prefix__)
backpack_action = BackpackAction(callback_data.BackpackData.__prefix__)
