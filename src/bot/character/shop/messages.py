from django.conf import settings

SHOP_GET_MESSAGE = (
    "<b>💰Магазин</b>\n\n"
    f"Покупай и продавай предметы за <b>{settings.GOLD_NAME}</b>"
)

PREVIEW_MESSAGE = "<b>💰Категории</b>"

LIST_MESSAGE = "<b>💰Товары</b>"

ITEM_GET_MESSAGE = "<b>{}</b>\n\n" "ℹ️{}\n" "{}\n" "{}"

NOT_ENOUGH_GOLD_MESSAGE = (
    "<b>❌ Неудача</b>\n\n" f"Недостаточно <b>{settings.GOLD_NAME}</b>!"
)

SUCCESS_BUY_MESSAGE = (
    "<b>✅ Успешно</b>\n\n"
    "<i>Приобретено:</i> <b>{}</b>\n"
    "<i>Осталось:</i> <b>{} "
    f"{settings.GOLD_NAME}</b>"
)

SELL_AMOUNT_MESSAGE = "⚠️ Укажите количество товара в сообщении"

NOT_ENOUGH_ITEMS_MESSAGE = (
    "<b>❌ Ошибка</b>\n\n" "Недостаточное количество <b>Предметов</b>!"
)

EQUIPPED_ITEM_MESSAGE = (
    "<b>❌ Ошибка</b>\n\n" "Этот <b>Предмет</b> экипирован!"
)


CHARACTER_IN_LOCATION_MESSAGE = (
    "<b>❌ Ошибка</b>\n\n" "<b>Персонаж</b> не находится в <b>Городе</b>!"
)


SUCCESS_SELL_MESSAGE = (
    "<b>✅ Продано</b>\n\n"
    "Вы продали: <b>{}</b> - <b>{}</b> шт.\n"
    "Получено: <b>{}</b>"
    f"{settings.GOLD_NAME}"
)

CONFIRM_AMOUNT_MESSAGE = (
    "<b>⚠️ Предупреждение</b>\n\n"
    "Вы уверены, что хотите продать <b>{}</b> - <b>{}</b> шт."
)
