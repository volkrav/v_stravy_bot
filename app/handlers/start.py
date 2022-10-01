import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import CommandStart, Text
from aiogram.dispatcher import FSMContext


from app.config import Config
from app.handlers import menu
from app.keyboards import inline, reply
from app.services import utils
from app.misc.states import Profile, Start


logger = logging.getLogger(__name__)

'''************************ КЛІЄНТСЬКА ЧАСТИНА ************************'''

'''************************ СТАРТОВЕ ВІКНО ************************'''


async def user_start(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if await utils.check_user_in_users(message.from_user.id):
        user = await utils.get_user_data(message.from_user.id)
        name = user.name
    else:
        name = message.from_user.first_name

    try:
        bot = message.bot
        answer = 'Обирайте потрібний розділ ⤵️'
        if current_state == None:
            answer = f'Вітаю, {name}.\n\n' + answer
        await utils.delete_inline_keyboard(bot, message.from_user.id)
        await Start.free.set()

        await bot.send_message(chat_id=message.from_user.id,
                               text=answer,
                               reply_markup=reply.kb_start
                               )
    except:
        config: Config = bot.get('config')
        await message.answer(f'Спілкування з ботом через ПП, '
                             f'напишіть йому: \n{config.tg_bot.bot_url}',)


async def command_menu(message: types.Message, state: FSMContext):
    await Start.free.set()
    await message.bot.send_message(chat_id=message.from_user.id,
                                   text='Меню',
                                   reply_markup=reply.kb_catalog)
    await menu.list_categories(message, state)


async def command_about(message: types.Message):
    await Start.free.set()

    with open('about.txt', 'r') as file:
        answer = file.read()
    await message.bot.send_message(chat_id=message.from_user.id,
                                   text=answer)


async def command_contacts(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == None:
        await Start.free.set()
    await message.bot.send_message(chat_id=message.from_user.id,
                                   text='<b>ГРИЛЬ-БАР "МИСЛИВЦІ"</b>\n\n' +
                                   '🗺 Адреса: м. Київ, вул. Шовковична 13/2\n' +
                                   '📞 Телефон: +38 (063) 014-20-60\n' +
                                   '✉️ E-mail: barohotnikk@ukr.net\n',
                                   reply_markup=inline.kb_about)


async def command_delivery(message: types.Message, state: FSMContext):
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


async def command_location(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == None:
        await Start.free.set()
    await message.bot.send_message(chat_id=message.from_user.id,
                                   text='Самостійно забрати замовлення можна за адресою:\n\n'
                                   'м. Київ, вул. Шовковичнa 13/2.\n'
                                   'Гриль-бар "Мисливці"\n\n'
                                   '<b>Знижка при самовивозі -10%</b>')


async def unsupported_command(message: types.Message):
    try:
        await utils.delete_inline_keyboard(message.bot, message.from_user.id)
    except Exception as err:
        logger.error(
            f'unsupported_command BAD {message.from_user.id} get {err.args}')
    logger.error(
        f'unsupported_command BAD {message.from_user.id} unsupported command {message.text}')
    await message.bot.send_message(chat_id=message.from_user.id,
                                   text='Вибачте, я не розумію цю команду.\n' +
                                   'Використовуйте, будь ласка, клавіатуру ⌨️⤵️',
                                   reply_markup=reply.kb_start)


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
