import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import CommandStart, Text
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound


from app.config import Config
from app.handlers import menu
from app.keyboards import inline, reply
from app.services import utils
from app.misc.states import Start


logger = logging.getLogger(__name__)

'''************************ КЛІЄНТСЬКА ЧАСТИНА ************************'''

'''************************ СТАРТОВЕ ВІКНО ************************'''


async def user_start(message: types.Message, state: FSMContext):
    try:
        logger.info(
            f'user_start OK {message.from_user.id} started work')

        current_state = await state.get_state()
        try:
            if await utils.check_user_in_users(message.from_user.id):
                user = await utils.get_user_data(message.from_user.id)
                name = user.name
            else:
                name = message.from_user.first_name
        except Exception as err:
            logger.error(
                f'user_start if check_user_in_users'
                f'BAD {message.from_user.id} get {err.args}')

        try:
            bot = message.bot
            answer = 'Обирайте потрібний розділ ⤵️'
            if current_state == None:
                answer = f'Вітаю, {name}.\n\n' + answer
            try:
                await utils.delete_inline_keyboard(bot, message.from_user.id)
                logger.info(
                    f'user_start OK {message.from_user.id} inline keyboard was removed')
            except MessageToDeleteNotFound:
                logger.warning(
                    f'user_start BAD {message.from_user.id} inline keyboard was removed earlier')
            except Exception as err:
                logger.error(
                    f'user_start utils.delete_inline_keyboard '
                    f'BAD {message.from_user.id} get {err.args}')

            await Start.free.set()

            await bot.send_message(chat_id=message.from_user.id,
                                   text=answer,
                                   reply_markup=reply.kb_start
                                   )
        except:
            config: Config = bot.get('config')
            await message.answer(f'Спілкування з ботом через ПП, '
                                 f'напишіть йому: \n{config.tg_bot.bot_url}',)
    except Exception as err:
        logger.error(
            f'user_start '
            f'BAD {message.from_user.id} get {err.args}')


async def command_menu(message: types.Message, state: FSMContext):
    try:
        logger.info(
            f'command_menu OK {message.from_user.id} looking at the menu')

        await Start.free.set()
        await message.bot.send_message(chat_id=message.from_user.id,
                                       text='Меню',
                                       reply_markup=reply.kb_catalog)
        await menu.list_categories(message, state)
    except Exception as err:
        logger.error(
            f'command_menu '
            f'BAD {message.from_user.id} get {err.args}')


async def command_about(message: types.Message):
    try:
        logger.info(
            f'command_about OK {message.from_user.id} looking at the about')

        await Start.free.set()
        with open('about.txt', 'r') as file:
            answer = file.read()
        await message.bot.send_message(chat_id=message.from_user.id,
                                       text=answer)
    except Exception as err:
        logger.error(
            f'command_about'
            f'BAD {message.from_user.id} get {err.args}')


async def command_contacts(message: types.Message, state: FSMContext):
    try:
        logger.info(
            f'command_contacts OK {message.from_user.id} looking at the contacts')

        current_state = await state.get_state()
        if current_state == None:
            await Start.free.set()
        await message.bot.send_message(chat_id=message.from_user.id,
                                       text='<b>ГРИЛЬ-БАР "МИСЛИВЦІ"</b>\n\n' +
                                       '🗺 Адреса: м. Київ, вул. Шовковична 13/2\n' +
                                       '📞 Телефон: +38 (063) 014-20-60\n' +
                                       '✉️ E-mail: barohotnikk@ukr.net\n',
                                       reply_markup=inline.kb_about)
    except Exception as err:
        logger.error(
            f'command_contacts'
            f'BAD {message.from_user.id} get {err.args}')


async def command_delivery(message: types.Message, state: FSMContext):
    try:
        logger.info(
            f'command_delivery OK {message.from_user.id} looking at the delivery')

        current_state = await state.get_state()
        if current_state == None:
            await Start.free.set()
        await message.bot.send_message(chat_id=message.from_user.id,
                                       text='Замовлення доставляємо по вівторках та п\'ятницях.\n\n' +
                                       'Вартість доставки:\n' +
                                       '🚚 Кур\'єром (Центр, Поділ, Дарницький​): 150грн.\n' +
                                       '🚚 Кур\'єром (Київ​, інші райони): 180грн.\n\n' +
                                       '<b>При замовленні від 800 грн - доставка (Київ) безкоштовно</b>\n'
                                       )
    except Exception as err:
        logger.error(
            f'command_delivery'
            f'BAD {message.from_user.id} get {err.args}')


async def command_location(message: types.Message, state: FSMContext):
    try:
        logger.info(
            f'command_location OK {message.from_user.id} looking at the location')

        current_state = await state.get_state()
        if current_state == None:
            await Start.free.set()
        await message.bot.send_message(chat_id=message.from_user.id,
                                       text='Самостійно забрати замовлення можна за адресою:\n\n'
                                       'м. Київ, вул. Шовковичнa 13/2.\n'
                                       'Гриль-бар "Мисливці"\n\n'
                                       '<b>Знижка при самовивозі -10%</b>')
    except Exception as err:
        logger.error(
            f'command_location'
            f'BAD {message.from_user.id} get {err.args}')


async def unsupported_command(message: types.Message):
    try:
        try:
            await utils.delete_inline_keyboard(message.bot, message.from_user.id)
            logger.info(
                f'unsupported_command OK {message.from_user.id} inline keyboard was removed')
        except MessageToDeleteNotFound:
            logger.warning(
                f'unsupported_command BAD {message.from_user.id} inline keyboard was removed earlier')
        except Exception as err:
            logger.error(
                f'unsupported_command utils.delete_inline_keyboard '
                f'BAD {message.from_user.id} get {err.args}')
        logger.warning(
            f'unsupported_command BAD {message.from_user.id} unsupported command {message.text}')
        await message.bot.send_message(chat_id=message.from_user.id,
                                       text='Вибачте, я не розумію цю команду.\n' +
                                       'Використовуйте, будь ласка, клавіатуру ⌨️⤵️',
                                       reply_markup=reply.kb_start)
    except Exception as err:
        logger.error(
            f'unsupported_command '
            f'BAD {message.from_user.id} get {err.args}')


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, Text(equals=['start', 'замовити'],
                                                 ignore_case=True), state='*')
    dp.register_message_handler(user_start, CommandStart(), state='*')
    dp.register_message_handler(command_menu,
                                Text(equals='Меню',
                                     ignore_case=True),
                                state=[Start.free, None])
    dp.register_message_handler(command_about,
                                Text(equals='ℹ️ Про нас',
                                     ignore_case=True),
                                state=[Start.free, None]
                                )
    dp.register_message_handler(command_contacts,
                                Text(equals='📞 Контакти',
                                     ignore_case=True),
                                state=[Start.free, None])
    dp.register_message_handler(command_delivery,
                                Text(equals='🚚 Доставка і оплата',
                                     ignore_case=True),
                                state=[Start.free, None])
    dp.register_message_handler(command_location,
                                Text(equals='💪 Самовивіз',
                                     ignore_case=True),
                                state=[Start.free, None])
    dp.register_message_handler(unsupported_command,
                                state=[Start.free])
