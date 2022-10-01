import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hcode
from app.handlers import start
from app.services import utils
from aiogram.utils.exceptions import MessageToDeleteNotFound


logger = logging.getLogger(__name__)


async def bot_echo(message: types.Message, state: FSMContext):
    try:
        logger.info(
            f'bot_echo OK {message.from_user.id} unsupported command {message.text}')

        answer = (
            f'Вітаю {message.from_user.first_name}\n\n'
            f'Це Vasylevsky Stravy бот, я допомагаю '
            f'оформлювати замовлення.\n'
            f'Ви ввели команду, яку я не розумію.\n\n<b>Використайте, будь-ласка, <u>клавіатуру</u> '
            f'або перезавантажте бота командою /start</b>'
        )
        try:
            await utils.delete_inline_keyboard(message.bot, message.from_user.id)
            logger.info(
                f'bot_echo OK {message.from_user.id} inline keyboard was removed')
        except MessageToDeleteNotFound:
            logger.info(
                f'bot_echo OK {message.from_user.id} inline keyboard was removed earlier')
        except Exception as err:
            logger.error(
                f'bot_echo utils.delete_inline_keyboard '
                f'BAD {message.from_user.id} get {err.args}')

        await message.answer(text=answer)
    except Exception as err:
        logger.error(
            f'bot_echo '
            f'BAD {message.from_user.id} get {err.args}')


def register_echo(dp: Dispatcher):
    dp.register_message_handler(bot_echo, state='*')
