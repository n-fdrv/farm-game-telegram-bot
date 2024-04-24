from django.conf import settings

ITEM_PREVIEW_MESSAGE = (
    "<b>🎒Инвентарь</b>\n\n"
    f"{settings.GOLD_NAME}: "
    "<b>{}</b>\n"
    f"{settings.DIAMOND_NAME}: "
    "<b>{}</b>"
)

ITEM_LIST_MESSAGE = "<b>🎒Инвентарь</b>"

SUCCESS_USE_MESSAGE = (
    "<b>✅ Успех</b>\n\n"
    "<i>Использовано:</i> <b>{}</b>\n"
    "<i>Осталось:</i> <b>{} шт.</b>"
)

SUCCESS_OPEN_BAG_MESSAGE = (
    "<b>✅ Успех</b>\n\n"
    "<i>Открыто:</i> <b>{}</b> - <b>{}</b> шт.\n"
    "<i>Получено:</i>\n<b>{}</b>\n\n"
    "<i>Осталось:</i> <b>{} шт.</b>"
)

SCROLL_LIST_MESSAGE = "Выберите предмет для улучшения"

ENHANCE_GET_MESSAGE = (
    "<b>{}\n{}</b>\n{}\n"
    "<i>🎲Шанс улучшения:</i> <b>{}</b>%\n"
    "<i>✅При успехе:</i>\n"
    "- <i>Характеристики</i> повысятся на <b>{}</b>\n"
    "- <i>Процентные характеристики</i> повысятся на <b>{}</b>\n"
    "<i>⚠️При неудаче:</i>\n"
    "- Предмет будет уничтожен"
)

EQUIP_IN_LOCATION_MESSAGE = (
    "<b>❌ Ошибка</b>\n\n" "Нельзя экипировать вещи во время охоты!"
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

SUCCESS_ENCHANT = (
    "<b>✅ Успех</b>\n\n"
    "Улучшение прошло успешно!\n"
    "<i>Получено:</i> <b>{}</b>\n"
)

NOT_CORRECT_CHARACTER_CLASS_MESSAGE = (
    "<b>❌ Неудача</b>\n\n"
    "Класс <b>Персонажа</b> не соответствует требуемому"
)

NOT_CORRECT_CHARACTER_SKILL_MESSAGE = (
    "<b>❌ Неудача</b>\n\n" "У Вас нет требуемой <b>Способности</b>"
)

NOT_ENOUGH_CHARACTER_LEVEL_MESSAGE = (
    "<b>❌ Неудача</b>\n\n" "Недостаточный уровень <b>Персонажа</b>"
)

ALREADY_KNOWN_SKILL_MESSAGE = (
    "<b>❌ Неудача</b>\n\n" "Вы уже знаете данную способность"
)

PUT_CONFIRM_MESSAGE = (
    "<b>⚠️ Подтверждение</b>\n\n"
    "Вы уверены, что хотите отправить: \n\n"
    "<b>{} - {} шт.</b>\n\n"
    "Клану: <b>{}</b>"
)

ENTER_AMOUNT_TO_CLAN_MESSAGE = (
    "<b>📩Передача Предмета</b>\n\n"
    "Введите количество <b>{}</b>\n"
    "Для передачи клану <b>{}</b>\n\n"
    "<i>❗️ В наличии:</i> <b>{} шт.</b>"
)

SUCCESS_PUT_MESSAGE_TO_USER = (
    "<b>📩Передача Предмета</b>\n\n"
    "<b>{}</b> положил в клановое хранилище:\n\n"
    "<b>{} - {} шт.</b>\n\n"
)

SUCCESS_PUT_MESSAGE = (
    "<b>✅ Успешно</b>\n\n"
    "Вы отправили:\n\n"
    "<b>{} - {} шт.</b>\n\n"
    "Клану: <b>{}</b>"
)
