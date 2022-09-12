from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageToDeleteNotFound
from aiogram.dispatcher.filters.state import StatesGroup, State

from app.keyboards import reply

from app.handlers import order
from app.handlers import start
from app.handlers import echo
from app.handlers.cart import Buy



class Ordering(StatesGroup):
    start = State()
    delivery_or_pickup = State()
    pickup = State()
    get_name = State()
    get_phone = State()


async def command_start_ordering(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data.setdefault('ordering', {})
    await message.answer('Готовий до оформлення замовлення', reply_markup=reply.kb_delivery_or_pickup)
    await Ordering.delivery_or_pickup.set()


async def command_delivery(message: types.Message, state: FSMContext):
    if message.text == '💪 Самовивіз':
        await start.command_location(message, state)
        await message.answer(text="Продовжуємо оформлювати замовлення самовивізом?",
                             reply_markup=reply.kb_yes_or_no)
        await Ordering.pickup.set()
    elif message.text == '🚚 Доставка':
        await start.command_delivery(message, state)
        await message.answer(text="Оформити замовлення з доставкою?",
                             reply_markup=reply.kb_yes_or_no)
    else:
        await echo.bot_echo(message, state)


async def command_pickup(message: types.Message, state: FSMContext):
    if message.text == 'Ні':
        await command_start_ordering(message, state)
    elif message.text == 'Так':
        async with state.proxy() as data:
            data['ordering']['pickup'] = True
        await message.answer(text='Введіть, будь ласка, Ваше ім\'я:',
                             reply_markup=reply.kb_cancel_ordering)
        await Ordering.get_name.set()


async def command_get_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['ordering']['name'] = message.text
        await message.answer(data['ordering'])
    await message.answer('Для зв\'язку з Вами нам потрібен Ваш номер телефону.',
                         reply_markup=reply.kb_share_contact)
    await Ordering.get_phone.set()


async def command_get_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['ordering']['phone'] = message.contact.phone_number
        await message.answer(data['ordering'])

async def command_cancel_ordering(message: types.Message, state: FSMContext):
    await order.command_view_order(message, state)


def register_ordering(dp: Dispatcher):
    dp.register_message_handler(command_start_ordering, Text(equals='🚀 Оформити',
                                                             ignore_case=True), state=Buy.view_order)
    dp.register_message_handler(command_cancel_ordering, Text(equals='❌ Скасувати',
                                                              ignore_case=True), state='*')
    dp.register_message_handler(command_delivery,
                                state=Ordering.delivery_or_pickup)
    dp.register_message_handler(command_pickup, state=Ordering.pickup)
    dp.register_message_handler(command_get_name, state=Ordering.get_name)
    dp.register_message_handler(command_get_phone, content_types=types.ContentType.CONTACT,
                                state=Ordering.get_phone)

# ❌ Відміна
