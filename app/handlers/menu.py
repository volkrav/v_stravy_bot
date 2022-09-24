from typing import Union
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from aiogram.dispatcher.filters import Text
from app.keyboards.inline import categories_keyboard, products_keyboard, product_keyboard, menu_cd
from app.handlers import start
from app.keyboards import reply
from app.models import db_api
from app.services import utils


async def list_categories(message: Union[types.Message, types.CallbackQuery], state: FSMContext, **kwargs):

    markup = await categories_keyboard()
    if isinstance(message, types.Message):
        msg = await message.answer('Дивись, що у нас є', reply_markup=markup)
        await utils.write_id_for_del_msg(message.from_user.id,
                                         message.chat.id,
                                         msg['message_id']
                                         )

    elif isinstance(message, types.CallbackQuery):

        call = message
        await call.message.edit_reply_markup(markup)
        # await utils.write_id_for_del_msg(message.from_user.id,
        #                                  message.chat.id,
        #                                  msg['message_id']
        #                                  )


async def list_products(message: Union[types.Message, types.CallbackQuery], category, state: FSMContext, **kwargs):
    markup = await products_keyboard(category)
    if isinstance(message, types.Message):
        msg = await message.answer(text='Вибираємо далі ⤵️', reply_markup=markup)
        await utils.write_id_for_del_msg(message.from_user.id,
                                         message.chat.id,
                                         msg['message_id']
                                         )

    elif isinstance(message, types.CallbackQuery):
        call = message

        await call.message.edit_reply_markup(markup)


async def show_product(message: types.CallbackQuery, category, product, state: FSMContext, **kwargs):

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
    await call.message.edit_reply_markup()

    await utils.write_id_for_del_msg(call.from_user.id,
                                     call.message.chat.id,
                                     msg_photo['message_id']
                                     )


async def command_exit(message: types.Message, state: FSMContext):
    await utils.delete_inline_keyboard(message.bot, message.from_user.id)
    await start.user_start(message, state)


async def navigate(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
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


def register_menu(dp: Dispatcher):
    dp.register_callback_query_handler(navigate,
                                       menu_cd.filter(),
                                       state='*')
    dp.register_message_handler(command_exit,
                                Text(equals='❌ Вихід', ignore_case=True),
                                state='*')

# ✖️ Вихід
