from core.config.game_config import MINUTES_FOR_ENTER_CLAN_RAID

CLAN_BOSSES_LIST_MESSAGE = (
    "<b>🎯Клановые Боссы</b>\n\n"
    "Регистрируйтесь на охоту на боссов и "
    "получайте ценные трофеи"
)

GET_CLAN_BOSS_MESSAGE = (
    "<b>{}</b>\n\n"
    "<i>Ваш клан:</i> <b>{}</b>\n\n"
    "<i>Возможные Трофеи:</i>\n{}"
)

NOT_ENOUGH_POWER_MESSAGE = (
    "❌ Неудачно!\n\n" "Недостаточная сила клана для данного Босса!"
)

ALERT_ABOUT_CLAN_BOSS_RESPAWN_MESSAGE = (
    "<b>⚠️ Уведомление</b>\n\n"
    "Клановый босс <b>{}</b> воскрес\n\n"
    "Желаете участвовать в охоте на него?\n\n"
    f"❗️ У вас есть {MINUTES_FOR_ENTER_CLAN_RAID} минута чтобы принять участие"
)

ALREADY_KILLED_CLAN_BOSS_MESSAGE = "❌ Ошибка!\n\n" "<b>{}</b> уже убит!"

SUCCESS_ACCEPT_CLAN_RAID_MESSAGE = (
    "<b>✅Успешно!</b>\n\n" "Вы приняли участие в охоте на <b>{}</b>!"
)

NO_BOSS_KILLED_MESSAGE = (
    "<b>⚠️ Уведомление</b>\n\n"
    "Вам не удалось одолеть кланового босса\n\n"
    "<b>{}</b> ушел в свое логово на некоторое время!"
)

SUCCESS_BOSS_KILLED_MESSAGE = (
    "<b>⚠️ Уведомление</b>\n\n"
    "Клановый босс <b>{}</b> убит!\n\n"
    "Клан <b>{}</b> победил в схватке Кланов и забрал "
    "трофеи себе\n"
    "<i>Участники победившего клана:</i> <b>{}</b>\n\n"
    "<i>Трофеи с Босса:</i> <b>{}</b>"
)
