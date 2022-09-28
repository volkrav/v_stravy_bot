import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import aiogram.utils.markdown as fmt
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageToDeleteNotFound

from app.handlers import order, start
from app.handlers.cart import Buy
from app.keyboards import reply
from app.misc import view
from app.services import utils
from app.config import Config
from app.misc.states import Ordering


logger = logging.getLogger(__name__)


async def command_start_ordering(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data.setdefault('ordering', {})
    await message.answer('Готовий до оформлення замовлення')
    logger.info(
        f'command_start_ordering OK {message.from_user.id} started placing an order')
    if await utils.check_user_in_users(message.from_user.id):
        await Ordering.ask_user_used_data.set()
        return await message.answer('Я можу використати Ваші дані з попереднього замовлення?',
                                    reply_markup=reply.kb_yes_or_no_without_cancel)

    await _ask_user_pickup_or_delivery(message, state)


async def command_cancel_ordering(message: types.Message, state: FSMContext):
    logger.info(
        f'command_cancel_ordering OK {message.from_user.id} canceled order')
    await order.command_view_order(message, state)


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

    # Перевіряю відповідь, доставка чи самовивіз
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

    # Перевіряю відповідь, використати дані користувача чи ні
    elif message.text == 'Ні' and current_state == 'Ordering:ask_user_used_data':
        logger.info(
            f'command_yes_or_no OK {message.from_user.id} selected not to used_data')
        await _ask_user_pickup_or_delivery(message, state)

    elif message.text == 'Так' and current_state == 'Ordering:ask_user_used_data':
        logger.info(
            f'command_yes_or_no OK {message.from_user.id} selected used_data')
        await _write_user_data_to_order(message, state)

    # Перевіряю відповідь, запам'ятати дані користувача чи ні
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
        await utils.write_user_to_users(message, state)

    # Перевіряю відповідь, дані замовлення вірні чи ні
    elif message.text == 'Ні' and current_state == 'Ordering:ask_user_checked_order':
        logger.info(
            f'command_yes_or_no OK {message.from_user.id} answered order_data is not correct')
        return await order.command_view_order(message, state)

    elif message.text == 'Так' and current_state == 'Ordering:ask_user_checked_order':
        logger.info(
            f'command_yes_or_no OK {message.from_user.id} answered order_data is  correct')
        await _verified_order(message, state)

    # Обробка непідтримуваної команди
    else:
        logger.error(
            f'command_yes_or_no BAD {message.from_user.id} unsupported command {message.text}')
        if (current_state == 'Ordering:pickup' or
                current_state == 'Ordering:delivery'):
            markup = reply.kb_yes_or_no
        elif (current_state == 'Ordering:ask_user_remember_data' or
              current_state == 'Ordering:ask_user_used_data' or
              current_state == 'Ordering:ask_user_checked_order'):
            markup = reply.kb_yes_or_no_without_cancel
        await message.answer('Потрібно вибрати "Так" або "Ні" ⌨️⤵️',
                             reply_markup=markup)


async def _get_name(message: types.Message):
    await message.answer(text='Введіть, будь ласка, Ваше ім\'я: ⌨️⤵️',
                         reply_markup=reply.kb_cancel_ordering)
    await Ordering.get_name.set()


async def command_write_name(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['ordering']['name'] = fmt.quote_html(message.text)
        logger.info(
            f'command_write_name OK {message.from_user.id} entered name {message.text}')
        await _get_phone(message)
    except Exception as err:
        logger.error(
            f'command_write_name BAD {message.from_user.id} '
            f'get {err.args}')


async def _get_address(message: types.Message):
    await message.answer(text='Введіть, будь ласка, адресу доставки: ⌨️⤵️',
                         reply_markup=reply.kb_cancel_ordering)
    await Ordering.get_address.set()


async def command_write_address(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['ordering']['address'] = fmt.quote_html(message.text)
        logger.info(
            f'command_write_address OK {message.from_user.id} entered address {message.text}')
        await _get_name(message)
    except Exception as err:
        logger.error(
            f'command_write_address BAD {message.from_user.id} '
            f'get {err.args}')


async def _get_phone(message: types.Message):
    await message.answer('Для зв\'язку з Вами нам потрібен Ваш номер телефону. Натисніть ⌨️⤵️',
                         reply_markup=reply.kb_share_contact)
    await Ordering.get_phone.set()


async def command_write_phone(message: types.Message, state: FSMContext):
    if message.contact:
        try:
            async with state.proxy() as data:
                data['ordering']['phone'] = message.contact.phone_number
            logger.info(
                f'command_write_phone OK {message.from_user.id} '
                f'shared phone {await utils.format_phone_number(message.contact.phone_number)}')
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


async def _ask_user_pickup_or_delivery(message: types.Message, state: FSMContext):
    await Ordering.delivery_or_pickup.set()
    await message.answer('Замовлення потрібно буде доставити за адресою ' +
                         'чи Ви заберете самостійно?',
                         reply_markup=reply.kb_delivery_or_pickup)


async def _write_user_data_to_order(message: types.Message, state: FSMContext):
    user_data = await utils.get_user_data(message.from_user.id)
    try:
        async with state.proxy() as data:
            order_data = data.get('ordering')
            order_data['name'] = user_data.name
            order_data['address'] = user_data.address
            order_data['pickup'] = user_data.pickup
            order_data['phone'] = user_data.phone
            logger.info(
                f'_write_user_data_to_order OK {message.from_user.id} '
                f'used data {order_data}')
        await _create_order_list(message, state)
    except Exception as err:
        await message.answer('На жаль, за технічних причин, я не зміг використати ' +
                             'Ваші дані. Про дану проблему повідомлено адміністратора.\n\n' +
                             'Будь ласка, заповніть дані самостйно.')
        logger.error(
            f'_write_user_data_to_order BAD {message.from_user.id} get {err.args}')
        await _ask_user_pickup_or_delivery(message, state)


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
        f'• Контактний номер: {await utils.format_phone_number(order.phone)}\n'
        f'• Доставка: {order.address}\n\n')

    amount_payable = view_list_products.amount
    if order.pickup:
        amount_payable = round(amount_payable * 0.9)
    elif order.address and view_list_products.amount < 800:
        amount_payable += 150
        answer += 'Доставка: 150 грн.\n\n'
    answer += f'Сумма до сплати: {amount_payable} грн.'
    await message.answer('***** Ваше замовлення: *****\n\n' + answer)
    async with state.proxy() as data:
        data['answer'] = answer
    logger.info(
        f'_create_order_list OK {message.from_user.id} checked an order')
    await Ordering.ask_user_checked_order.set()
    await message.answer('👆 В замовленні всі дані вірні?\nЯ можу відправити його адміністратору?',
                         reply_markup=reply.kb_yes_or_no_without_cancel)


async def _verified_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    answer = data.get(
        'answer', f'Виникла непередбачувана помилка в замовленні:\n {data}')
    await _send_order_to_admins(message, answer)
    if not await utils.check_user_in_users(message.from_user.id):
        return await _ask_user_for_permission_remember_data(message, state)
    logger.info(
        f'_verified_order OK {message.from_user.id} successfully placed an order')
    await state.finish()
    await start.user_start(message, state)


async def _send_order_to_admins(message: types.Message, answer: str):
    config: Config = message.bot.get('config')
    for id_admin in config.tg_bot.admin_ids:
        await message.bot.send_message(chat_id=id_admin,
                                       text='<b>Отримано нове замовлення:</b>\n\n' + answer)
        logger.info(
            f'_send_order_to_admins OK {message.from_user.id} '
            f'bot sent order to admin {id_admin}')
    await message.answer('👍 Ваше замовлення відправлено адміністратору.')


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
                                    Ordering.ask_user_used_data,
                                    Ordering.ask_user_remember_data,
                                    Ordering.ask_user_checked_order
                                ])
    dp.register_message_handler(command_write_name,
                                state=Ordering.get_name)
    dp.register_message_handler(command_write_address,
                                state=Ordering.get_address)
    dp.register_message_handler(command_write_phone,
                                content_types=types.ContentType.ANY,
                                state=Ordering.get_phone)
