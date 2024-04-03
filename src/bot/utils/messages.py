from django.conf import settings

BOOK_INFO_MESSAGE = (
    "\n<i>Требуемый класс:</i> <b>{}</b>\n"
    "<i>Требуемый уровень:</i> <b>{}</b>\n"
    "<i>Требуемая способность:</i> <b>{}</b>\n"
)

ITEM_GET_MESSAGE = (
    "<b>{}</b> - {} шт. "
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
