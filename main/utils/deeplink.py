from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ActionType = Literal["open_model"] | None
_SEPARATOR = "__"


@dataclass
class DeeplinkPayload:
    action: ActionType = None
    action_arg: str | None = None


def parse_deeplink(args: str | None) -> DeeplinkPayload:
    if not args:
        return DeeplinkPayload()
    payload = DeeplinkPayload()
    for part in args.split(_SEPARATOR):
        if part.startswith("open_model_"):
            payload.action = "open_model"
            payload.action_arg = part[len("open_model_"):]
    return payload


def build_model_link(bot_username: str, form_code: str) -> str:
    args = f"open_model_{form_code}"
    return f"https://t.me/{bot_username.lstrip('@')}?start={args}"
