from django.conf import settings

BOOK_INFO_MESSAGE = (
    "\n<i>Требуемый класс:</i> <b>{}</b>\n"
    "<i>Требуемый уровень:</i> <b>{}</b>\n"
    "<i>Требуемая способность:</i> <b>{}</b>\n"
)

EQUIPPED_CLASS_INFO = "\n<i>Необходимый класс:</i> <b>{}</b>\n"

ITEM_GET_MESSAGE = (
    "<b>{}</b> - {} шт."
    "<i>{}</i>\n\n"
    "ℹ️{}\n"
    "{}\n"
    "{}\n"
    "<i>Лоты на Торговой Площадке:</i>\n"
    f"<b>{settings.GOLD_NAME}</b>: "
    "<b>{}</b>\n"
    f"<b>{settings.DIAMOND_NAME}</b>: "
    "<b>{}</b>"
)

NOT_CORRECT_AMOUNT_MESSAGE = (
    "<b>❌ Ошибка</b>\n\n" "Количество <b>Предметов</b> указано неверно!"
)

NOT_CORRECT_PRICE_MESSAGE = (
    "<b>❌ Ошибка</b>\n\n" "<b>Цена</b> указано неверно!"
)

NOT_ENOUGH_GOLD_MESSAGE = "<b>❌ Ошибка</b>\n\n" "Недостаточно 🟡Золота!"

NOT_ENOUGH_DIAMOND_MESSAGE = "<b>❌ Ошибка</b>\n\n" "Недостаточно 💎Алмазов!"

NOT_ENOUGH_REQUIRED_ITEMS_MESSAGE = (
    "<b>❌Ошибка!</b>\n\n" "Недостаточно необходимых предметов!"
)

NOT_UNKNOWN_ERROR_MESSAGE = (
    "<b>❌ Ошибка</b>\n\n"
    "Произошла неизвестная ошибка! Обратитесь в поддержку"
)

ALREADY_KILLED_MESSAGE = "❌ Ошибка!\n\n" "<b>{}</b> уже убит!"
