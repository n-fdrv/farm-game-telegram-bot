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
    skill_toggle = f"{callback_data.CharacterData.__prefix__}-skto"
    skill_use = f"{callback_data.CharacterData.__prefix__}-skus"

    about = f"{callback_data.CharacterData.__prefix__}-ab"

    auto_use = f"{callback_data.CharacterData.__prefix__}-auus"

    power_list = f"{callback_data.CharacterData.__prefix__}-poli"
    power_get = f"{callback_data.CharacterData.__prefix__}-poge"
    power_add_confirm = f"{callback_data.CharacterData.__prefix__}-poadco"
    power_add = f"{callback_data.CharacterData.__prefix__}-poad"
    power_reset_confirm = f"{callback_data.CharacterData.__prefix__}-poreco"
    power_reset = f"{callback_data.CharacterData.__prefix__}-pore"


class LocationAction(Action):
    """Действия для хендлеров локаций."""

    enter = f"{callback_data.LocationData.__prefix__}-en"
    exit_location_confirm = f"{callback_data.LocationData.__prefix__}-exco"
    exit_location = f"{callback_data.LocationData.__prefix__}-exlo"

    characters_list = f"{callback_data.LocationData.__prefix__}-chli"
    characters_get = f"{callback_data.LocationData.__prefix__}-chge"
    characters_kill_confirm = f"{callback_data.LocationData.__prefix__}-chkico"
    characters_kill = f"{callback_data.LocationData.__prefix__}-chki"

    boss_list = f"{callback_data.LocationData.__prefix__}-boli"
    boss_get = f"{callback_data.LocationData.__prefix__}-boge"
    boss_accept = f"{callback_data.LocationData.__prefix__}-boac"


class DungeonAction(Action):
    """Действия для хендлеров подземелий."""

    enter_confirm = f"{callback_data.DungeonData.__prefix__}-enco"
    enter = f"{callback_data.DungeonData.__prefix__}-en"
    exit_location_confirm = f"{callback_data.DungeonData.__prefix__}-exco"
    exit_location = f"{callback_data.DungeonData.__prefix__}-exlo"

    characters_list = f"{callback_data.DungeonData.__prefix__}-chli"
    characters_get = f"{callback_data.DungeonData.__prefix__}-chge"
    characters_kill_confirm = f"{callback_data.DungeonData.__prefix__}-chkico"
    characters_kill = f"{callback_data.DungeonData.__prefix__}-chki"

    boss_list = f"{callback_data.DungeonData.__prefix__}-boli"
    boss_get = f"{callback_data.DungeonData.__prefix__}-boge"
    boss_accept = f"{callback_data.DungeonData.__prefix__}-boac"


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

    put_clan_amount = f"{callback_data.BackpackData.__prefix__}-puclam"
    put_clan_confirm = f"{callback_data.BackpackData.__prefix__}-puclco"
    put_clan = f"{callback_data.BackpackData.__prefix__}-pucl"


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


class MasterShopAction(Action):
    """Действия для хендлеров магазина."""

    preview = f"{callback_data.MasterShopData.__prefix__}-pr"

    choose_type = f"{callback_data.MasterShopData.__prefix__}-chty"
    search_recipe = f"{callback_data.MasterShopData.__prefix__}-sere"
    search_recipe_list = f"{callback_data.MasterShopData.__prefix__}-sereli"

    craft_choose_type = f"{callback_data.MasterShopData.__prefix__}-crchty"
    craft_list = f"{callback_data.MasterShopData.__prefix__}-crli"
    craft_get = f"{callback_data.MasterShopData.__prefix__}-crge"
    craft_confirm = f"{callback_data.MasterShopData.__prefix__}-crco"
    craft = f"{callback_data.MasterShopData.__prefix__}-cr"

    recipe_list = f"{callback_data.MasterShopData.__prefix__}-reli"
    recipe_create_amount = f"{callback_data.MasterShopData.__prefix__}-recram"
    recipe_delete_confirm = f"{callback_data.MasterShopData.__prefix__}-redeco"
    recipe_update = f"{callback_data.MasterShopData.__prefix__}-reup"


class PremiumAction(Action):
    """Действия для хендлеров создания."""

    buy = f"{callback_data.PremiumData.__prefix__}-buy"


class PvPAction(Action):
    """Действия для хендлеров ПвП."""

    pass


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

    search_clan = f"{callback_data.ClanData.__prefix__}-secl"
    search_list = f"{callback_data.ClanData.__prefix__}-seli"

    members = f"{callback_data.ClanData.__prefix__}-me"
    wars = f"{callback_data.ClanData.__prefix__}-wa"
    settings = f"{callback_data.ClanData.__prefix__}-se"
    exit_confirm = f"{callback_data.ClanData.__prefix__}-exco"
    exit = f"{callback_data.ClanData.__prefix__}-ex"

    create_request_confirm = f"{callback_data.ClanData.__prefix__}-crreco"
    create_request = f"{callback_data.ClanData.__prefix__}-crre"
    enter_clan_confirm = f"{callback_data.ClanData.__prefix__}-enclco"
    enter_clan = f"{callback_data.ClanData.__prefix__}-encl"

    request_list = f"{callback_data.ClanData.__prefix__}-reli"
    request_get = f"{callback_data.ClanData.__prefix__}-rege"
    request_accept = f"{callback_data.ClanData.__prefix__}-reac"
    request_decline = f"{callback_data.ClanData.__prefix__}-rede"

    members_get = f"{callback_data.ClanData.__prefix__}-mege"
    member_kick_confirm = f"{callback_data.ClanData.__prefix__}-mekico"
    member_kick = f"{callback_data.ClanData.__prefix__}-meki"

    settings_emoji = f"{callback_data.ClanData.__prefix__}-seem"
    settings_description = f"{callback_data.ClanData.__prefix__}-sede"
    settings_access = f"{callback_data.ClanData.__prefix__}-seac"
    settings_remove = f"{callback_data.ClanData.__prefix__}-sere"

    settings_access_confirm = f"{callback_data.ClanData.__prefix__}-seacco"
    settings_emoji_set = f"{callback_data.ClanData.__prefix__}-seemse"

    wars_get = f"{callback_data.ClanData.__prefix__}-wage"
    wars_accept_confirm = f"{callback_data.ClanData.__prefix__}-waacco"
    wars_accept = f"{callback_data.ClanData.__prefix__}-waac"
    wars_end_confirm = f"{callback_data.ClanData.__prefix__}-waenco"
    wars_end = f"{callback_data.ClanData.__prefix__}-waen"
    wars_declare = f"{callback_data.ClanData.__prefix__}-wade"
    wars_declare_set = f"{callback_data.ClanData.__prefix__}-wadese"


class ClanWarehouseAction(Action):
    """Действия для хендлеров клана."""

    preview = f"{callback_data.ClanWarehouseData.__prefix__}-pr"
    look = f"{callback_data.ClanWarehouseData.__prefix__}-lo"

    send_list = f"{callback_data.ClanWarehouseData.__prefix__}-seli"
    send_amount = f"{callback_data.ClanWarehouseData.__prefix__}-seam"
    send_confirm = f"{callback_data.ClanWarehouseData.__prefix__}-seco"
    send = f"{callback_data.ClanWarehouseData.__prefix__}-se"

    put_preview = f"{callback_data.ClanWarehouseData.__prefix__}-pupr"
    put_list = f"{callback_data.ClanWarehouseData.__prefix__}-puli"
    put_get = f"{callback_data.ClanWarehouseData.__prefix__}-puge"
    put = f"{callback_data.ClanWarehouseData.__prefix__}-pu"


class ClanBossesAction(Action):
    """Действия для хендлеров клана."""

    accept_raid = f"{callback_data.ClanBossesData.__prefix__}-acra"


class TopAction(Action):
    """Действия для хендлеров клана."""

    preview = f"{callback_data.TopData.__prefix__}-pr"
    by_exp = f"{callback_data.TopData.__prefix__}-byex"
    by_kills = f"{callback_data.TopData.__prefix__}-byki"


character_action = CharacterAction(callback_data.CharacterData.__prefix__)
location_action = LocationAction(callback_data.LocationData.__prefix__)
dungeon_action = DungeonAction(callback_data.DungeonData.__prefix__)
backpack_action = BackpackAction(callback_data.BackpackData.__prefix__)
shop_action = ShopAction(callback_data.ShopData.__prefix__)
marketplace_action = MarketplaceAction(
    callback_data.MarketplaceData.__prefix__
)
premium_action = PremiumAction(callback_data.PremiumData.__prefix__)
clan_action = ClanAction(callback_data.ClanData.__prefix__)
clan_warehouse_action = ClanWarehouseAction(
    callback_data.ClanWarehouseData.__prefix__
)
clan_bosses_action = ClanBossesAction(callback_data.ClanBossesData.__prefix__)
top_action = TopAction(callback_data.TopData.__prefix__)
master_shop_action = MasterShopAction(callback_data.MasterShopData.__prefix__)
pvp_action = PvPAction(callback_data.PvPData.__prefix__)
