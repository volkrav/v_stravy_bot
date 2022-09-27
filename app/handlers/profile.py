from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from app.services import utils
from app.misc.states import Start


'''
- Змінити імя
- Змінити адресу
- Назад
'''


async def command_view_profile(message: types.Message, state: FSMContext):
    if await utils.check_user_in_users(message.from_user.id):
        user: utils.User = await utils.get_user_data(message.from_user.id)
        answer = (f'<b>Ваша особиста інформація:\n\n</b>'
                  f'<b>Ім\'я:</b> {user.name}\n'
                  f'<b>Номер телефону:</b> {user.phone}\n'
                  f'<b>Адреса доставки:</b> {user.address}\n'
                  )

    else:
        answer = (f'В цьому розділі буде зберігатися Ваша особиста інформація, '
                  f'яку я, з Вашого дозволу, запам\'ятаю при оформленні першого замовлення.\n'
                  f'Надалі особисту інформацію можна буде відредагувати або видалити.'
                  )
    await message.bot.send_message(chat_id=message.from_user.id,
                                   text=answer)


def register_profile(dp: Dispatcher):
    dp.register_message_handler(command_view_profile,
                                Text(equals='😇 Особиста інформація',
                                     ignore_case=True),
                                state=[Start.free, None])
