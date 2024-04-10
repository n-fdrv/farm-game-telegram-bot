import datetime

from apscheduler.jobstores.base import JobLookupError
from django.apps import apps
from loguru import logger

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
async def remove_scheduler(job_id: str):
    """Удаление шедулера по id."""
    bot, scheduler = await get_bot_and_scheduler()
    try:
        scheduler.remove_job(job_id)
    except JobLookupError:
        logger.warning("Не удалось удалить job т.к. его не существует")


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


@log_schedulers
async def run_date_job(job, date, args):
    """Шедулер убийства персонажа."""
    bot, scheduler = await get_bot_and_scheduler()
    job = scheduler.add_job(
        job,
        "date",
        run_date=date,
        args=args,
    )
    return job
