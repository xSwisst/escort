from aiogram.fsm.state import State, StatesGroup


class VANewAgreement(StatesGroup):
    name = State()
    url = State()
