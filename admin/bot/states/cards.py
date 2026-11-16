from aiogram.fsm.state import State, StatesGroup


class VANewCard(StatesGroup):
    number = State()
    limits = State()
    confirm = State()
