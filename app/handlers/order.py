from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageToDeleteNotFound

from app.handlers import start
from app.handlers.cart import Buy
from app.keyboards import reply
from app.services import utils
from app.misc import view


async def command_view_order(message: types.Message, state: FSMContext):
    await Buy.view_order.set()
    await utils.delete_inline_keyboard(message.bot, message.from_user.id)

    async with state.proxy() as data:
        if 'order' in data and data['order'].keys():
            view_list_products = await view.list_products(data['order'])
            answer = '***** Ваше замовлення: *****\n\n' + view_list_products.text
            msg = await message.answer(text=answer, reply_markup=reply.kb_menu_view_order)
            data['msg_view_order'] = msg['message_id']
        else:
            answer = 'Кошик ще порожній, спершу оберіть товар'
            await message.answer(text=answer)
            await start.command_menu(message, state=state)


async def command_change_order(message: types.Message, state: FSMContext):
    await Buy.change_order.set()

    async with state.proxy() as data:
        try:
            await message.bot.delete_message(message.from_user.id, data['msg_view_order'])
        except MessageToDeleteNotFound:
            print(f'повідомлення {data["msg_view_order"]} вже було видалено')
        except KeyError:
            print(
                f'command_change_order Команда не актуальна, data[\'msg_view_order\'] не існує')

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
                keyboard=[[reply.KeyboardButton(text='❌ Вихід')]],
                resize_keyboard=True
            ))
            data['msg_change_order'] = msg['message_id']
        else:
            answer = 'Кошик ще порожній, спершу оберіть товар'
            await message.answer(answer)
            await start.command_menu(message, state)


async def command_change_quantity(message: types.Message, state: FSMContext):
    await Buy.change_quantity.set()
    current_uid = await _get_current_uid_from_part(message.text.split('/change')[-1], state)

    async with state.proxy() as data:
        try:
            await message.bot.delete_message(message.from_user.id, data['msg_change_order'])
        except MessageToDeleteNotFound:
            print(
                f'command_change_quantity - повідомлення {data["msg_change_order"]} вже було видалено')
        except KeyError:
            print(
                f'command_change_quantity Команда не актуальна, data[\'msg_view_order\'] не існує')

        current_quantity = data['order'][current_uid]
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
    except MessageToDeleteNotFound:
        print(
            f'command_change_quantity - повідомлення {message["message_id"]} вже було видалено')
    except KeyError:
        print(
            f'command_change_quantity Команда не актуальна, data[\'msg_view_order\'] не існує')

    await message.answer('Вкажіть кількість: введіть потрібне число, або натисніть кнопку ⌨️⤵️',
                         reply_markup=reply.kb_quantity)


async def add_new_quantity(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            current_uid = data['uid_for_change_quantity']
            data['order'][current_uid] = int(message.text)
        await message.answer(f'Кількість змінено!')
        await command_change_order(message, state)
    except ValueError:
        await message.answer(f'Кількість повинна бути числом, а ви вказали {message.text}.\n'
                             f'Потрібно прибрати зайві символи та пробіли.')
        await message.answer('Вкажіть кількість: введіть потрібне число, або натисніть кнопку ⌨️⤵️',
                             reply_markup=reply.kb_quantity)


async def command_del_product(message: types.Message, state: FSMContext):

    current_uid = await _get_current_uid_from_part(
        message.text.split('/del')[-1], state)
    try:
        await message.bot.delete_message(message.from_user.id, message['message_id'])
    except MessageToDeleteNotFound:
        print(
            f'command_del_product - повідомлення {message["message_id"]} вже було видалено')
    except KeyError:
        print(
            f'command_del_product Команда не актуальна, data[\'msg_view_order\'] не існує')

    async with state.proxy() as data:
        try:
            await message.bot.delete_message(message.from_user.id, data['msg_change_order'])
        except MessageToDeleteNotFound:
            print(
                f'command_change_quantity - повідомлення {data["msg_change_order"]} вже було видалено')
        except KeyError:
            print(
                f'command_del_product Команда не актуальна, data[\'msg_view_order\'] не існує')

        try:
            del data['order'][current_uid]
            await message.answer('Товар видалено!')
        except KeyError:
            print(f'товар {current_uid} вже було видалено')
    await command_change_order(message, state)


async def cancel_add_new_quantity(message: types.Message, state: FSMContext):
    await command_change_order(message, state)


async def command_clear_order(message: types.Message, state: FSMContext):
    await message.answer('Кошик очищено.')
    await state.finish()
    await start.command_menu(message, state=state)


async def command_back_to_view_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        await message.bot.delete_message(message.from_user.id, data['msg_change_order'])
    except MessageToDeleteNotFound:
        print(f'повідомлення {data["msg_change_order"]} вже було видалено')
    except KeyError:
        print(
            f'command_back_to_view_order Команда не актуальна, data[\'msg_view_order\'] не існує')

    await command_view_order(message, state)


async def command_back_to_command_menu(message: types.Message, state: FSMContext):
    await start.command_menu(message, state=state)


async def _get_current_uid_from_part(part_uid: int, state: FSMContext) -> str:
    async with state.proxy() as data:
        for uid in data['order'].keys():
            if part_uid in uid:
                return uid
    return None


def register_order(dp: Dispatcher):
    dp.register_message_handler(command_view_order,
                                Text(equals='Ваше замовлення',
                                     ignore_case=True),
                                state='*')
    dp.register_message_handler(command_back_to_command_menu,
                                Text(equals='↩️ До каталогу',
                                     ignore_case=True),
                                state=[None, Buy.view_order])
    dp.register_message_handler(command_change_order, Text(equals='✏️ Змінити',
                                                           ignore_case=True), state=Buy.view_order)
    dp.register_message_handler(command_clear_order, Text(equals='🧹 Очистити',
                                                          ignore_case=True), state=Buy.view_order)
    dp.register_message_handler(command_back_to_view_order,
                                Text(equals='❌ Вихід', ignore_case=True),
                                state=[Buy.change_order])
    dp.register_message_handler(command_change_quantity, Text(startswith='/change',
                                                              ignore_case=True), state=Buy.change_order)
    dp.register_message_handler(command_del_product, Text(startswith='/del',
                                                          ignore_case=True), state=Buy.change_order)
    dp.register_message_handler(cancel_add_new_quantity, Text(equals='Передумав',
                                                              ignore_case=True), state=Buy.change_quantity)
    dp.register_message_handler(add_new_quantity, state=Buy.change_quantity)
