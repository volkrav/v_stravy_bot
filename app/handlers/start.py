from unicodedata import category
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import CommandStart, Text

from app.config import Config
from app.handlers.menu import list_categories
from app.keyboards import reply, inline

'''************************ КЛІЄНТСЬКА ЧАСТИНА ************************'''

'''************************ СТАРТОВЕ ВІКНО ************************'''


async def user_start(message: types.Message):
    try:
        bot = message.bot

        await bot.send_message(message.from_user.id,
                               f'Смачного\n\n'
                               f'Обирайте потрібне ⤵️',
                               reply_markup=reply.kb_start
                               )
    except:
        config: Config = bot.get('config')
        await message.answer(f'Спілкування з ботом через ПП, '
                             f'напишіть йому: \n{config.tg_bot.bot_url}',)


async def command_delivery(message: types.Message):
    await message.answer('Замовлення доставляємо по вівторках та п\'ятницях.\n\n' +
                         'Вартість доставки:\n' +
                         '🚚 Кур\'єром (Центр, Поділ, Дарницький​): 150грн.\n' +
                         '🚚 Кур\'єром (Київ​, інші райони): 180грн.\n\n' +
                         '<b>При замовленні від 800 грн - доставка (Київ) безкоштовно</b>\n'
                         )


async def command_location(message: types.Message):
    await message.answer('м. Київ, вул. Шовковичнa 13/2.\n'
                         'Гриль-бар "Мисливці"')


async def command_menu(message: types.Message):
    await message.bot.send_message(message.from_user.id,
                                   'Меню',
                                   reply_markup=reply.kb_catalog)
    await list_categories(message)


# async def command_show_item(call: types.CallbackQuery, callback_data: dict):
#     await list_products(call, callback_data['category'])


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, Text(equals=['start', 'замовити'],
                                                 ignore_case=True))
    dp.register_message_handler(user_start, CommandStart())
    dp.register_message_handler(command_delivery, Text(equals='🚚 Доставка і оплата',
                                                       ignore_case=True))
    dp.register_message_handler(command_location, Text(equals='Розташування',
                                                       ignore_case=True))
    dp.register_message_handler(command_menu, Text(equals='Меню',
                                                   ignore_case=True))
    # dp.register_callback_query_handler(
    #     command_show_item, inline.menu_cd.filter())
