import logging

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
from app.config import Config


logger = logging.getLogger(__name__)


class Ordering(StatesGroup):
    start = State()
    delivery_or_pickup = State()
    pickup = State()
    delivery = State()
    get_address = State()
    get_name = State()
    get_phone = State()
    preparing_an_order_for_sent = State()
    ask_user_remember_data = State()


async def command_start_ordering(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data.setdefault('ordering', {})
    await message.answer('Готовий до оформлення замовлення', reply_markup=reply.kb_delivery_or_pickup)
    logger.info(
        f'command_start_ordering OK {message.from_user.id} started placing an order')
    await Ordering.delivery_or_pickup.set()


async def command_delivery_or_pickup(message: types.Message, state: FSMContext):
    if message.text == '💪 Самовивіз':
        await start.command_location(message, state)
        answer = "Продовжуємо оформлювати замовлення самовивізом?"
        await Ordering.pickup.set()
    elif message.text == '🚚 Доставка':
        await start.command_delivery(message, state)
        answer = "Оформити замовлення з доставкою?"
        await Ordering.delivery.set()
    else:
        logger.error(
            f'command_delivery_or_pickup BAD {message.from_user.id} unsupported command {message.text}')
        return await message.answer('Потрібно вибрати "Самовивіз" або "Доставка" ⌨️⤵️',
                                    reply_markup=reply.kb_delivery_or_pickup)
    await message.answer(answer, reply_markup=reply.kb_yes_or_no)


async def command_yes_or_no(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    # Перевіряю відповіді, доставки чи самовивіз
    if (message.text == 'Ні' and
            (current_state == 'Ordering:pickup' or
             current_state == 'Ordering:delivery')):
        return await command_start_ordering(message, state)

    elif message.text == 'Так' and current_state == 'Ordering:pickup':
        async with state.proxy() as data:
            data['ordering']['pickup'] = True
        logger.info(
            f'command_yes_or_no OK {message.from_user.id} selected pickup')
        await _get_name(message)

    elif message.text == 'Так' and current_state == 'Ordering:delivery':
        async with state.proxy() as data:
            data['ordering']['pickup'] = False
        logger.info(
            f'command_yes_or_no OK {message.from_user.id} selected delivery')
        await _get_address(message)

    # Перевіряю відповіді, запам'ятати дані користувача чи ні
    elif message.text == 'Ні' and current_state == 'Ordering:ask_user_remember_data':
        await message.answer('Зрозумів. Не записую Ваші дані')
        logger.info(
            f'command_yes_or_no OK {message.from_user.id} selected not to remember data')
        await state.finish()
        return await start.user_start(message, state)

    elif message.text == 'Так' and current_state == 'Ordering:ask_user_remember_data':
        await message.answer('Записую Ваші дані')
        logger.info(
            f'command_yes_or_no OK {message.from_user.id} selected to remember data')
        await state.finish()
        return await start.user_start(message, state)

    # Обробка непідтримуваної команди
    else:
        logger.error(
            f'command_yes_or_no BAD {message.from_user.id} unsupported command {message.text}')
        await message.answer('Потрібно вибрати "Так" або "Ні" ⌨️⤵️',
                             reply_markup=reply.kb_yes_or_no)


async def _get_address(message: types.Message):
    await message.answer(text='Введіть, будь ласка, адресу доставки: ⌨️⤵️',
                         reply_markup=reply.kb_cancel_ordering)
    await Ordering.get_address.set()


async def _get_name(message: types.Message):
    await message.answer(text='Введіть, будь ласка, Ваше ім\'я: ⌨️⤵️',
                         reply_markup=reply.kb_cancel_ordering)
    await Ordering.get_name.set()


async def command_write_name(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['ordering']['name'] = message.text
        logger.info(
            f'command_write_name OK {message.from_user.id} entered name {message.text}')
        await _get_phone(message)
    except Exception as err:
        logger.error(
            f'command_write_name BAD {message.from_user.id} '
            f'get {err.args}')

async def _get_phone(message: types.Message):
    await message.answer('Для зв\'язку з Вами нам потрібен Ваш номер телефону. Натисніть ⌨️⤵️',
                         reply_markup=reply.kb_share_contact)
    await Ordering.get_phone.set()


async def command_write_address(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['ordering']['address'] = message.text
        logger.info(
            f'command_write_address OK {message.from_user.id} entered address {message.text}')
        await _get_name(message)
    except Exception as err:
        logger.error(
            f'command_write_address BAD {message.from_user.id} '
            f'get {err.args}')


async def command_write_phone(message: types.Message, state: FSMContext):
    if message.contact:
        try:
            async with state.proxy() as data:
                data['ordering']['phone'] = message.contact.phone_number
            logger.info(
                f'command_write_phone OK {message.from_user.id} '
                f'shared phone {await _format_phone_number(message.contact.phone_number)}')
            await Ordering.preparing_an_order_for_sent.set()
            await _create_order_list(message, state)
        except Exception as err:
            logger.error(
                f'command_write_phone BAD {message.from_user.id} '
                f'get {err.args}')
    else:
        await message.answer('Натисніть, будь ласка, "Відправити номер" ⌨️⤵️',
                             reply_markup=reply.kb_share_contact)
        logger.error(
            f'command_write_phone BAD {message.from_user.id} '
            f'unsupported command {message.text}')


async def _create_order_list(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            view_list_products = await view.list_products(data['order'])
            order = await utils.create_order(data['ordering'])
        except Exception as err:
            logger.error(
                f'_create_order_list BAD {message.from_user.id} get {err.args}')

    answer = view_list_products.text + (
        f'<b>Деталі замовлення:</b>\n'
        f'• Ваше ім\'я: {order.name}\n'
        f'• Контактний номер: {await _format_phone_number(order.phone)}\n'
        f'• Доставка: {order.address}\n\n')

    amount_payable = view_list_products.amount
    if order.pickup:
        amount_payable = round(amount_payable * 0.9)
    elif order.address and view_list_products.amount < 800:
        amount_payable += 150
        answer += 'Доставка: 150 грн.\n\n'
    answer += f'Сумма до сплати: {amount_payable} грн.'
    await message.answer('***** Ваше замовлення: *****\n\n' + answer)
    await message.answer('👍 Ваше замовлення відправлено адміністратору.')
    logger.info(
        f'_create_order_list OK {message.from_user.id} placed an order')
    await _send_order_to_admins(message, answer)
    await _ask_user_for_permission_remember_data(message, state)


async def command_cancel_ordering(message: types.Message, state: FSMContext):
    logger.info(
        f'command_cancel_ordering OK {message.from_user.id} canceled order')
    await order.command_view_order(message, state)


async def _format_phone_number(phone: str) -> str:
    if '+' not in phone:
        phone = '+' + phone
    return (f'({phone[3:6]}) '
            f'{phone[6:9]}-'
            f'{phone[9:11]}-'
            f'{phone[11:]}'
            )


async def _send_order_to_admins(message: types.Message, answer: str):
    config: Config = message.bot.get('config')
    for id_admin in config.tg_bot.admin_ids:
        await message.bot.send_message(chat_id=id_admin,
                                       text='<b>Отримано нове замовлення:</b>\n\n' + answer)
        logger.info(
            f'_send_order_to_admins OK {message.from_user.id} '
            f'bot sent order to admin {id_admin}')


async def _ask_user_for_permission_remember_data(message: types.Message, state: FSMContext):
    await Ordering.ask_user_remember_data.set()
    await message.answer('❓Дозволите мені запам\'ятати Ваші контактні дані, ' +
                         'щоб наступного разу я міг запропонувати ввести іх замість Вас?',
                         reply_markup=reply.kb_yes_or_no_without_cancel)


def register_ordering(dp: Dispatcher):
    dp.register_message_handler(command_start_ordering,
                                Text(equals='🚀 Оформити', ignore_case=True),
                                state=Buy.view_order)
    dp.register_message_handler(command_cancel_ordering,
                                Text(equals='❌ Скасувати', ignore_case=True),
                                state='*')
    dp.register_message_handler(command_delivery_or_pickup,
                                state=Ordering.delivery_or_pickup)
    dp.register_message_handler(command_yes_or_no,
                                state=[
                                    Ordering.pickup,
                                    Ordering.delivery,
                                    Ordering.ask_user_remember_data,
                                ])
    # dp.register_message_handler(command_yes_or_no,
    #                             state=Ordering.delivery)
    dp.register_message_handler(command_write_name,
                                state=Ordering.get_name)
    dp.register_message_handler(command_write_address,
                                state=Ordering.get_address)
    dp.register_message_handler(command_write_phone,
                                content_types=types.ContentType.ANY,
                                state=Ordering.get_phone)

# ❌ Відміна
