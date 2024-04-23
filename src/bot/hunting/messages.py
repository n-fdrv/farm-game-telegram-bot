from core.config.game_config import MINUTES_FOR_ENTER_CLAN_RAID

HUNTING_ZONE_ENTER_MESSAGE = (
    "<b>🎯Охота начата!</b>\n\n" "<i>Зона Охоты:</i> <b>{}</b>\n\n" "{}"
)

HUNTING_ZONE_NOT_AVAILABLE = "<b>❌Данная Зона Охоты не доступна!</b>\n\n" "{}"

ALREADY_IN_ZONE_MESSAGE = "<b>❌Ошибка!</b>\n\n" "Вы уже охотитесь в <b>{}</b>"

PREPARING_HUNTING_END_MESSAGE = (
    "<b>🎯Охота окончена!</b>\n\n"
    "⏳ Высчитываем полученный <b>🔮Опыт</b> и <b>🪵Трофеи</b>\n\n"
    "⚠️ Это занимает приблизительно 5-10 секунд"
)

HUNTING_CONTINUE_MESSAGE = "🎯Охота продолжается!"

HUNTING_END_MESSAGE = "🎯Охота окончена!"

HUNTING_STAT_MESSAGE = (
    "ℹ️<b>Статистика Охоты:</b>\n\n"
    "<i>🔮Получено Опыта:</i> <b>{}%</b>\n"
    "<i>⚔️Убито Монстров:</i> <b>{}</b>\n"
    "<i>🪵Трофеи:</i> <b>{}</b>\n\n"
    "{}"
)

EXIT_HUNTING_CONFIRMATION_MESSAGE = (
    "<b>⚠️Подтверждение!</b>\n\n"
    "Вы уверены, что закончить <b>🎯Охоту</b> и "
    "выйти из <b>{}</b>"
)

BOSS_LIST_MESSAGE = (
    "<b>☠️Боссы Локации</b>\n\n"
    "Когда Вы охотитесь в данной локации "
    "у Вас есть возможность участвовать в охоте следующих боссов."
)

GET_LOCATION_BOSS_MESSAGE = "<b>{}</b>\n\n" "<i>Возможные Трофеи:</i>\n{}"

NOT_ENOUGH_POWER_MESSAGE = (
    "<b>❌ Ошибка!</b>\n\n"
    "Недостаточно силы, чтобы участвовать в охоте на <b>{}</b>!"
)

SUCCESS_ACCEPT_BOSS_MESSAGE = (
    "<b>✅Успешно!</b>\n\n" "Вы приняли участие в охоте на <b>{}</b>!"
)

ALERT_ABOUT_BOSS_RESPAWN_MESSAGE = (
    "<b>⚠️ Уведомление</b>\n\n"
    "Босс <b>{}</b> воскрес\n\n"
    "Желаете участвовать в охоте на него?\n\n"
    f"❗️ У вас есть {MINUTES_FOR_ENTER_CLAN_RAID} минута чтобы принять участие"
)

NO_BOSS_KILLED_MESSAGE = (
    "<b>⚠️ Уведомление</b>\n\n"
    "Никто не осмелился поучаствовать в охоте на Босса!\n\n"
    "<b>{}</b> ушел в свое логово на некоторое время!"
)

SUCCESS_BOSS_KILLED_MESSAGE = (
    "<b>⚠️ Уведомление</b>\n\n"
    "Босс <b>{}</b> убит!\n\n"
    "Персонаж <b>{}</b> победил в схватке и забрал "
    "трофеи себе\n"
    "<i>Трофеи с Босса:</i> <b>{}</b>"
)
