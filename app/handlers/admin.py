import logging

from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher

from app.services.parser import runparser
from app.handlers import start


logger = logging.getLogger(__name__)


async def admin_command_parser(message: types.Message, state: FSMContext):

    await message.answer('Вітаю, адміністраторе! Починаю парсинг...')
    try:
        logger.info(
            f'admin_command_parser OK {message.from_user.id} started parsing')
        runparser.main()
        await message.answer('Категорії та товари успішно оновилися.')
        await start.user_start(message, state)
        logger.info(
            f'admin_command_parser OK {message.from_user.id} successfully parsed')
    except Exception as err:
        logger.error(
            f'admin_command_parser BAD {message.from_user.id} get {err.args}')


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_command_parser,
                                commands=['parser'],
                                state='*',
                                is_admin=True)
