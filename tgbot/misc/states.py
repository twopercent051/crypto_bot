from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMEditPrice(StatesGroup):
    home = State()
    buy_price = State()
    sell_price = State()
    wallet = State()


class FSMOffer(StatesGroup):
    home = State()
    net = State()
    wallet = State()
    pay_method = State()
    pay_details = State()
    finish = State()


class FSMConnect(StatesGroup):
    connect = State()
    mailing = State()



