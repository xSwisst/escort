from aiogram.fsm.state import State, StatesGroup


class VANewModel(StatesGroup):
    params = State()
    prices = State()
    photos = State()


class VAEditParam(StatesGroup):
    value = State()


class VAAddPhoto(StatesGroup):
    waiting = State()


class VANewReview(StatesGroup):
    input_text = State()


class VAEditReview(StatesGroup):
    input_text = State()


class VANewService(StatesGroup):
    input_text = State()


class VAEditService(StatesGroup):
    input_text = State()


class VANewAdditional(StatesGroup):
    input_text = State()


class VAEditAdditional(StatesGroup):
    input_text = State()
