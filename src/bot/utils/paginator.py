import math

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.callback_helpers import get_callback_by_action


class Paginator:
    """Класс пагинации инлайн-кнопок."""

    paginator: InlineKeyboardMarkup

    def __init__(
        self,
        keyboard: InlineKeyboardBuilder,
        action: str,
        size: int = 5,
        page: int = 1,
        **kwargs
    ):
        """Создает объект пагинатора."""
        self.keyboard = keyboard
        self.action = action
        self.size = size
        self.data_len = len(keyboard.as_markup().inline_keyboard)
        self.page_amount = math.ceil(self.data_len / self.size)
        self.page = page
        self.data_end = size * page
        self.data_start = self.data_end - size
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        """Метод при вызове класса."""
        return self.get_paginator()

    def get_paginator(self):
        """Метод получения пагинатора."""
        self.paginator = InlineKeyboardMarkup(
            inline_keyboard=[
                *self.get_page_data(),
                *self.get_pagination_buttons(),
            ]
        )
        return self.paginator

    def get_paginator_with_button(self, text, action):
        """Метод получения пагинатора с независимой кнопкой."""
        self.paginator = InlineKeyboardMarkup(
            inline_keyboard=[
                *self.get_page_data(),
                *self.get_pagination_buttons(),
                *self.add_independent_button(text, action),
            ]
        )
        return self.paginator

    def get_paginator_with_buttons_list(self, buttons):
        """Метод получения пагинатора с независимыми кнопками."""
        self.paginator = InlineKeyboardMarkup(
            inline_keyboard=[
                *self.get_page_data(),
                *self.get_pagination_buttons(),
                *self.add_buttons(buttons),
            ]
        )
        return self.paginator

    def get_page_data(self):
        """Метод получения данных страницы."""
        page_data = self.keyboard.as_markup().inline_keyboard[
            self.data_start : self.data_end
        ]
        return page_data

    def get_pagination_buttons(self):
        """Метод получения кнопок пагинации."""
        pagination_keyboard = InlineKeyboardBuilder()
        callback = get_callback_by_action(self.action)
        if "user_id" in self.kwargs:
            callback.user_id = self.kwargs["user_id"]
        if "type" in self.kwargs:
            callback.type = self.kwargs["type"]
        if self.page > 1:
            callback.page = self.page - 1
            pagination_keyboard.button(text="⬅️", callback_data=callback)
        if self.page_amount > self.page:
            callback.page = self.page + 1
            pagination_keyboard.button(text="➡️", callback_data=callback)
        pagination_keyboard.adjust(2)
        return pagination_keyboard.as_markup().inline_keyboard

    @staticmethod
    def add_independent_button(text, action, item_id=None):
        """Метод добавления независимой кнопки."""
        keyboard = InlineKeyboardBuilder()
        callback = get_callback_by_action(action)
        if item_id:
            callback.id = item_id
        keyboard.button(text=text, callback_data=callback)
        keyboard.adjust(1)
        return keyboard.as_markup().inline_keyboard

    @staticmethod
    def add_buttons(buttons: list[tuple]):
        """Метод добавления независимой кнопки."""
        keyboard = InlineKeyboardBuilder()
        for button in buttons:
            keyboard.button(text=button[0], callback_data=button[1])
        keyboard.adjust(1)
        return keyboard.as_markup().inline_keyboard
