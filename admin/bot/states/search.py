from aiogram.fsm.state import State, StatesGroup


class ClientSearchState(StatesGroup):
    waiting_query = State()


class VASendMessage(StatesGroup):
    text = State()


class VAManageBalance(StatesGroup):
    waiting_amount = State()
