from aiogram.fsm.state import State, StatesGroup


class VAMalling(StatesGroup):
    audience = State()
    message = State()
    settings = State()
    add_media = State()
    add_media_confirm = State()
    button_text = State()
    button_value = State()
    button_confirm = State()
