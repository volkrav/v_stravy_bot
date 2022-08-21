from typing import Union
from aiogram import types, Dispatcher
from app.keyboards.inline import categories_keyboard, item_keyboard, menu_cd


async def list_categories(message: Union[types.Message, types.CallbackQuery], **kwargs):
    markup = await categories_keyboard()
    if isinstance(message, types.Message):
        await message.answer('Дивись, що у нас є', reply_markup=markup)

    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_reply_markup(markup)


async def show_item(message: types.CallbackQuery, category, **kwargs):
    markup = await item_keyboard(category)
    call = message

    await call.message.edit_reply_markup(markup)


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
