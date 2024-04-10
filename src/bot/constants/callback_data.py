from typing import Optional

from aiogram.filters.callback_data import CallbackData


class BaseCallbackData(CallbackData, prefix="pac"):
    """Базовый Callback_data."""

    action: str
    id: Optional[int] = None
    page: int = 1


class CharacterData(BaseCallbackData, prefix="ch"):
    """Данные для хенжлеров персонажа."""

    type: Optional[str] = None


class PremiumData(BaseCallbackData, prefix="pr"):
    """Данные для хенжлеров премиум магазина."""

    type: Optional[str] = None
    price: Optional[int] = 0


class LocationData(BaseCallbackData, prefix="loc"):
    """Данные для хенжлеров локаций."""

    character_id: Optional[int] = 0
    message_id: Optional[int] = 0


class BackpackData(BaseCallbackData, prefix="bp"):
    """Данные для хенжлеров инвентаря."""

    user_id: Optional[int] = None
    item_id: Optional[int] = None
    type: Optional[str] = None
    amount: Optional[int] = 1


class ShopData(BaseCallbackData, prefix="sh"):
    """Данные для хенжлеров магазина."""

    type: Optional[str] = None
    amount: Optional[int] = 1


class MarketplaceData(BaseCallbackData, prefix="mp"):
    """Данные для хендлеров торговой площадки.."""

    currency: Optional[str] = None
    type: Optional[str] = None
    amount: Optional[int] = 1
    name_contains: Optional[str] = None
    back_action: Optional[str] = None


class ClanData(BaseCallbackData, prefix="cl"):
    """Данные для хендлеров клана."""

    name_contains: Optional[str] = None
    character_id: Optional[int] = 0
    settings_value: Optional[str] = None
    war_id: Optional[int] = 0


class ClanWarehouseData(BaseCallbackData, prefix="wa"):
    """Данные для хендлеров клана."""

    character_id: Optional[int] = None
    item_id: Optional[int] = None
    type: Optional[str] = None
    amount: Optional[int] = 1


class ClanBossesData(BaseCallbackData, prefix="clbo"):
    """Данные для хендлеров клановых боссов."""

    pass


class TopData(BaseCallbackData, prefix="top"):
    """Данные для хендлеров топа персонажей."""

    filter_by: Optional[str] = None


class MasterShopData(BaseCallbackData, prefix="mash"):
    """Данные для хендлеров мастерской."""

    type: Optional[str] = None
    character_id: Optional[int] = None
    name_contains: Optional[str] = None
    back_action: Optional[str] = None
    price: Optional[int] = None


CALLBACK_DATA_PREFIX = {
    CharacterData.__prefix__: CharacterData,
    LocationData.__prefix__: LocationData,
    BackpackData.__prefix__: BackpackData,
    ShopData.__prefix__: ShopData,
    MarketplaceData.__prefix__: MarketplaceData,
    PremiumData.__prefix__: PremiumData,
    ClanData.__prefix__: ClanData,
    TopData.__prefix__: TopData,
    ClanWarehouseData.__prefix__: ClanWarehouseData,
    ClanBossesData.__prefix__: ClanBossesData,
    MasterShopData.__prefix__: MasterShopData,
}
