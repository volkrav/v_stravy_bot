from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hcode
from app.handlers import start
from app.services import utils


async def bot_echo(message: types.Message, state: FSMContext):
    answer = (
        f'Вітаю {message.from_user.first_name}\n\n'
        f'Це Vasylevsky Stravy бот, я допомагаю '
        f'оформлювати замовлення.\n'
        f'Схоже, я був на технічному обслуговуванні, тому пропоную розпочати з початку'
    )
    await utils.delete_inline_keyboard(message.bot, message.from_user.id)
    await message.answer(text=answer)
    await start.user_start(message, state)


async def bot_echo_all(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    answer = (
        f'Ехо в стані {hcode(state_name)}\n'
        f'Ваше повідомлення:\n'
        f'{message.text}'
    )
    await message.answer(text=answer)


def register_echo(dp: Dispatcher):
    dp.register_message_handler(bot_echo, state='*')
    # dp.register_message_handler(bot_echo_all,
    #                             state='*',
    #                             content_types=types.ContentType.ANY)
