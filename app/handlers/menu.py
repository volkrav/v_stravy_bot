import logging

from typing import Union
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound


from aiogram.dispatcher.filters import Text
from app.keyboards.inline import categories_keyboard, products_keyboard, product_keyboard, menu_cd
from app.handlers import start
from app.keyboards import reply
from app.models import db_api
from app.services import utils


logger = logging.getLogger(__name__)

'''************************ КЛІЄНТСЬКА ЧАСТИНА ************************'''

'''************************ СПИСОК КАТЕГОРІЙ ************************'''


async def list_categories(message: Union[types.Message, types.CallbackQuery], state: FSMContext, **kwargs):

    try:
        markup = await categories_keyboard()
        if isinstance(message, types.Message):
            msg = await message.answer('Дивись, що у нас є', reply_markup=markup)
            logger.info(
                f'list_categories OK {message.from_user.id} view the list of categories')
            try:
                await utils.write_id_for_del_msg(message.from_user.id,
                                                 message.chat.id,
                                                 msg['message_id']
                                                 )
            except Exception as err:
                logger.error(
                    f'list_categories utils.write_id_for_del_msg '
                    f'BAD {message.from_user.id} get {err.args}')

        elif isinstance(message, types.CallbackQuery):

            call = message
            logger.info(
                f'list_categories OK {call.from_user.id} view the list of categories')

            await call.message.edit_reply_markup(markup)
            # await utils.write_id_for_del_msg(message.from_user.id,
            #                                  message.chat.id,
            #                                  msg['message_id']
            #                                  )
    except Exception as err:
        logger.error(
            f'list_categories '
            f'BAD {message.from_user.id} get {err.args}')


'''************************ СПИСОК ТОВАРІВ ************************'''


async def list_products(message: Union[types.Message, types.CallbackQuery], category, state: FSMContext, **kwargs):
    try:

        markup = await products_keyboard(category)
        if isinstance(message, types.Message):
            logger.info(
                f'list_products OK {message.from_user.id} view the list of products')

            msg = await message.answer(text='Вибираємо далі ⤵️', reply_markup=markup)
            try:
                await utils.write_id_for_del_msg(message.from_user.id,
                                                 message.chat.id,
                                                 msg['message_id']
                                                 )
            except Exception as err:
                logger.error(
                    f'list_products utils.write_id_for_del_msg '
                    f'BAD {message.from_user.id} get {err.args}')
        elif isinstance(message, types.CallbackQuery):
            call = message
            logger.info(
                f'list_products OK {call.from_user.id} view the list of products')

            await call.message.edit_reply_markup(markup)
    except Exception as err:
        logger.error(
            f'list_products '
            f'BAD {message.from_user.id} get {err.args}')


'''************************ ПЕРЕГЛЯД ТОВАРУ ************************'''


async def show_product(message: types.CallbackQuery, category, product, state: FSMContext, **kwargs):
    try:
        current_product = await db_api.load_product(
            product,
            [
                'uid',
                'title',
                'gallery',
                'descr',
                'text',
                'price'
            ])

        call = message
        async with state.proxy() as data:
            data['current_title'] = current_product['title']
        markup = await product_keyboard(
            current_product['title'],
            current_product['uid'],
            current_product['price'],
            category
        )
        album = types.MediaGroup()
        for img in current_product['gallery'].split(','):
            album.attach_photo(img)
        await call.message.answer_media_group(album)
        msg_photo = await call.bot.send_message(
            call.from_user.id,
            f"<b>{current_product['title']}.</b>\n\n"
            f"Ціна: {current_product['price']} грн.\n\n"
            f"{current_product['descr']}\n\n"
            f"{current_product['text']}\n"
            f"Додайте обраний товар до кошика ⤵️",
            reply_markup=markup)
        logger.info(
            f'show_product OK {message.from_user.id} view the {current_product["title"]}')

        await call.message.edit_reply_markup()
        try:
            await utils.write_id_for_del_msg(call.from_user.id,
                                             call.message.chat.id,
                                             msg_photo['message_id']
                                             )
        except Exception as err:
            logger.error(
                f'show_product utils.write_id_for_del_msg '
                f'BAD {message.from_user.id} get {err.args}')

    except Exception as err:
        logger.error(
            f'show_product '
            f'BAD {message.from_user.id} get {err.args}')


async def command_exit(message: types.Message, state: FSMContext):
    try:
        try:
            await utils.delete_inline_keyboard(message.bot, message.from_user.id)
            logger.info(
                f'command_exit OK {message.from_user.id} inline keyboard was removed')
        except MessageToDeleteNotFound:
            logger.warning(
                f'command_exit BAD {message.from_user.id} inline keyboard was removed earlier')
        except Exception as err:
            logger.error(
                f'command_exit utils.delete_inline_keyboard '
                f'BAD {message.from_user.id} get {err.args}')
        finally:
            await start.user_start(message, state)
    except Exception as err:
        logger.error(
            f'command_exit '
            f'BAD {message.from_user.id} get {err.args}')


async def navigate(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    try:
        current_level = callback_data.get('level')
        category = callback_data.get('category')
        product = callback_data.get('product')

        levels = {
            '0': list_categories,
            '1': list_products,
            '2': show_product
        }

        current_level_function = levels.get(current_level)

        await current_level_function(call, state=state, category=category, product=product)
    except Exception as err:
        logger.error(
            f'navigate '
            f'BAD {call.from_user.id} get {err.args}')


def register_menu(dp: Dispatcher):
    dp.register_callback_query_handler(navigate,
                                       menu_cd.filter(),
                                       state='*')
    dp.register_message_handler(command_exit,
                                Text(equals='❌ Вихід', ignore_case=True),
                                state='*')

# ✖️ Вихід
