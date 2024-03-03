from typing import Optional

from aiogram.filters.callback_data import CallbackData


class BaseCallbackData(CallbackData, prefix="pac"):
    """Базовый Callback_data."""

    action: str
    id: Optional[int] = None
    page: int = 1
    back_action: Optional[str] = None


class CharacterData(BaseCallbackData, prefix="ch"):
    """Данные для хенжлеров персонажа."""

    pass


class LocationData(BaseCallbackData, prefix="loc"):
    """Данные для хенжлеров локаций."""

    pass


class BackpackData(BaseCallbackData, prefix="bp"):
    """Данные для хенжлеров инвентаря."""

    user_id: Optional[int] = None
    item_id: Optional[int] = None
    type: Optional[str] = None
    amount: Optional[int] = 1


class ShopData(BaseCallbackData, prefix="sh"):
    """Данные для хенжлеров магазина."""

    amount: Optional[int] = 1


class CraftData(BaseCallbackData, prefix="cra"):
    """Данные для хенжлеров создания."""

    pass


CALLBACK_DATA_PREFIX = {
    CharacterData.__prefix__: CharacterData,
    LocationData.__prefix__: LocationData,
    BackpackData.__prefix__: BackpackData,
    ShopData.__prefix__: ShopData,
    CraftData.__prefix__: CraftData,
}
