from core.config.game_config import RESET_POWER_DIAMOND_COST

POWER_LIST_MESSAGE = (
    "<b>✨Сила</b>\n\n"
    "<i>✨Очков Силы:</i> <b>{}</b>\n\n"
    "<i>❤️Здоровье:</i> <b>+{}</b> <i>🔷Мана:</i> <b>+{}</b>\n"
    "<i>⚔️Атака:</i> <b>+{}</b> <i>🛡Защита:</i> <b>+{}</b>\n"
    "<i>🎯Точность:</i> <b>+{}</b> <i>🥾Уклонение:</i> <b>+{}</b>\n"
    "<i>🎲Шанс Крит. Удара:</i> <b>+{}%</b> "
    "<i>♦️Сила Крит. Удара:</i> <b>+{}%</b>\n\n"
)


POWER_RESET_CONFIRM_MESSAGE = (
    "<b>⚠️ Подтверждение</b>\n\n"
    "Вы уверены, что сбросить распределение силы?\n\n"
    f"❗️Стоимость услуги: {RESET_POWER_DIAMOND_COST}💎"
)

SUCCESS_POWER_RESET_MESSAGE = (
    "<b>✅Успешно!</b>\n\n" "Вы сбросили распределение силы!"
)

POWER_GET_MESSAGE = (
    "<b>{}</b>\n\n" "<i>{}</i> <b>+{}</b>\n\n" "<i>Стоимость:</i> <b>{}✨</b>"
)

POWER_ADD_CONFIRM_MESSAGE = (
    "<b>⚠️ Подтверждение</b>\n\n" "Вы уверены, что добавить новую силу?\n\n"
)

NOT_ENOUGH_SKILL_POINTS_MESSAGE = "❌ Ошибка!\n\n" "Недостаточно очков силы!"

SUCCESS_POWER_ADD_MESSAGE = (
    "<b>✅Успешно!</b>\n\n" "Вы добавили новую силу:\n\n" "<b>{}</b>"
)
