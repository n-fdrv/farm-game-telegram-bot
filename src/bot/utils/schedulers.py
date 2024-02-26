import datetime

from apscheduler.jobstores.base import JobLookupError
from character.models import Character
from django.apps import apps
from loguru import logger

from bot.character.utils import kill_character
from bot.location.keyboards import get_drop_keyboard
from bot.location.messages import HUNTING_END_MESSAGE
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
async def hunting_end_scheduler(user: User):
    """Шедулер отправки сообщения об окончании охоты."""
    bot, scheduler = await get_bot_and_scheduler()
    keyboard = await get_drop_keyboard()
    job = scheduler.add_job(
        bot.send_message,
        "date",
        run_date=user.character.hunting_end,
        kwargs={
            "chat_id": user.telegram_id,
            "text": HUNTING_END_MESSAGE,
            "reply_markup": keyboard.as_markup(),
        },
    )
    user.character.job_id = job.id
    await user.character.asave(update_fields=("job_id",))


@log_schedulers
async def remove_scheduler(job_id: str):
    """Удаление шедулера по id."""
    bot, scheduler = await get_bot_and_scheduler()
    try:
        scheduler.remove_job(job_id)
    except JobLookupError:
        logger.warning("Не удалось удалить job т.к. его не существует")


@log_schedulers
async def kill_character_scheduler(character: Character, date):
    """Шедулер убийства персонажа."""
    bot, scheduler = await get_bot_and_scheduler()
    scheduler.add_job(
        kill_character,
        "date",
        run_date=date,
        args=[character, bot],
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
