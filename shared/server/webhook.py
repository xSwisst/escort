from __future__ import annotations

import inspect
from contextlib import asynccontextmanager
from typing import Any, Callable, Sequence
from urllib.parse import urlparse

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import FastAPI, Request, Response


async def _run_hook(callback: Callable, bot: Bot) -> None:
    params = inspect.signature(callback).parameters
    result = callback(bot) if params else callback()
    if inspect.isawaitable(result):
        await result


def create_webhook_app(
    *,
    bot: Bot,
    dispatcher: Dispatcher,
    api_factory: Callable[[], FastAPI] | None = None,
    webhook_url: str,
    webhook_secret: str = "",
    allowed_updates: list[str] | None = None,
    drop_pending: bool = True,
    on_startup: Sequence[Callable] | None = None,
    on_shutdown: Sequence[Callable] | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.bot = bot
        app.state.dispatcher = dispatcher

        kwargs: dict[str, Any] = {
            "url": webhook_url,
            "secret_token": webhook_secret,
            "drop_pending_updates": drop_pending,
        }
        if allowed_updates:
            kwargs["allowed_updates"] = allowed_updates
        if webhook_url:
            await bot.set_webhook(**kwargs)

        if on_startup:
            for hook in on_startup:
                await _run_hook(hook, bot)

        yield

        if on_shutdown:
            for hook in on_shutdown:
                await _run_hook(hook, bot)

        if webhook_url:
            await bot.delete_webhook()
        await bot.session.close()

    app = api_factory() if api_factory else FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.router.lifespan_context = lifespan

    webhook_path = urlparse(webhook_url).path if webhook_url else "/webhook"

    @app.post(webhook_path)
    async def webhook_handler(request: Request) -> Response:
        if not webhook_secret:
            return Response(status_code=403)
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret != webhook_secret:
            return Response(status_code=403)
        raw = await request.json()
        update = Update.model_validate(raw, context={"bot": bot})
        await dispatcher.feed_update(bot=bot, update=update, dispatcher=dispatcher)
        return Response(status_code=200)

    return app
