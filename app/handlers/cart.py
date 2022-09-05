from os import stat
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

from app.keyboards import reply
from app.services import utils
from .menu import list_products


class Buy(StatesGroup):
    free_state = State()
    add_quantity = State()
    view_order = State()
    change_order = State()
    change_quantity = State()


async def create_order(message: types.CallbackQuery, state: FSMContext):
    call = message
    product_uid = call.data.split(':')[-1]

    await utils.delete_inline_keyboard(message.bot, message.from_user.id)

    await Buy.add_quantity.set()
    async with state.proxy() as data:
        data.setdefault('order', {})
        data['order'][product_uid] = 0
        data['current_uid'] = product_uid
        data['partuid'] = call.data.split(':')[1]
        current_title = data["current_title"]
        print(f'create_order -> {data}')

    await call.message.answer(f'Ви обрали <b>{current_title}</b>')
    await call.message.answer('Вкажіть кількість: введіть потрібне число, або натисніть кнопку ⌨️⤵️',
                              reply_markup=reply.kb_quantity)




async def add_quantity_to_order(message: types.Message, state: FSMContext):

    try:
        async with state.proxy() as data:
            current_uid = data['current_uid']
            data['order'][current_uid] = int(message.text)
            await message.answer(f'Додав до кошика:\n\n <b>{data["order"][current_uid]} шт. * '
                                 f'{data["current_title"]}</b>',
                                 reply_markup=reply.kb_catalog)
        # await state.finish()
            await Buy.free_state.set()
            await list_products(message, data['partuid'], state=state)
    except ValueError:
        await message.answer(f'Кількість повинна бути числом, а ви вказали {message.text}.\n'
                             f'Потрібно прибрати зайві символи та пробіли.')
        await message.answer('Вкажіть кількість: введіть потрібне число, або натисніть кнопку ⌨️⤵️',
                             reply_markup=reply.kb_quantity)


async def do_not_add_product(message: types.Message, state: FSMContext):
    await message.answer('Добре 😇', reply_markup=reply.kb_catalog)
    await Buy.free_state.set()
    async with state.proxy() as data:
        del data['order'][data['current_uid']]
        category = data['partuid']
    # await state.finish()
    await list_products(message, category, state=state)


def register_cart(dp: Dispatcher):
    dp.register_callback_query_handler(
        create_order, Text(startswith='buy:'), state='*')
    dp.register_message_handler(
        do_not_add_product, Text(equals='Передумав', ignore_case=True), state='*')
    dp.register_message_handler(add_quantity_to_order, state=Buy.add_quantity)

# ❌
