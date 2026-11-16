import os

from shared.bot.texts import TextLoader

_loader = TextLoader(os.path.dirname(__file__))
t = _loader.t
btn = _loader.btn

__all__ = ["btn", "t"]
