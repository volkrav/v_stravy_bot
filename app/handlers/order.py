from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageToDeleteNotFound
from aiogram.utils.markdown import hcode
from app.handlers.cart import Buy
from app.keyboards import reply
from app.services import utils

from .start import command_menu


async def command_view_order(message: types.Message, state: FSMContext):
    await Buy.view_order.set()
    await utils.delete_inline_keyboard(message.bot, message.from_user.id)

    async with state.proxy() as data:
        if 'order' in data and data['order'].keys():
            current_order = data['order']
            product_list = await utils.create_product_list(current_order.keys())
            answer = '***** Ваше замовлення: *****\n\n'
            amount_payable = 0
            for index, product in enumerate(product_list, 1):
                amount_payable += current_order[product.uid] * product.price
                answer += (f'# {index} \n'
                           f'<b>{current_order[product.uid]} шт. * {product.title}</b>\n'
                           f'Ціна: {product.price} грн.\n'
                           f'Всього: {current_order[product.uid] * product.price} грн.\n\n'
                           )
            answer += f'Сумма до сплати: {amount_payable} грн.'
            msg = await message.answer(text=answer, reply_markup=reply.kb_menu_view_order)
            data['msg_view_order'] = msg['message_id']
        else:
            answer = 'Кошик ще порожній, спершу оберіть товар'
            await message.answer(text=answer)
            await command_menu(message, state=state)


async def command_change_order(message: types.Message, state: FSMContext):
    await Buy.change_order.set()

    async with state.proxy() as data:
        try:
            await message.bot.delete_message(message.from_user.id, data['msg_view_order'])
        except MessageToDeleteNotFound:
            print(f'повідомлення {data["msg_view_order"]} вже було видалено')

        if 'order' in data and data['order'].keys():
            current_order = data['order']
            product_list = await utils.create_product_list(current_order.keys())
            answer = '***** Редагуємо замовлення: *****\n\n'
            amount_payable = 0
            for index, product in enumerate(product_list, 1):
                amount_payable += current_order[product.uid] * product.price
                answer += (f'# {index} \n'
                           f'<b>{current_order[product.uid]} шт. * {product.title}</b>\n'
                           f'Ціна: {product.price} грн.\n'
                           f'Всього: {current_order[product.uid] * product.price} грн.\n'
                           f'Змінити кількість: натисніть  /change{product.uid[:5]}\n'
                           f'Видалити: натисніть  /del{product.uid[:5]}\n\n'
                           )
            answer += f'Сумма до сплати: {amount_payable} грн.'
            msg = await message.answer(text=answer, reply_markup=reply.ReplyKeyboardMarkup(
                keyboard=[[reply.KeyboardButton(text='✖️ Вихід')]],
                resize_keyboard=True
            ))
            data['msg_change_order'] = msg['message_id']
        else:
            answer = 'Кошик ще порожній, спершу оберіть товар'
            await message.answer(answer)
            await command_menu(message, state)


async def command_change_quantity(message: types.Message, state: FSMContext):
    await Buy.change_quantity.set()
    part_of_uid = message.text.split('/change')[-1]

    async with state.proxy() as data:
        try:
            await message.bot.delete_message(message.from_user.id, data['msg_change_order'])
        except MessageToDeleteNotFound:
            print(f'повідомлення {data["msg_view_order"]} вже було видалено')

        for uid, quantity in data['order'].items():
            if part_of_uid in uid:
                current_uid = uid
                current_quantity = quantity
                data['uid_for_change_quantity'] = current_uid

    product = await utils.create_product(current_uid)
    await message.bot.send_photo(
        message.from_user.id,
        photo=product.img,
        caption=(
            f'<b>{product.title}</b>\n\n'
            f'Кількість в замовленні: {current_quantity} шт.'
        )
    )
    try:
        await message.bot.delete_message(message.from_user.id, message['message_id'])
    except Exception as err:
        print(err)
    await message.answer('Вкажіть кількість: введіть потрібне число, або натисніть кнопку ⌨️⤵️',
                         reply_markup=reply.kb_quantity)


async def add_new_quantity(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            current_uid = data['uid_for_change_quantity']
        
        await message.answer(f'{current_uid} - {int(message.text)}')
    except ValueError:
        await message.answer(f'Кількість повинна бути числом, а ви вказали {message.text}.\n'
                             f'Потрібно прибрати зайві символи та пробіли.')
        await message.answer('Вкажіть кількість: введіть потрібне число, або натисніть кнопку ⌨️⤵️',
                             reply_markup=reply.kb_quantity)

async def cancel_add_new_quantity(message: types.Message, state: FSMContext):
    await command_change_order(message, state)


async def command_clear_order(message: types.Message, state: FSMContext):
    await message.answer('Кошик очищено.')
    await state.finish()
    await command_menu(message, state=state)


async def command_back_to_view_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        await message.bot.delete_message(message.from_user.id, data['msg_change_order'])
    except MessageToDeleteNotFound:
        print(f'повідомлення {data["msg_view_order"]} вже було видалено')
    await command_view_order(message, state)


async def command_back_to_command_menu(message: types.Message, state: FSMContext):
    await command_menu(message, state=state)


def register_order(dp: Dispatcher):
    dp.register_message_handler(command_view_order,
                                Text(equals='Ваше замовлення',
                                     ignore_case=True),
                                state='*')
    dp.register_message_handler(command_back_to_command_menu, Text(equals='↩️ До каталогу',
                                                                   ignore_case=True), state=Buy.view_order)
    dp.register_message_handler(command_change_order, Text(equals='✏️ Змінити',
                                                           ignore_case=True), state=Buy.view_order)
    dp.register_message_handler(command_clear_order, Text(equals='🧹 Очистити',
                                                          ignore_case=True), state=Buy.view_order)
    dp.register_message_handler(command_back_to_view_order, Text(equals='✖️ Вихід',
                                                                 ignore_case=True), state=Buy.change_order)
    dp.register_message_handler(command_change_quantity, Text(startswith='/change',
                                                              ignore_case=True), state=Buy.change_order)
    dp.register_message_handler(cancel_add_new_quantity, Text(equals='Передумав',
                                                              ignore_case=True), state=Buy.change_quantity)
    dp.register_message_handler(add_new_quantity, state=Buy.change_quantity)
