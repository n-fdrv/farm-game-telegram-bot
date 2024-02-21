from aiogram.fsm.state import State, StatesGroup


class CharacterState(StatesGroup):
    """Состояния для хендлеров персонажа."""

    enter_nickname = State()
