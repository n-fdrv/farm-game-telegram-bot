from core.config import game_config

WARS_LIST_MESSAGE = "<b>⚔️Клановые Войны</b>"

ACCEPT_WAR_CONFIRM_MESSAGE = (
    "<b>⚠️ Подтверждение</b>\n\n"
    "Вы уверены, что хотите начать войну?\n\n"
    "❗️ После начала войны:\n"
    f"1️⃣ Потеря опыта при смерти от члена враждующего клана: "
    f"<b>{game_config.WAR_EXP_DECREASE_PERCENT}%</b>\n"
    "2️⃣ При убийстве члена враждующего клана "
    "Ваш Клан отберет: <b>🚩 1 Репутацию</b>\n"
    "3️⃣ Вы не получите Эффект <b>♦️Усталость</b>"
    " при убийстве члена враждующего клана"
)

ALERT_NEW_WAR_MESSAGE = (
    "<b>⚔️Новая Война Кланов</b>\n\n" "Начата война:\n" "<b>{}</b> ⚔️ <b>{}</b>"
)

SUCCESS_ACCEPTING_WAR_MESSAGE = (
    "✅ Успешно!\n\n" "Принята война от клана <b>{}</b>"
)

END_WAR_CONFIRM_MESSAGE = (
    "<b>⚠️ Подтверждение</b>\n\n"
    "Вы уверены, что хотите окончить войну?\n\n"
    f"❗️ Требуется  <b>🚩 {game_config.WAR_END_REPUTATION_COST} Репутации</b>"
    f" которая перейдет победившему Клану"
)

ALERT_END_WAR_MESSAGE = (
    "<b>🏳️Война Кланов окончена</b>\n\n"
    "Клан <b>{}</b> сдался\n"
    "Клан <b>{}</b> получил "
    f"<b>🚩 {game_config.WAR_END_REPUTATION_COST} Репутации</b>"
)

NOT_ENOUGH_REPUTATION_MESSAGE = (
    "<b>❌ Неудачно!</b>\n\n" "Недостаточно <b>🚩Репутации</b>"
)

SUCCESS_ENDING_WAR_MESSAGE = "✅ Успешно!\n\n" "Война с <b>{}</b> окончена!"
