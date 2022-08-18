from aiogram.dispatcher.filters import Command
from aiogram import types, Dispatcher


async def admin_start(message: types.Message):

    answer = 'Hello, admin!'
    await message.reply(text=answer)


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=['start'], state='*', is_admin=True)
