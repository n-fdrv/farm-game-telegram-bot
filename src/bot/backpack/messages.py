from django.conf import settings

ITEM_PREVIEW_MESSAGE = (
    "<b>🎒Инвентарь</b>\n\n"
    f"{settings.GOLD_NAME}: "
    "<b>{}</b>\n"
    f"{settings.DIAMOND_NAME}: "
    "<b>{}</b>"
)

ITEM_LIST_MESSAGE = "<b>🎒Инвентарь</b>"

ITEM_GET_MESSAGE = "<b>{}</b> - {} шт. <i>{}</i>\n\n" "ℹ️{}\n" "{}\n" "{}"

SUCCESS_USE_MESSAGE = "<b>✅ Успех</b>\n\n" "Использовано: <b>{}</b>"

SUCCESS_OPEN_BAG_MESSAGE = (
    "<b>✅ Успех</b>\n\n"
    "Открыто: <b>{}</b> - <b>{}</b> шт.\n"
    "Получено: <b>{}</b>\n"
    "Осталось: <b>{} шт.</b>"
)

SCROLL_LIST_MESSAGE = "Выберите предмет для улучшения"

ENHANCE_GET_MESSAGE = (
    "<b>{}\n{}</b>\n{}\n"
    "<i>🎲Шанс улучшения:</i> <b>{}</b>%\n"
    "<i>✅При успехе:</i>\n"
    "- <i>Характеристики</i> повысятся на <b>{}</b>\n"
    "- <i>Процентные характеристики</i> повысятся на <b>{}</b>\n"
    "<i>⚠️При неудаче:</i>\n"
    "- Предмет останется с тем же уровнем улучшения"
)

NOT_CORRECT_EQUIPMENT_TYPE_MESSAGE = (
    "<b>❌ Неудача</b>\n\n"
    "Данный тип экипировки не подходит Вашему персонажу!"
)

EQUIP_MESSAGE = "<b>✅ Успех</b>\n\n" "Экипировка успешно надета"

UNEQUIP_MESSAGE = "<b>✅ Успех</b>\n\n" "Экипировка успешно снята"

NO_BRACELET_MESSAGE = (
    "<b>❌ Неудача</b>\n\n"
    "Для экипировки <b>Талисмана</b> требуется <b>Браслет</b>"
)

NOT_ENOUGH_BRACELET_LEVEL_MESSAGE = (
    "<b>❌ Неудача</b>\n\n"
    "Вы можете носить только <b>{}</b> Талисман(ов) одновремено.\n"
    "Для увеличения данного количества - улучшите свой Браслет"
)


NOT_MASTER_CLASS_MESSAGE = (
    "<b>❌ Неудача</b>\n\n" "Изучать рецепты может только <b>🔨Мастер</b>"
)

NOT_ENOUGH_SKILL_LEVEL_MESSAGE = (
    "<b>❌ Неудача</b>\n\n"
    "Недостаточный уровень умения <b>Мастер Создания</b>"
)

ALREADY_KNOWN_RECIPE = (
    "<b>❌ Неудача</b>\n\n"
    "Данный рецепт уже есть в вашей <b>Книге Рецептов</b>"
)

NOT_CORRECT_SCROLL_TYPE_MESSAGE = (
    "<b>❌ Неудача</b>\n\n"
    "Некорректный тип свитка для данного <b>Предмета</b>"
)

FAILURE_ENCHANT = "<b>❌ Неудача</b>\n\n" "Улучшение не удалось!\n"

SUCCESS_ENCHANT = "<b>✅ Успех</b>\n\n" "Улучшение прошло успешно!\n"
