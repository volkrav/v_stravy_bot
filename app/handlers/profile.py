from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from app.services import utils
from app.handlers import start
from app.misc.states import Start
from app.keyboards import reply
from app.misc.states import Profile

'''
- Змінити імя
- Змінити адресу
- Назад
'''


async def command_view_profile(message: types.Message, state: FSMContext):
    await Profile.view.set()
    if await utils.check_user_in_users(message.from_user.id):
        user: utils.User = await utils.get_user_data(message.from_user.id)
        answer = (f'<b>Ваша особиста інформація:\n\n</b>'
                  f'<b>Ім\'я:</b> {user.name}\n'
                  f'<b>Номер телефону:</b> {user.phone}\n'
                  f'<b>Адреса доставки:</b> {user.address}\n'
                  )
        markup = reply.kb_profile
    else:
        answer = (f'В цьому розділі буде зберігатися Ваша особиста інформація, '
                  f'яку я, з Вашого дозволу, запам\'ятаю при оформленні першого замовлення.\n'
                  f'Надалі особисту інформацію можна буде відредагувати або видалити.'
                  )
        markup = reply.kb_back
    await message.bot.send_message(chat_id=message.from_user.id,
                                   text=answer,
                                   reply_markup=markup)


async def command_back_to_main_menu(message: types.Message, state: FSMContext):
    await start.user_start(message, state)


def register_profile(dp: Dispatcher):
    dp.register_message_handler(command_view_profile,
                                Text(equals='😇 Особиста інформація',
                                     ignore_case=True),
                                state=[Start.free, None])
    dp.register_message_handler(command_back_to_main_menu,
                                Text(equals='↩️ Назад',
                                     ignore_case=True),
                                state=[Profile.view, None])
