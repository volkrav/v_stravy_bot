from typing import NamedTuple

from aiogram.dispatcher.filters.state import State, StatesGroup


class Start(StatesGroup):
    free = State()

class Profile(StatesGroup):
    view = State()


class Ordering(StatesGroup):
    start = State()
    delivery_or_pickup = State()
    pickup = State()
    delivery = State()
    get_address = State()
    get_name = State()
    get_phone = State()
    ask_user_used_data = State()
    ask_user_checked_order = State()
    ask_user_remember_data = State()


class Product(NamedTuple):
    uid: str
    title: str
    price: int
    descr: str
    text: str
    img: str
    quantity: str
    gallery: str
    url: str
    partuids: str


class Order(NamedTuple):
    pickup: bool
    name: str
    phone: str
    address: str


class ViewOrder(NamedTuple):
    text: str
    amount: int


class User(NamedTuple):
    id: int
    name: str
    address: str
    pickup: bool
    phone: str


class Buy(StatesGroup):
    free_state = State()
    add_quantity = State()
    view_order = State()
    change_order = State()
    change_quantity = State()
