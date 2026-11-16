from aiogram.fsm.state import State, StatesGroup


class AddressCreate(StatesGroup):
    title = State()
    address = State()


class AddressEdit(StatesGroup):
    title = State()
    address = State()
