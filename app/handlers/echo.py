from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hcode


async def bot_echo(message: types.Message):
    answer = (
        f'Ехо без стану\n'
        f'Ваш id: {hcode(message.from_user.id)}'
        f'Ваше повідомлення:\n'
        f'{message.text}'
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
    dp.register_message_handler(bot_echo)
    dp.register_message_handler(bot_echo_all,
                                state='*',
                                content_types=types.ContentType.ANY)
