from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageToDeleteNotFound
from aiogram.dispatcher.filters.state import StatesGroup, State

from app.keyboards import reply

from app.handlers import order
from app.handlers import start


class Ordering(StatesGroup):
    start = State()
    delivery = State()
    get_name = State()


async def command_start_ordering(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        print(f'test -> {data}')
    await message.answer('Готовий до оформлення замовлення', reply_markup=reply.kb_pickup_or_delivery)
    await Ordering.delivery.set()


async def command_delivery(message: types.Message, state: FSMContext):
    if message.text == '💪 Самовивіз':
        await start.command_location(message, state)
        await message.answer(text="Продовжуємо оформлювати замовлення самовивізом?",
                             reply_markup=reply.kb_yes_or_no)
    elif message.text == '🚚 Доставка':
        await start.command_delivery(message, state)
        await message.answer(text="Оформити замовлення з доставкою?",
                             reply_markup=reply.kb_yes_or_no)


async def command_cancel_ordering(message: types.Message, state: FSMContext):
    await order.command_view_order(message, state)


def register_ordering(dp: Dispatcher):
    dp.register_message_handler(command_start_ordering, Text(equals='🚀 Оформити',
                                                             ignore_case=True), state='*')
    dp.register_message_handler(command_cancel_ordering, Text(equals='❌ Скасувати',
                                                              ignore_case=True), state='*')
    dp.register_message_handler(command_delivery, state=Ordering.delivery)

# ❌ Відміна
