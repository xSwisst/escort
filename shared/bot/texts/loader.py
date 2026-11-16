"""
Unified YAML-based text/button loader.
"""
from __future__ import annotations

import os
from typing import Any

import yaml


class _SafeMap(dict):
    def __getitem__(self, key: str) -> Any:
        val = super().get(key)
        return "" if val is None else val

    def __missing__(self, key: str) -> str:
        return ""


COLOR_TO_STYLE: dict[str, str] = {
    "red": "danger",
    "danger": "danger",
    "green": "success",
    "success": "success",
    "geren": "success",
    "blue": "primary",
    "primary": "primary",
}


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


class TextLoader:
    def __init__(self, base_dir: str, default_lang: str = "ru"):
        self._default_lang = default_lang
        self._localized = os.path.isdir(os.path.join(base_dir, default_lang))

        if self._localized:
            self._messages: dict[str, dict] = {}
            self._buttons: dict[str, dict] = {}
            for entry in os.scandir(base_dir):
                if not entry.is_dir():
                    continue
                lang = entry.name
                messages_path = os.path.join(entry.path, "messages.yaml")
                buttons_path = os.path.join(entry.path, "buttons.yaml")
                if os.path.exists(messages_path):
                    self._messages[lang] = _load(messages_path)
                if os.path.exists(buttons_path):
                    self._buttons[lang] = _load(buttons_path)
        else:
            messages_path = os.path.join(base_dir, "messages.yaml")
            buttons_path = os.path.join(base_dir, "buttons.yaml")
            self._messages_flat = _load(messages_path) if os.path.exists(messages_path) else {}
            self._buttons_flat = _load(buttons_path) if os.path.exists(buttons_path) else {}

    def t(self, key: str, lang: str | None = None, **kwargs: Any) -> str:
        if self._localized:
            data = self._messages.get(lang or self._default_lang, {})
        else:
            data = self._messages_flat
        text = str(data.get(key, key))
        if kwargs and "{" in text:
            try:
                text = text.format_map(_SafeMap(kwargs))
            except Exception:
                import re
                def replacer(match):
                    k = match.group(1)
                    val = kwargs.get(k)
                    return "" if val is None else str(val)
                text = re.sub(r"\{([a-zA-Z0-9_]+)\}", replacer, text)
        return text

    def btn(self, key: str, lang: str | None = None, **overrides: Any) -> dict:
        if self._localized:
            data = self._buttons.get(lang or self._default_lang, {})
        else:
            data = self._buttons_flat
        raw_val = data.get(key, {"text": key})
        if isinstance(raw_val, str):
            result = {"text": raw_val}
        else:
            result = dict(raw_val)

        text = str(result.get("text", ""))
        if overrides and "{" in text and "text" not in overrides:
            try:
                result["text"] = text.format_map(_SafeMap(overrides))
            except Exception:
                pass

        result.update(overrides)

        color = result.pop("color", None)
        if color:
            style = COLOR_TO_STYLE.get(str(color).lower())
            if style:
                result["style"] = style

        return {name: value for name, value in result.items() if value is not None}



