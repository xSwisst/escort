from aiogram.fsm.state import State, StatesGroup


class SearchCodeState(StatesGroup):
    code = State()
