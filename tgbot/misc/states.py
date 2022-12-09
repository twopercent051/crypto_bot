from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMEditPrice(StatesGroup):
    home = State()
    buy_price = State()
    sell_price = State()


class FSMOffer(StatesGroup):
    home = State()
    operation = State()

class FSMConnect(StatesGroup):
    connect = State()



