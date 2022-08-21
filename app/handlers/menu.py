from typing import Union
from aiogram import types
from app.keyboards.inline import categories_keyboard, items_keyboard


async def list_categories(message: Union[types.Message, types.CallbackQuery], **kwargs):
    markup = await categories_keyboard()
    if isinstance(message, types.Message):
        await message.answer('Дивись, що у нас є', reply_markup=markup)

    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_reply_markup(markup)
