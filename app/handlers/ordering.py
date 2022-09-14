from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageToDeleteNotFound

from app.handlers import echo, order, start
from app.handlers.cart import Buy
from app.keyboards import reply
from app.misc import view
from app.services import utils


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
        answer = "Продовжуємо оформлювати замовлення самовивізом?"
        await Ordering.pickup.set()
    elif message.text == '🚚 Доставка':
        await start.command_delivery(message, state)
        answer = "Оформити замовлення з доставкою?"
    else:
        return await echo.bot_echo(message, state)
    await message.answer(answer, reply_markup=reply.kb_yes_or_no)


async def command_pickup(message: types.Message, state: FSMContext):
    if message.text == 'Ні':
        return await command_start_ordering(message, state)
    elif message.text == 'Так':
        async with state.proxy() as data:
            data['ordering']['pickup'] = True
    await message.answer(text='Введіть, будь ласка, Ваше ім\'я: ⌨️⤵️',
                         reply_markup=reply.kb_cancel_ordering)
    await Ordering.get_name.set()


async def command_get_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['ordering']['name'] = message.text
        await message.answer(data['ordering'])
    await message.answer('Для зв\'язку з Вами нам потрібен Ваш номер телефону. Натисніть ⌨️⤵️',
                         reply_markup=reply.kb_share_contact)
    await Ordering.get_phone.set()


async def command_get_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['ordering']['phone'] = message.contact.phone_number
    await _create_order_list(message, state)


async def _create_order_list(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            view_list_products = await view.list_products(data['order'])
            order = await utils.create_order(data['ordering'])
        except KeyError:
            print('_create_order_list - KeyError: "order"')
            return await echo.bot_echo(message, state)
    answer = ('***** Ваше замовлення: *****\n\n'
              + view_list_products.text)
    if order.pickup:
        amount_payable = round(view_list_products.amount * 0.9)
    answer += (
        f'<b>Деталі замовлення:</b>\n'
        f'• Ваше ім\'я: {order.name}\n'
        f'• Контактний номер: {await _format_phone_number(order.phone)}\n'
        f'• Доставка: {order.address}\n\n'
    )
    answer += f'Сумма до сплати: {amount_payable} грн.'
    await message.answer(answer)
    await message.answer("Ваше замовлення відправлено адміністратору.")
    await send_order_to_admins(message, answer)
    # await message


async def command_cancel_ordering(message: types.Message, state: FSMContext):
    await order.command_view_order(message, state)


async def _format_phone_number(phone: str) -> str:
    if '+' not in phone:
        phone = '+' + phone
    return (f'({phone[3:6]}) '
            f'{phone[6:9]}-'
            f'{phone[9:11]}-'
            f'{phone[11:]}'
            )


async def send_order_to_admins(message: types.Message, answer: str):
    config = message.bot.get('config')
    for id_admin in config.tg_bot.admin_ids:
        await message.bot.send_message(chat_id=message.from_user.id, text=answer)


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
