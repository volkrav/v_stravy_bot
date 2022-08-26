from typing import Union
from aiogram import types, Dispatcher
from app.keyboards.inline import categories_keyboard, products_keyboard, menu_cd
from app.handlers import start
from app.keyboards import reply


async def list_categories(message: Union[types.Message, types.CallbackQuery], **kwargs):
    markup = await categories_keyboard()
    if isinstance(message, types.Message):
        await message.answer('Дивись, що у нас є', reply_markup=markup)

    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_reply_markup(markup)


async def show_item(message: types.CallbackQuery, category, **kwargs):
    markup = await products_keyboard(category)
    call = message

    await call.message.edit_reply_markup(markup)

# async def command_back(message: types.Message, mess_id):
#     # await message.delete_reply_markup()
#     # await start.user_start(message)

#     await message.bot.delete_message(chat_id=message.from_user.id, message_id=mess_id)


async def navigate(call: types.CallbackQuery, callback_data: dict):
    current_level = callback_data.get('level')
    category = callback_data.get('category')
    item = callback_data.get('item')

    levels = {
        '0': list_categories,
        '1': show_item
    }

    current_level_function = levels.get(current_level)

    await current_level_function(call, category=category, item=item)


def register_menu(dp: Dispatcher):
    dp.register_callback_query_handler(navigate,
                                       menu_cd.filter())
    # dp.register_message_handler(command_back, text='back')
