from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hcode


async def bot_echo(message: types.Message):
    answer = (
        f'Вітаю {message.from_user.first_name}\n\n'
        f'Ваше повідомлення: -> '
        f'{message.text}\n'
        f'Обробка цієї команди в розробці'
    )
    await message.answer(text=answer)


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
