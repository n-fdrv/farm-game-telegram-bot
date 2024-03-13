from bot.premium_shop.buttons import (
    DIAMONDS_BUTTON,
    PREMIUM_BUTTON,
    START_PACK_BUTTON,
)
from core.config import game_config

PREMIUM_LIST_MESSAGE = (
    "<b>🏬 Премиум Магазин</b>\n\n"
    "<i>Здесь ты можешь:</i>\n"
    "1️⃣Пополнить баланс <b>💎Алмазов</b>\n"
    "2️⃣Купить <b>🎟Премиум Подписку</b>\n"
    "3️⃣Купить <b>⚔️Стартовый Набор</b> для упрощенного развития"
)

NO_CHARACTER_MESSAGE = (
    "❌ Ошибка!\n\n"
    "Чтобы пользоваться <b>🏬 Премиум Магазином</b> "
    "требуется создать персонажа"
)

PREMIUM_GET_MESSAGE = {
    DIAMONDS_BUTTON: (
        "💎Алмазы\n\n"
        "С помощью 💎Алмазов можно купить "
        "предметы в <b>🏬 Премиум Магазине</b> "
        "и на <b>💱Торговой Площадке</b>"
    ),
    PREMIUM_BUTTON: (
        "<b>🎟Премиум Подписка</b>\n\n"
        "Ускоряет развитие твоего <b>Персонажа</b>\n\n"
        "<i>Эффекты:</i>\n"
        "<i>🔮Получение опыта:</i> "
        f"<b>+{game_config.PREMIUM_EXP_MODIFIER * 100 - 100}%</b>\n"
        "<i>🍀Шанс трофеев:</i>  "
        f"<b>+{game_config.PREMIUM_DROP_MODIFIER * 100 - 100}%</b>\n"
        "<i>🪦Потеря опыта при смерти:</i>  "
        f"<b>{game_config.PREMIUM_DEATH_EXP_MODIFIER * 100 - 100}%</b>"
    ),
    START_PACK_BUTTON: (
        "<b>⚔️Стартовый Набор</b>\n\n"
        "Содержит предметы для ускорения развития\n\n"
        "<i>Предметы:</i>\n"
        "<b>⚔️Классовое Оружие</b>\n"
        "<b>🛡Классовая Броня</b>\n"
        "<b>📦Мешок с Эликсирами (Обычный) - 40 шт.</b>\n"
    ),
}

NOT_ENOUGH_CURRENCY = "❌ Неудачно!\n\n" "Недостаточно <b>💎Алмазов</b>!"

SUCCESS_BUY_MESSAGE = "✅ Успешно!\n\n" "Получено: <b>{}</b>\n"
