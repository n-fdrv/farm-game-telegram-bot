import datetime

from apscheduler.jobstores.base import JobLookupError
from character.models import Character
from django.apps import apps
from loguru import logger

from bot.location.utils import end_hunting, kill_character
from bot.models import User
from core.config.logging import log_schedulers


async def get_bot_and_scheduler():
    """Метод получения бота и шедулера."""
    app_config = apps.get_app_config("bot")
    app = app_config.bot
    scheduler = app.get_scheduler()
    bot = app.get_bot()
    return bot, scheduler


@log_schedulers
async def send_message_to_all_users(text: str):
    """Шедулер отправки сообщения всем пользователям."""
    bot, scheduler = await get_bot_and_scheduler()
    async for user in User.objects.filter(is_admin=True):
        scheduler.add_job(
            bot.send_message,
            "date",
            run_date=datetime.datetime.now(),
            args=[user.telegram_id, text],
        )


@log_schedulers
async def hunting_end_scheduler(character: Character):
    """Шедулер отправки сообщения об окончании охоты."""
    bot, scheduler = await get_bot_and_scheduler()
    job = scheduler.add_job(
        end_hunting,
        "date",
        run_date=character.hunting_end,
        args=[character, bot],
    )
    character.job_id = job.id
    await character.asave(update_fields=("job_id",))


@log_schedulers
async def remove_scheduler(job_id: str):
    """Удаление шедулера по id."""
    bot, scheduler = await get_bot_and_scheduler()
    try:
        scheduler.remove_job(job_id)
    except JobLookupError:
        logger.warning("Не удалось удалить job т.к. его не существует")


@log_schedulers
async def kill_character_scheduler(
    character: Character, date, attacker: Character = None
):
    """Шедулер убийства персонажа."""
    bot, scheduler = await get_bot_and_scheduler()
    scheduler.add_job(
        kill_character,
        "date",
        run_date=date,
        args=[character, bot, attacker],
    )


@log_schedulers
async def send_message_to_user(user_id: int, text: str):
    """Шедулер отправки сообщения пользователю."""
    bot, scheduler = await get_bot_and_scheduler()
    scheduler.add_job(
        bot.send_message,
        "date",
        run_date=datetime.datetime.now(),
        args=[user_id, text],
    )
