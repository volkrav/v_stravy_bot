from typing import Union
from aiogram import types, Dispatcher
from app.keyboards.inline import categories_keyboard, products_keyboard, product_keyboard, menu_cd
from app.handlers import start
from app.keyboards import reply
from app.models import db_api

CURRENT_ID = {}


async def list_categories(message: Union[types.Message, types.CallbackQuery], **kwargs):

    markup = await categories_keyboard()
    if isinstance(message, types.Message):
        await message.answer('Дивись, що у нас є', reply_markup=markup)
        CURRENT_ID['chat_id'] = message.chat.id
        CURRENT_ID['message_id'] = message.message_id + 2
        print(f'list_categories (message) –> {message.message_id}')

    elif isinstance(message, types.CallbackQuery):

        call = message
        await call.message.edit_reply_markup(markup)
        print(f'list_categories (call) –> {call.message.message_id}')
        CURRENT_ID['chat_id'] = call.message.chat.id
        CURRENT_ID['message_id'] = call.message.message_id


async def list_products(message: types.CallbackQuery, category, **kwargs):
    markup = await products_keyboard(category)
    call = message

    await call.message.edit_reply_markup(markup)
    print(f'list_products (call) –> {call.message.message_id}')

    CURRENT_ID['chat_id'] = call.message.chat.id
    CURRENT_ID['message_id'] = call.message.message_id


async def show_product(message: types.CallbackQuery, category, product, **kwargs):

    current_product = await db_api.load_product(
        product,
        [
            'uid',
            'title',
            'url',
            'descr',
            'text',
            'price'
        ]
    )

    call = message

    markup = await product_keyboard(
        current_product['title'],
        current_product['uid'],
        current_product['price'],
        category
    )

    await call.bot.send_photo(
        call.from_user.id,
        current_product['url'],
        f"<b>{current_product['title']}</b>\n\n"
        f"{current_product['descr']}\n\n"
        f"{current_product['text']}",
        reply_markup=markup)
    await call.message.edit_reply_markup()
    print(f'show_product (call) –> {call.message.message_id}')
    CURRENT_ID['chat_id'] = call.message.chat.id
    CURRENT_ID['message_id'] = call.message.message_id + 1

    # await call.message.answer()


async def command_exit(message: types.Message):
    print(CURRENT_ID['chat_id'])
    print(CURRENT_ID['message_id'])

    # await message.delete_reply_markup()
    # await start.user_start(message)
    chat_id = CURRENT_ID['chat_id']
    message_id = CURRENT_ID['message_id']
    await message.bot.delete_message(chat_id=chat_id, message_id=message_id)
    await start.user_start(message)


async def del_markup(call: types.CallbackQuery, **kwargs):
    await call.message.edit_reply_markup()
    print(f'del_markup (call) –> {call.message.message_id}')


async def navigate(call: types.CallbackQuery, callback_data: dict):
    current_level = callback_data.get('level')
    category = callback_data.get('category')
    product = callback_data.get('product')

    levels = {
        '0': del_markup,
        '1': list_categories,
        '2': list_products,
        '3': show_product
    }

    current_level_function = levels.get(current_level)

    await current_level_function(call, category=category, product=product)


def register_menu(dp: Dispatcher):
    dp.register_callback_query_handler(navigate,
                                       menu_cd.filter())
    dp.register_message_handler(command_exit, text='back')

# ✖️ Вихід
