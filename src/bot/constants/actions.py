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
    class_list = f"{callback_data.CharacterData.__prefix__}-clli"
    class_get = f"{callback_data.CharacterData.__prefix__}-clge"

    skill_list = f"{callback_data.CharacterData.__prefix__}-skli"
    skill_get = f"{callback_data.CharacterData.__prefix__}-skge"

    about = f"{callback_data.CharacterData.__prefix__}-ab"


class LocationAction(Action):
    """Действия для хендлеров локаций."""

    enter = f"{callback_data.LocationData.__prefix__}-en"
    exit_location_confirm = f"{callback_data.LocationData.__prefix__}-exco"
    exit_location = f"{callback_data.LocationData.__prefix__}-exlo"

    characters_list = f"{callback_data.LocationData.__prefix__}-chli"
    characters_get = f"{callback_data.LocationData.__prefix__}-chge"
    characters_kill_confirm = f"{callback_data.LocationData.__prefix__}-chkico"
    characters_kill = f"{callback_data.LocationData.__prefix__}-chki"


class BackpackAction(Action):
    """Действия для хендлеров инвентаря."""

    preview = f"{callback_data.BackpackData.__prefix__}-pr"
    equip = f"{callback_data.BackpackData.__prefix__}-eq"
    use = f"{callback_data.BackpackData.__prefix__}-use"
    open = f"{callback_data.BackpackData.__prefix__}-op"
    open_all = f"{callback_data.BackpackData.__prefix__}-opal"

    enhance_list = f"{callback_data.BackpackData.__prefix__}-enli"
    enhance_get = f"{callback_data.BackpackData.__prefix__}-enge"
    enhance = f"{callback_data.BackpackData.__prefix__}-en"


class ShopAction(Action):
    """Действия для хендлеров магазина."""

    buy_preview = f"{callback_data.ShopData.__prefix__}-bupr"
    buy_list = f"{callback_data.ShopData.__prefix__}-buli"
    buy_get = f"{callback_data.ShopData.__prefix__}-buge"
    buy = f"{callback_data.ShopData.__prefix__}-bu"

    sell_preview = f"{callback_data.ShopData.__prefix__}-sepr"
    sell_list = f"{callback_data.ShopData.__prefix__}-seli"
    sell_get = f"{callback_data.ShopData.__prefix__}-sege"
    sell_amount = f"{callback_data.ShopData.__prefix__}-seam"
    sell = f"{callback_data.ShopData.__prefix__}-se"


class CraftAction(Action):
    """Действия для хендлеров создания."""

    pass


class PremiumAction(Action):
    """Действия для хендлеров создания."""

    buy = f"{callback_data.PremiumData.__prefix__}-buy"


class MarketplaceAction(Action):
    """Действия для хендлеров торговой площадки."""

    preview = f"{callback_data.MarketplaceData.__prefix__}-pr"
    buy_currency = f"{callback_data.MarketplaceData.__prefix__}-bucu"

    buy_preview = f"{callback_data.MarketplaceData.__prefix__}-bupr"
    sell_preview = f"{callback_data.MarketplaceData.__prefix__}-sepr"

    items_list = f"{callback_data.MarketplaceData.__prefix__}-itli"
    sell_list = f"{callback_data.MarketplaceData.__prefix__}-seli"
    buy_list = f"{callback_data.MarketplaceData.__prefix__}-buli"

    sell_get = f"{callback_data.MarketplaceData.__prefix__}-sege"
    buy_get = f"{callback_data.MarketplaceData.__prefix__}-buge"
    item_get = f"{callback_data.MarketplaceData.__prefix__}-itge"
    item_search = f"{callback_data.MarketplaceData.__prefix__}-itse"
    search_lot_list = f"{callback_data.MarketplaceData.__prefix__}-seloli"

    remove_preview = f"{callback_data.MarketplaceData.__prefix__}-repr"

    buy_confirm = f"{callback_data.MarketplaceData.__prefix__}-buco"

    add_preview = f"{callback_data.MarketplaceData.__prefix__}-adpr"
    choose_currency = f"{callback_data.MarketplaceData.__prefix__}-chcu"
    add = f"{callback_data.MarketplaceData.__prefix__}-add"
    buy = f"{callback_data.MarketplaceData.__prefix__}-buy"


class ClanAction(Action):
    """Действия для хендлеров клана."""

    preview = f"{callback_data.ClanData.__prefix__}-pr"
    create_preview = f"{callback_data.ClanData.__prefix__}-crpr"

    members = f"{callback_data.ClanData.__prefix__}-me"
    wars = f"{callback_data.ClanData.__prefix__}-wa"
    settings = f"{callback_data.ClanData.__prefix__}-se"
    exit_confirm = f"{callback_data.ClanData.__prefix__}-exco"
    exit = f"{callback_data.ClanData.__prefix__}-ex"


character_action = CharacterAction(callback_data.CharacterData.__prefix__)
location_action = LocationAction(callback_data.LocationData.__prefix__)
backpack_action = BackpackAction(callback_data.BackpackData.__prefix__)
shop_action = ShopAction(callback_data.ShopData.__prefix__)
craft_action = CraftAction(callback_data.CraftData.__prefix__)
marketplace_action = MarketplaceAction(
    callback_data.MarketplaceData.__prefix__
)
premium_action = PremiumAction(callback_data.PremiumData.__prefix__)
clan_action = ClanAction(callback_data.ClanData.__prefix__)
