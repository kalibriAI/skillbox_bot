from aiogram.fsm.state import State, StatesGroup


class HotelSearchMachine(StatesGroup):
    search_type = State()
    destination = State()
    longitude = State()
    latitude = State()
    location = State()
    check_in = State()
    check_out = State()
    result_size = State()
    sort = State()
    min_price = State()
    max_price = State()
