from os import stat
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

from app.keyboards import reply
from app.services import utils
from .menu import list_products

my_cart = {}


class Buy(StatesGroup):
    add_quantity = State()


async def create_order(message: types.CallbackQuery, state: FSMContext):
    call = message
    await utils.delete_inline_keyboard(message.bot, message.from_user.id)

    await Buy.add_quantity.set()
    my_cart['user_id'] = call.from_user.id
    my_cart['product_uid'] = call.data.split(':')[-1]
    my_cart['partuid'] = call.data.split(':')[1]

    async with state.proxy() as data:
        data['partuid'] = call.data.split(':')[1]
        print(f'with state.proxy - {data["partuid"]}')

    await call.message.answer(f'Ви обрали {my_cart["product_uid"]}\n\n')
    await call.message.answer('Вкажіть кількість: введіть потрібне число, або натисніть кнопку ⌨️⤵️',
                              reply_markup=reply.kb_quantity)


async def do_not_add_product(message: types.Message, state: FSMContext):
    await message.answer('Добре 😇')
    data = await state.get_data()
    category = data['partuid']
    print(f'do_not_add_product - {category}')
    await state.finish()
    await list_products(message, category)


async def add_quantity_to_order(message: types.Message, state: FSMContext):

    try:
        my_cart['quantity'] = int(message.text)
        await message.answer(my_cart)
        await state.finish()
        await list_products(message, my_cart['partuid'])
    except ValueError:
        await message.answer(f'Кількість повинна бути числом, а ви вказали {message.text}.\n'
                             f'Потрібно прибрати зайві символи та пробіли.')
        await message.answer('Вкажіть кількість: введіть потрібне число, або натисніть кнопку ⌨️⤵️',
                             reply_markup=reply.kb_quantity)


def register_cart(dp: Dispatcher):
    dp.register_callback_query_handler(
        create_order, Text(startswith='buy:'), state='*')
    dp.register_message_handler(
        do_not_add_product, Text(equals='Передумав', ignore_case=True), state='*')
    dp.register_message_handler(add_quantity_to_order, state=Buy.add_quantity)

# ❌
