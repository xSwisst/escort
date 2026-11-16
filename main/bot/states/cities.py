from aiogram.fsm.state import State, StatesGroup


class CityState(StatesGroup):
    waiting_city = State()
