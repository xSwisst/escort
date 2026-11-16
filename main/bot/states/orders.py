from aiogram.fsm.state import State, StatesGroup


class OrderAddressCreate(StatesGroup):
    title = State()
    address = State()


class OrderCheckState(StatesGroup):
    waiting_for_check = State()
