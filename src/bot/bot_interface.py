import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from django.conf import settings
from loguru import logger
from redis.asyncio.client import Redis

from bot.character.backpack.handlers import backpack_router
from bot.character.handlers import character_router
from bot.character.shop.handlers import shop_router
from bot.character.skills.handlers import character_skills_router
from bot.clan.bosses.handlers import clan_bosses_router
from bot.clan.bosses.utils import make_clan_bosses_schedulers_after_restart
from bot.clan.handlers import clan_router
from bot.clan.members.handlers import clan_members_router
from bot.clan.requests.handlers import clan_request_router
from bot.clan.settings.handlers import clan_settings_router
from bot.clan.warehouse.handlers import clan_warehouse_router
from bot.clan.wars.handlers import clan_wars_router
from bot.command.handlers import command_router
from bot.constants import commands
from bot.location.handlers import location_router
from bot.location.utils import make_location_bosses_schedulers_after_restart
from bot.marketplace.handlers import marketplace_router
from bot.master_shop.handlers import master_shop_router
from bot.premium_shop.handlers import premium_router
from bot.top.handlers import top_router


async def on_startup(bot: Bot):
    """Метод настройки Webhook."""
    logger.info("Bot has been started")
    await bot.set_webhook(settings.WEBHOOK_URL, drop_pending_updates=True)
    logger.info("Webhook has been set up")


class AiogramApp:
    """Класс бота."""

    def __init__(self) -> None:
        """Создает бота."""
        self.__TOKEN = settings.TELEGRAM_TOKEN
        self.bot = Bot(token=self.__TOKEN, parse_mode="HTML")
        self.dispatcher = Dispatcher(bot=self.bot)
        self.scheduler = AsyncIOScheduler()
        logger.info("Bot instance created")

    def _download_routes(self, routes):
        """Добавляет роуты боту."""
        head = self.dispatcher
        for route in routes:
            tail = route
            head.include_router(tail)
            head = route

    def _make_jobs(self):
        """Добавляет нужные шедулеры."""
        asyncio.ensure_future(
            make_clan_bosses_schedulers_after_restart(self.bot)
        )
        asyncio.ensure_future(
            make_location_bosses_schedulers_after_restart(self.bot)
        )

    def start(self) -> None:
        """Запускает бота."""
        routes = [
            command_router,
            character_router,
            character_skills_router,
            location_router,
            backpack_router,
            shop_router,
            marketplace_router,
            premium_router,
            clan_router,
            clan_request_router,
            clan_members_router,
            clan_settings_router,
            clan_wars_router,
            clan_bosses_router,
            clan_warehouse_router,
            top_router,
            master_shop_router,
        ]
        self._download_routes(routes)
        asyncio.ensure_future(
            self.bot.set_my_commands(
                [
                    BotCommand(
                        command=commands.START_COMMAND,
                        description=commands.START_DESCRIPTION,
                    ),
                    BotCommand(
                        command=commands.HELP_COMMAND,
                        description=commands.HELP_DESCRIPTION,
                    ),
                    BotCommand(
                        command=commands.SUPPORT_COMMAND,
                        description=commands.SUPPORT_DESCRIPTION,
                    ),
                ]
            )
        )
        storage = MemoryStorage()
        if settings.REDIS:
            redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
            storage = RedisStorage(redis)
        if settings.WEBHOOK_ENABLED:
            self.dispatcher.startup.register(on_startup)
            app = web.Application()
            webhook_requests_handler = SimpleRequestHandler(
                dispatcher=self.dispatcher,
                bot=self.bot,
            )
            webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)
            setup_application(
                app, self.dispatcher, bot=self.bot, storage=storage
            )
            asyncio.ensure_future(
                web._run_app(
                    app,
                    host=settings.WEB_SERVER_HOST,
                    port=settings.WEB_SERVER_PORT,
                )
            )
        else:
            asyncio.ensure_future(
                self.dispatcher.start_polling(
                    self.bot, skip_updates=True, storage=storage
                )
            )
        self.scheduler.start()
        self._make_jobs()

    def stop(self) -> None:
        """Останавливает бота."""
        asyncio.ensure_future(self.dispatcher.stop_polling())

    def get_bot(self):
        """Метод получения бота."""
        return self.bot

    def get_scheduler(self):
        """Метод получения шедулера."""
        return self.scheduler
