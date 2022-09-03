from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

from app.keyboards import reply
from .menu import list_products

my_cart = {}


class Buy(StatesGroup):
    add_quantity = State()


async def create_order(message: types.CallbackQuery, **kwargs):
    await Buy.add_quantity.set()
    call = message
    print(call.data)
    my_cart['user_id'] = call.from_user.id
    my_cart['product_uid'] = call.data.split(':')[-1]
    my_cart['partuid'] = call.data.split(':')[1]

    await call.message.answer(f'Ви обрали {my_cart["product_uid"]}\n\n')
    await call.message.answer('Вкажіть кількість: введіть потрібне число, або натисніть кнопку ⌨️⤵️',
                              reply_markup=reply.kb_quantity)


async def add_quantity_to_order(message: types.Message, state: FSMContext):

    try:
        my_cart['quantity'] = int(message.text)
        await message.answer(my_cart)
        await state.finish()
        await list_products(message, my_cart['partuid'])
    except ValueError:
        await message.answer(f'Потрібно вказати ціле число, и ви вказали {message.text}')
        await message.answer('Вкажіть кількість: введіть потрібне число, або натисніть кнопку ⌨️⤵️',
                              reply_markup=reply.kb_quantity)
    # await state.finish()
    # await


def register_cart(dp: Dispatcher):
    dp.register_callback_query_handler(
        create_order, Text(startswith='buy:'))
    dp.register_message_handler(add_quantity_to_order, state=Buy.add_quantity)
