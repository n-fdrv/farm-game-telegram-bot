from aiogram.fsm.state import State, StatesGroup


class CharacterState(StatesGroup):
    """Состояния для хендлеров персонажа."""

    enter_nickname = State()


class ShopState(StatesGroup):
    """Состояния для хендлеров магазина."""

    item_amount = State()


class MarketplaceState(StatesGroup):
    """Состояния для хендлеров торговой площадки."""

    item_price = State()
    item_amount = State()
    item_search = State()


class ClanState(StatesGroup):
    """Состояния для хендлеров клана."""

    enter_name = State()
    clan_search = State()
