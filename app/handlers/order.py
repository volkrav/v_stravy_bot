import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageToDeleteNotFound

from app.handlers import start
from app.keyboards import reply
from app.services import utils
from app.misc import view
from app.misc.states import Buy


logger = logging.getLogger(__name__)


async def command_view_order(message: types.Message, state: FSMContext):
    logger.info(
        f'command_view_order OK {message.from_user.id} looking at your order')

    try:
        try:
            await utils.delete_inline_keyboard(message.bot, message.from_user.id)
            logger.info(
                f'command_view_order OK {message.from_user.id} inline keyboard was removed')
        except MessageToDeleteNotFound:
            logger.warning(
                f'command_view_order BAD {message.from_user.id} inline keyboard was removed earlier')
        except Exception as err:
            logger.error(
                f'command_view_order utils.delete_inline_keyboard '
                f'BAD {message.from_user.id} get {err.args}')

        async with state.proxy() as data:
            await Buy.view_order.set()

            if 'order' in data and data['order'].keys():
                await message.answer('В цьому розділі можна оформити, змінити або ' +
                                     'очистити Ваше замовлення.',
                                     reply_markup=reply.kb_menu_view_order)

                view_list_products = await view.list_products(data['order'])
                answer = '***** Ваше замовлення: *****\n\n' + view_list_products.text
                msg = await message.answer(text=answer)
                data['msg_view_order'] = msg['message_id']
            else:
                answer = 'Кошик ще порожній, спершу оберіть товар'
                await message.answer(text=answer)
                await start.command_menu(message, state=state)
    except Exception as err:
        logger.error(
            f'command_view_order '
            f'BAD {message.from_user.id} get {err.args}')


async def command_change_order(message: types.Message, state: FSMContext):
    try:
        await Buy.change_order.set()

        async with state.proxy() as data:
            try:
                await message.bot.delete_message(message.from_user.id, data['msg_view_order'])
            except MessageToDeleteNotFound:
                logger.warning(
                    f'command_change_order '
                    f'BAD {message.from_user.id} message was removed earlier')
            except KeyError as err:
                logger.error(
                    f'command_change_order message.bot.delete_message '
                    f'BAD {message.from_user.id} get {err.args}')

            if 'order' in data and data['order'].keys():
                await message.answer('Використовуйте команди <b>change...</b> для зміни кількості ' +
                                     'або <b>del...</b> для видалення товару ⤵️',
                                     reply_markup=reply.ReplyKeyboardMarkup(
                                         keyboard=[
                                             [reply.KeyboardButton(text='❌ Вихід')]],
                                         resize_keyboard=True
                                     ))
                current_order = data['order']
                product_list = await utils.create_product_list(current_order.keys())
                answer = '***** Редагуємо замовлення: *****\n\n'
                amount_payable = 0
                for index, product in enumerate(product_list, 1):
                    amount_payable += current_order[product.uid] * \
                        product.price
                    answer += (f'# {index} \n'
                               f'<b>{current_order[product.uid]} шт. * {product.title}</b>\n'
                               f'Ціна: {product.price} грн.\n'
                               f'Всього: {current_order[product.uid] * product.price} грн.\n'
                               f'<b>Змінити кількість:</b> натисніть -> <b>/change{product.uid[:5]}</b>\n'
                               f'<b>Видалити:</b> натисніть -> <b>/del{product.uid[:5]}</b>\n\n'
                               )
                answer += f'Сумма: {amount_payable} грн.'
                msg = await message.answer(text=answer)
                data['msg_change_order'] = msg['message_id']
            else:
                answer = 'Кошик ще порожній, спершу оберіть товар'
                await message.answer(answer)
                await start.command_menu(message, state)
    except Exception as err:
        logger.error(
            f'command_change_order '
            f'BAD {message.from_user.id} get {err.args}')


async def command_change_quantity(message: types.Message, state: FSMContext):

    try:
        await Buy.change_quantity.set()
        current_uid = await _get_current_uid_from_part(message.text.split('/change')[-1], state)
        if current_uid:
            async with state.proxy() as data:
                try:
                    await message.bot.delete_message(message.from_user.id, data['msg_change_order'])
                except MessageToDeleteNotFound:
                    logger.warning(
                        f'command_change_quantity '
                        f'BAD {message.from_user.id} message was removed earlier')
                except KeyError as err:
                    logger.error(
                        f'command_change_quantity message.bot.delete_message '
                        f'BAD {message.from_user.id} get {err.args}')

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
                logger.warning(
                    f'command_change_quantity '
                    f'OK {message.from_user.id} message was removed earlier')
            except KeyError as err:
                logger.error(
                    f'command_change_quantity message.bot.delete_message '
                    f'BAD {message.from_user.id} get {err.args}')

            await message.answer('Вкажіть кількість: введіть потрібне число, або натисніть кнопку ⌨️⤵️',
                                 reply_markup=reply.kb_quantity)
        else:
            logger.warning(
                f'command_change_quantity '
                f'BAD {message.from_user.id} used the wrong command {message.text}')

            return await command_change_order(message, state)
    except Exception as err:
        logger.error(
            f'command_change_quantity '
            f'BAD {message.from_user.id} get {err.args}')


async def add_new_quantity(message: types.Message, state: FSMContext):
    try:
        try:
            async with state.proxy() as data:
                current_uid = data['uid_for_change_quantity']
                data['order'][current_uid] = int(message.text)
            await message.answer(f'Кількість змінено!')
            logger.info(
                f'add_new_quantity OK {message.from_user.id} '
                f'changed quantity to {int(message.text)}')

            await command_change_order(message, state)
        except ValueError:
            logger.warning(
                f'add_new_quantity '
                f'BAD {message.from_user.id} entered the wrong value {message.text}')

            await message.answer(f'Кількість повинна бути числом, а ви вказали {message.text}.\n'
                                 f'Потрібно прибрати зайві символи та пробіли.')
            await message.answer('Вкажіть кількість: введіть потрібне число, або натисніть кнопку ⌨️⤵️',
                                 reply_markup=reply.kb_quantity)
    except Exception as err:
        logger.error(
            f'add_new_quantity '
            f'BAD {message.from_user.id} get {err.args}')


async def command_del_product(message: types.Message, state: FSMContext):
    try:
        current_uid = await _get_current_uid_from_part(
            message.text.split('/del')[-1], state)
        try:
            await message.bot.delete_message(message.from_user.id, message['message_id'])
        except MessageToDeleteNotFound:
            logger.warning(
                f'command_del_product '
                f'OK {message.from_user.id} message was removed earlier')
        except KeyError as err:
            logger.error(
                f'command_del_product message.bot.delete_message '
                f'BAD {message.from_user.id} get {err.args}')
        if current_uid:
            async with state.proxy() as data:
                try:
                    await message.bot.delete_message(message.from_user.id, data['msg_change_order'])
                except MessageToDeleteNotFound:
                    logger.warning(
                        f'command_del_product '
                        f'OK {message.from_user.id} message was removed earlier')
                except KeyError as err:
                    logger.error(
                        f'command_del_product message.bot.delete_message '
                        f'BAD {message.from_user.id} get {err.args}')

                try:
                    del data['order'][current_uid]
                    await message.answer('Товар видалено!')
                    logger.info(
                        f'command_del_product OK {message.from_user.id} removed product')

                except KeyError as err:
                    logger.error(
                        f'command_del_product del data '
                        f'BAD {message.from_user.id} get {err.args}')
        else:
            logger.warning(
                f'command_del_product '
                f'BAD {message.from_user.id} used the wrong command {message.text}')

            return await command_change_order(message, state)

        await command_change_order(message, state)
    except Exception as err:
        logger.error(
            f'command_del_product '
            f'BAD {message.from_user.id} get {err.args}')


async def cancel_add_new_quantity(message: types.Message, state: FSMContext):
    await command_change_order(message, state)


async def command_clear_order(message: types.Message, state: FSMContext):
    try:
        await message.answer('Кошик очищено.')
        logger.info(
            f'command_clear_order OK {message.from_user.id} emptied the basket')

        await state.finish()
        await start.command_menu(message, state=state)
    except Exception as err:
        logger.error(
            f'command_clear_order '
            f'BAD {message.from_user.id} get {err.args}')


async def command_back_to_view_order(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        try:
            await message.bot.delete_message(message.from_user.id, data['msg_change_order'])
        except MessageToDeleteNotFound:
            logger.warning(
                f'command_back_to_view_order '
                f'OK {message.from_user.id} message was removed earlier')
        except KeyError as err:
            logger.error(
                f'command_back_to_view_order message.bot.delete_message '
                f'BAD {message.from_user.id} get {err.args}')
        logger.info(
            f'command_back_to_view_order OK {message.from_user.id} back to view his order')

        await command_view_order(message, state)
    except Exception as err:
        logger.error(
            f'command_back_to_view_order '
            f'BAD {message.from_user.id} get {err.args}')


async def command_back_to_command_menu(message: types.Message, state: FSMContext):
    try:
        logger.info(
            f'command_back_to_command_menu OK {message.from_user.id} back to menu')

        await start.command_menu(message, state=state)
    except Exception as err:
        logger.error(
            f'command_back_to_command_menu '
            f'BAD {message.from_user.id} get {err.args}')


async def _get_current_uid_from_part(part_uid: int, state: FSMContext) -> str:
    try:
        async with state.proxy() as data:
            for uid in data['order'].keys():
                if part_uid in uid:
                    return uid
        return None
    except Exception as err:
        logger.error(
            f'_get_current_uid_from_part '
            f'BAD _ get {err.args}')


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
