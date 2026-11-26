from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from bot.handlers import get_routers
from clients.api import api_client
from clients.logs import logs_client
from core.settings import settings
from repository.session import Database
from shared.bot.cbr import install_cbr
from shared.bot.middleware import DatabaseMiddleware
from shared.server.webhook import create_webhook_app

db = Database(settings.DATABASE_URL)


async def _close_clients() -> None:
    await api_client.close()
    await logs_client.close()
    await db.close()


def create_app():
    bot = Bot(settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    
    storage = None
    if settings.REDIS_URL:
        try:
            storage = RedisStorage.from_url(settings.REDIS_URL)
        except Exception:
            storage = None

    dispatcher = Dispatcher(storage=storage) if storage else Dispatcher()
    
    db_middleware = DatabaseMiddleware(db.session_maker)
    dispatcher.message.middleware(db_middleware)
    dispatcher.callback_query.middleware(db_middleware)

    for router in get_routers():
        dispatcher.include_router(router)

    cbr_startup, cbr_shutdown = install_cbr(
        bot=bot,
        dispatcher=dispatcher,
        bot_token=settings.BOT_TOKEN,
        redis_url=settings.REDIS_URL,
    )

    return create_webhook_app(
        bot=bot,
        dispatcher=dispatcher,
        webhook_url=settings.WEBHOOK_URL,
        webhook_secret=settings.WEBHOOK_SECRET_TOKEN,
        allowed_updates=["message", "edited_message", "callback_query"],
        on_startup=[cbr_startup],
        on_shutdown=[cbr_shutdown, _close_clients],
    )


app = create_app()
