from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hcode
from app.services.utils import delete_inline_keyboard


async def command_view_order(message: types.Message):

    await delete_inline_keyboard(message.bot, message.from_user.id)

    answer = (
        f'Тут буде виведене ваше замовлення, яке можна буде:\n'
        f'- Оформити\n'
        f'- Редагувати\n'
        f'- Скасувати'
    )
    await message.reply(text=answer)


def register_order(dp: Dispatcher):
    dp.register_message_handler(command_view_order, Text(equals='Ваше замовлення',
                                                         ignore_case=True), state='*')
