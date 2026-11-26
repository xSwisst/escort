"""
Callback & Inline Registry (CBR) — unified ephemeral token system for
`callback_data`, `switch_inline_query_current_chat`, and inline result payloads.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import re
import secrets
import time
from collections import OrderedDict
from typing import Any, Awaitable, Callable, Dict, Optional, Union

import redis.asyncio as aioredis
from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.client.session.middlewares.base import BaseRequestMiddleware
from aiogram.methods import AnswerInlineQuery
from aiogram.methods.base import TelegramMethod, TelegramType
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineQuery,
    InputTextMessageContent,
    Message,
    TelegramObject,
)

logger = logging.getLogger("cbr")

_TOKEN_LEN = 40
_DEFAULT_TTL = 604800  # 7 days
_MAX_LOCAL_SIZE = 50000
_MAX_INLINE_MAP_SIZE = 10000
_TOKEN_RE = re.compile(r"^[0-9a-f]{40}$")
_TOKEN_PREFIX_RE = re.compile(r"^([0-9a-f]{40})(.*)$", re.S)


class CallbackRegistry:
    """
    Token registry backed by Redis with an in-memory LRU fallback cache.
    Tokens are HMAC-SHA256 digests scoped to a specific Telegram user_id.
    """

    def __init__(self) -> None:
        self._redis: Optional[aioredis.Redis] = None
        self._local_cache: OrderedDict[str, tuple[str, float, bool]] = OrderedDict()
        self._inline_users: OrderedDict[str, int] = OrderedDict()
        self._salt = hashlib.sha256(b"escort_cbr_default_salt").digest()

    def configure_salt(self, secret: str) -> None:
        raw = (secret or "escort_cbr_default_salt").encode("utf-8")
        self._salt = hashlib.sha256(raw).digest()

    async def init_redis(self, redis_url: str) -> None:
        if not redis_url:
            return
        try:
            self._redis = aioredis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=2.0,
                socket_timeout=2.0,
            )
            await self._redis.ping()
            logger.info("CBR: connected to Redis")
        except Exception as exc:
            logger.warning("CBR: Redis unavailable (%s), using in-memory fallback", exc)
            self._redis = None

    async def close_redis(self) -> None:
        if self._redis is not None:
            try:
                await self._redis.aclose()
            except Exception:
                pass
            self._redis = None

    def remember_inline_query(self, inline_query_id: str, user_id: int) -> None:
        if not inline_query_id:
            return
        if len(self._inline_users) >= _MAX_INLINE_MAP_SIZE:
            self._inline_users.popitem(last=False)
        self._inline_users[inline_query_id] = user_id

    def pop_inline_query_user(self, inline_query_id: str) -> Optional[int]:
        return self._inline_users.pop(inline_query_id, None)

    def _generate_token(self, user_id: Union[int, str], data: str, one_time: bool = False) -> str:
        if one_time:
            raw = f"{user_id}:{data}:{secrets.token_hex(4)}".encode("utf-8")
        else:
            raw = f"{user_id}:{data}".encode("utf-8")
        return hmac.new(self._salt, raw, hashlib.sha256).hexdigest()[:_TOKEN_LEN]

    def get_token(self, user_id: Union[int, str], data: str) -> str:
        return self._generate_token(user_id, data, one_time=False)

    async def register(
        self,
        data: str,
        user_id: Union[int, str],
        ttl: int = _DEFAULT_TTL,
        one_time: bool = False,
    ) -> str:
        if self.is_token(data):
            return data

        token = self._generate_token(user_id, data, one_time=one_time)
        storage_key = f"cbr:{user_id}:{token}"
        expires_at = time.monotonic() + ttl

        if len(self._local_cache) >= _MAX_LOCAL_SIZE:
            self._local_cache.popitem(last=False)
        self._local_cache[storage_key] = (data, expires_at, one_time)

        if self._redis is not None:
            try:
                await self._redis.set(storage_key, data, ex=ttl)
            except Exception as exc:
                logger.debug("CBR Redis set failed (%s), cached in memory", exc)

        return token

    async def resolve(self, token: str, user_id: Union[int, str]) -> Optional[str]:
        storage_key = f"cbr:{user_id}:{token}"
        now = time.monotonic()

        cached = self._local_cache.get(storage_key)
        if cached is not None:
            data, expires_at, one_time = cached
            if now <= expires_at:
                if one_time:
                    self._local_cache.pop(storage_key, None)
                    if self._redis is not None:
                        try:
                            await self._redis.delete(storage_key)
                        except Exception:
                            pass
                return data
            self._local_cache.pop(storage_key, None)

        if self._redis is not None:
            try:
                data = await self._redis.get(storage_key)
                if data is not None:
                    self._local_cache[storage_key] = (data, now + 3600, False)
                    return data
            except Exception as exc:
                logger.debug("CBR Redis get failed (%s)", exc)

        return None

    def is_token(self, value: Optional[str]) -> bool:
        return bool(value and _TOKEN_RE.fullmatch(value))


cbr = CallbackRegistry()


class CbrRequestMiddleware(BaseRequestMiddleware):
    """
    Outgoing aiogram session middleware:
    - Replaces InlineKeyboardMarkup `callback_data` and `switch_inline_query_current_chat`
      with per-user tokens.
    - Replaces AnswerInlineQuery `InputTextMessageContent.message_text` with per-user tokens.
    """

    def __init__(self, registry: CallbackRegistry = cbr) -> None:
        self._registry = registry

    async def _rewrite_markup(self, markup: InlineKeyboardMarkup, user_id: Union[int, str]) -> tuple[InlineKeyboardMarkup, bool]:
        new_markup = markup.model_copy(deep=True)
        changed = False
        for row in new_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data and not self._registry.is_token(btn.callback_data):
                    is_one_time = ":pay:" in btn.callback_data or btn.callback_data.endswith(":pay")
                    btn.callback_data = await self._registry.register(
                        data=btn.callback_data,
                        user_id=user_id,
                        one_time=is_one_time,
                    )
                    changed = True

                inline_q = btn.switch_inline_query_current_chat
                if inline_q is not None and inline_q != "" and not _TOKEN_PREFIX_RE.match(inline_q):
                    token = await self._registry.register(data=inline_q, user_id=user_id)
                    btn.switch_inline_query_current_chat = f"{token} " if inline_q.endswith("=") else token
                    changed = True
        return new_markup, changed

    async def __call__(
        self,
        make_request: Callable[[Bot, TelegramMethod[TelegramType]], Awaitable[TelegramType]],
        bot: Bot,
        method: TelegramMethod[TelegramType],
    ) -> TelegramType:
        reply_markup = getattr(method, "reply_markup", None)
        if isinstance(reply_markup, InlineKeyboardMarkup):
            chat_id = getattr(method, "chat_id", None)
            if chat_id is not None:
                try:
                    user_id: Union[int, str] = int(chat_id)
                except (ValueError, TypeError):
                    user_id = str(chat_id)
                new_markup, changed = await self._rewrite_markup(reply_markup, user_id)
                if changed:
                    setattr(method, "reply_markup", new_markup)

        if isinstance(method, AnswerInlineQuery) and method.results:
            user_id = self._registry.pop_inline_query_user(method.inline_query_id)
            if user_id is not None:
                new_results = []
                changed = False
                for item in method.results:
                    imc = getattr(item, "input_message_content", None)
                    msg_text = getattr(imc, "message_text", None) if isinstance(imc, InputTextMessageContent) else None
                    if msg_text and msg_text != "None" and not self._registry.is_token(msg_text):
                        token = await self._registry.register(data=msg_text, user_id=user_id)
                        new_imc = imc.model_copy(update={"message_text": token})
                        new_item = item.model_copy(update={"input_message_content": new_imc})
                        new_results.append(new_item)
                        changed = True
                    else:
                        new_results.append(item)
                if changed:
                    method = method.model_copy(update={"results": new_results})

        return await make_request(bot, method)


class CbrMiddleware(BaseMiddleware):
    """
    Incoming outer middleware for CallbackQuery, InlineQuery, and Message:
    transparently resolves per-user CBR tokens back to original payloads.
    """

    def __init__(self, registry: CallbackRegistry = cbr) -> None:
        super().__init__()
        self._registry = registry

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, CallbackQuery) and event.data and event.from_user:
            raw = event.data
            if self._registry.is_token(raw):
                resolved = await self._registry.resolve(raw, event.from_user.id)
                if resolved is None:
                    try:
                        await event.answer("⚠️ Кнопка устарела или недоступна.", show_alert=True)
                    except Exception:
                        pass
                    return None
                event = event.model_copy(update={"data": resolved})

        elif isinstance(event, InlineQuery) and event.from_user:
            self._registry.remember_inline_query(event.id, event.from_user.id)
            raw_q = (event.query or "").strip()
            match = _TOKEN_PREFIX_RE.match(raw_q)
            if match:
                token, rest = match.group(1), match.group(2)
                resolved = await self._registry.resolve(token, event.from_user.id)
                if resolved is not None:
                    if resolved.endswith("="):
                        new_query = f"{resolved}{rest.lstrip()}"
                    else:
                        new_query = f"{resolved}{rest}"
                    event = event.model_copy(update={"query": new_query})

        elif isinstance(event, Message) and event.text and event.from_user:
            raw_text = event.text.strip()
            if self._registry.is_token(raw_text):
                resolved = await self._registry.resolve(raw_text, event.from_user.id)
                if resolved is not None:
                    event = event.model_copy(update={"text": resolved})

        return await handler(event, data)


def install_cbr(
    *,
    bot: Bot,
    dispatcher: Dispatcher,
    bot_token: str = "",
    redis_url: str = "",
) -> tuple[Callable[[], Awaitable[None]], Callable[[], Awaitable[None]]]:
    """
    Attach outgoing and incoming CBR middlewares to a bot + dispatcher and
    return `(on_startup, on_shutdown)` hooks for Redis lifecycle management.
    """
    cbr.configure_salt(bot_token)
    bot.session.middleware(CbrRequestMiddleware(cbr))

    incoming = CbrMiddleware(cbr)
    dispatcher.callback_query.outer_middleware(incoming)
    dispatcher.inline_query.outer_middleware(incoming)
    dispatcher.message.outer_middleware(incoming)

    async def _startup() -> None:
        await cbr.init_redis(redis_url)

    async def _shutdown() -> None:
        await cbr.close_redis()

    return _startup, _shutdown
