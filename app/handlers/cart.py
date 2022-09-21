import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.keyboards import reply
from app.services import utils

from .menu import list_products

logger = logging.getLogger(__name__)


class Buy(StatesGroup):
    free_state = State()
    add_quantity = State()
    view_order = State()
    change_order = State()
    change_quantity = State()


async def add_to_basket(message: types.CallbackQuery, state: FSMContext):
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

    # struct INFO - назва_метода статус_виконання користувач коментар

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
            logger.info(f'add_quantity_to_order OK {message.from_user.id} added sku={current_uid} quantity={(data["order"][current_uid])} to basket')
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
    try:
        async with state.proxy() as data:
            del data['order'][data['current_uid']]
            category = data['partuid']
        # await state.finish()
        await list_products(message, category, state=state)
    except KeyError as err:
        logger.error(err.args)


def register_cart(dp: Dispatcher):
    dp.register_callback_query_handler(
        add_to_basket, Text(startswith='buy:'), state='*')
    dp.register_message_handler(
        do_not_add_product, Text(equals='Передумав', ignore_case=True), state='*')
    dp.register_message_handler(add_quantity_to_order, state=Buy.add_quantity)

# ❌
