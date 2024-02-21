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


CALLBACK_DATA_PREFIX = {CharacterData.__prefix__: CharacterData}
