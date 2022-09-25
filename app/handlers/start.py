from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import CommandStart, Text
from aiogram.dispatcher import FSMContext


from app.config import Config
from app.handlers import menu
from app.keyboards import reply
from app.services import utils


'''************************ КЛІЄНТСЬКА ЧАСТИНА ************************'''

'''************************ СТАРТОВЕ ВІКНО ************************'''


async def user_start(message: types.Message, state: FSMContext):

    if await utils.check_user_in_users(message.from_user.id):
        user = await utils.get_user_data(message.from_user.id)
        name = user.name
    else:
        name = message.from_user.first_name

    try:
        bot = message.bot

        await utils.delete_inline_keyboard(bot, message.from_user.id)

        await bot.send_message(message.from_user.id,
                               f'Вітаю, {name}\n\n'
                               f'Обирайте потрібний розділ ⤵️',
                               reply_markup=reply.kb_start
                               )
    except:
        config: Config = bot.get('config')
        await message.answer(f'Спілкування з ботом через ПП, '
                             f'напишіть йому: \n{config.tg_bot.bot_url}',)


async def command_delivery(message: types.Message, state: FSMContext):
    await message.answer('Замовлення доставляємо по вівторках та п\'ятницях.\n\n' +
                         'Вартість доставки:\n' +
                         '🚚 Кур\'єром (Центр, Поділ, Дарницький​): 150грн.\n' +
                         '🚚 Кур\'єром (Київ​, інші райони): 180грн.\n\n' +
                         '<b>При замовленні від 800 грн - доставка (Київ) безкоштовно</b>\n'
                         )


async def command_location(message: types.Message, state: FSMContext):
    await message.answer('Самостійно забрати замовлення можна за адресою:\n\n'
                         'м. Київ, вул. Шовковичнa 13/2.\n'
                         'Гриль-бар "Мисливці"\n\n'
                         '<b>Знижка при самовивозі -10%</b>')


async def command_about(message: types.Message, state: FSMContext):
    file = open('about.txt', 'r')
    answer = file.read()
    await message.answer(answer)


async def command_menu(message: types.Message, state: FSMContext):
    await message.bot.send_message(message.from_user.id,
                                   'Меню',
                                   reply_markup=reply.kb_catalog)
    await menu.list_categories(message, state)


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, Text(equals=['start', 'замовити'],
                                                 ignore_case=True), state='*')
    dp.register_message_handler(user_start, CommandStart(), state='*')
    dp.register_message_handler(command_menu, Text(equals='Меню',
                                                   ignore_case=True), state='*')
    dp.register_message_handler(command_delivery, Text(equals='🚚 Доставка і оплата',
                                                       ignore_case=True), state='*')
    dp.register_message_handler(command_location, Text(equals='💪 Самовивіз',
                                                       ignore_case=True), state='*')
    dp.register_message_handler(command_about, Text(equals='ℹ️ Про нас',
                                                    ignore_case=True), state='*')
