from django.conf import settings

NO_CHARACTER_MESSAGE = (
    "❌ Ошибка!\n\n"
    "Чтобы пользоваться <b>💱Торговой Площадкой</b> "
    "требуется создать персонажа"
)

MARKETPLACE_PREVIEW_MESSAGE = (
    "<b>💱Торговая Площадка</b>\n\n"
    "Здесь Вы можете купить или продать предметы "
    "другим пользователям за <b>🟡Золото</b> или <b>💎Алмазы</b>"
)

PREVIEW_MESSAGE = "Выберите тип предмета:"

CHOOSE_BUY_CURRENCY_MESSAGE = "Выберите валюту покупки!"

SELL_LIST_MESSAGE = "Выберите предмет:"

SELL_GET_MESSAGE = (
    "<b>{}</b> - {} шт."
    "\n\n"
    "ℹ️{}\n"
    "<b>{}</b>\n"
    "<i>Лоты:</i>\n"
    f"<b>{settings.GOLD_NAME}</b>: "
    "<b>{}</b>\n"
    f"<b>{settings.DIAMOND_NAME}</b>: "
    "<b>{}</b>"
)

ADD_PREVIEW_MESSAGE = "Выберите валюту продажи предмета!"

ADD_PRICE_MESSAGE = "Укажите цену вашего товара!"

NOT_CORRECT_PRICE_MESSAGE = "Неверная цена товара! Введите цену снова"

CORRECT_PRICE_MESSAGE = (
    "✅ Отлично!\n\n" "⚠️Теперь укажите количество товара на <b>Продажу</b>"
)

CONFIRM_LOT_MESSAGE = (
    "⚠️ Подтверждение!\n\n"
    "<b>{}</b> - {} шт.\n"
    "<i>Цена</i>: <b>{} {}</b>\n"
    "<i>Вы получите</i>: <b>{} {}</b> <i>(Комиссия {}%)</i>\n\n"
    "❔ Выставить на торговую площадку?"
)

NOT_SUCCESS_LOT_MESSAGE = (
    "❌ Ошибка!\n\n" "Произошла ошибка добавления лота. Попробуй еще раз!"
)

BUY_GET_MESSAGE = (
    "<b>{}</b> - {} шт.\n\n"
    "{}\n"
    "<b>{}</b>\n"
    "<i>Продавец:</i> <b>{}</b>\n"
    "<i>Цена:</i> <b>{}</b>"
)

BUY_CONFIRM_MESSAGE = (
    "⚠️ Подтверждение!\n\n"
    "Вы уверены, что хотите купить <b>{}</b> - <b>{} шт.</b> за <b>{}</b>?"
)

SUCCESS_SELL_MESSAGE = (
    "✅ Успешная Продажа!\n\n"
    "Вы продали <b>{}</b> - <b>{}</b> шт. и получили <b>{}</b>"
)


ITEM_LIST_MESSAGE = "Ваши активные лоты: <b>{}/{}</b>"

REMOVE_CONFIRM_MESSAGE = (
    "⚠️ Подтверждение!\n\n" "Вы уверены, что хотите удалить лот с продажи?"
)

NO_MARKETPLACE_ITEM_MESSAGE = (
    "❌ Ошибка!\n\n" "❗ Данный лот уже был удален или выкуплен!"
)

ITEM_SEARCH_MESSAGE = "🔎 Поиск\n\n" "Введите название предмета в сообщении"

ITEM_SEARCH_AMOUNT_MESSAGE = (
    "🔎 Поиск\n\n" "Найдено <b>{}</b> лот(ов) по запросу: <b>{}</b>"
)

SEARCH_ITEM_LIST_MESSAGE = "🔎 Поиск\n\n" "Список найденных предметов:"

MAX_LOT_AMOUNT_MESSAGE = (
    "❌ Неудачно!\n\n" "Достигнуто максимальное число доступных лотов!"
)

SUCCESS_ADD_LOT_MESSAGE = "✅ Успешно!\n\n" "Предмет выставлен на продажу"

NOT_ENOUGH_CURRENCY = "❌ Неудачно!\n\n" "Недостаточно {}!"

SUCCESS_BUY_MESSAGE = (
    "✅ Успешно!\n\n" "Получено: <b>{}</b>\n" "Оплачено: <b>{}</b>"
)

REMOVE_LOT_MESSAGE = "✅ Успешно!\n\n" "<b>{}</b> удален с Торговой Площадки"
