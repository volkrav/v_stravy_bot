from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageToDeleteNotFound
from aiogram.dispatcher.filters.state import StatesGroup, State

from app.keyboards import reply

from .order import command_view_order


class Ordering(StatesGroup):
    get_name = State()


async def command_start_ordering(message: types.Message, state: FSMContext):
    await state.finish()
    async with state.proxy() as data:
        print(f'test -> {data}')
    await message.answer('Готовий до оформлення замовлення', reply_markup=reply.kb_ordering)


async def command_cancel_ordering(message: types.Message, state: FSMContext):
    await command_view_order(message, state)


def register_ordering(dp: Dispatcher):
    dp.register_message_handler(command_start_ordering, Text(equals='🚀 Оформити',
                                           ignore_case=True), state='*')
    dp.register_message_handler(command_cancel_ordering, Text(equals='❌ Відміна',
                                                              ignore_case=True), state='*')


# ❌ Відміна
