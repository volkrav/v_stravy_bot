import logging


from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
import aiogram.utils.markdown as fmt


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
logger = logging.getLogger(__name__)


async def command_view_profile(message: types.Message, state: FSMContext):
    await Profile.view.set()
    if await utils.check_user_in_users(message.from_user.id):
        await Profile.change_data.set()
        user: utils.User = await utils.get_user_data(message.from_user.id)
        answer = (f'<b>Ваша контактна інформація:\n\n</b>'
                  f'<b>• Ім\'я:</b> {user.name}\n'
                  f'<b>• Номер телефону:</b> {await utils.format_phone_number(user.phone)}\n'
                  f'<b>• Адреса доставки:</b> {user.address}\n'
                  )
        markup = reply.kb_profile
    else:
        answer = (f'В цьому розділі буде зберігатися Ваша контактна інформація, '
                  f'яку я, з Вашого дозволу, запам\'ятаю при оформленні першого замовлення.\n'
                  f'Надалі особисту інформацію можна буде відредагувати або видалити.'
                  )
        markup = reply.kb_back
    await message.bot.send_message(chat_id=message.from_user.id,
                                   text=answer,
                                   reply_markup=markup)


async def command_back_to_main_menu(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if (current_state == 'Profile:change_name' or
            current_state == 'Profile:change_address'):
        return await command_view_profile(message, state)
    await start.user_start(message, state)


async def command_change_data(message: types.Message, state: FSMContext):
    if message.text == '✏️ Змінити ім\'я':
        await Profile.change_name.set()
        await message.answer(text='Введіть, будь ласка, нове ім\'я: ⌨️⤵️',
                             reply_markup=reply.kb_back)
    elif message.text == '✏️ Змінити адресу':
        await message.answer(text='Введіть, будь ласка, нову адресу: ⌨️⤵️',
                             reply_markup=reply.kb_back)
        await Profile.change_address.set()


async def command_change_name(message: types.Message, state: FSMContext):
    try:
        await utils.change_user_name(message.from_user.id, fmt.quote_html(message.text))
        logger.info(
            f'command_change_name OK {message.from_user.id} change name as {fmt.quote_html(message.text)}')
        await command_view_profile(message, state)
    except Exception as err:
        logger.error(
            f'command_change_name BAD {message.from_user.id} get {err.args}')


async def command_change_address(message: types.Message, state: FSMContext):
    try:
        await utils.change_user_address(message.from_user.id, fmt.quote_html(message.text))
        logger.info(
            f'command_change_address OK {message.from_user.id} change address as {fmt.quote_html(message.text)}')
        await command_view_profile(message, state)
    except Exception as err:
        logger.error(
            f'command_change_name BAD {message.from_user.id} get {err.args}')


async def command_del_data(message: types.Message, state: FSMContext):
    try:
        await utils.del_user_data(message.from_user.id)
        await message.answer('👍 Ваші контактні дані успішно видалені.')
        logger.info(
            f'command_del_data OK {message.from_user.id} deleted data successfully')
        await start.user_start(message, state)
    except Exception as err:
        await message.answer('☹️ Щось пішло не так. Зафіксував помилку для розробника.')
        logger.error(
            f'command_del_data BAD {message.from_user.id} get {err.args}')
        await start.user_start(message, state)


def register_profile(dp: Dispatcher):
    dp.register_message_handler(command_view_profile,
                                Text(equals='😇 Особиста інформація',
                                     ignore_case=True),
                                state=[Start.free, None])
    dp.register_message_handler(command_back_to_main_menu,
                                Text(equals='↩️ Назад',
                                     ignore_case=True),
                                state='*')
    dp.register_message_handler(command_change_data,
                                Text(startswith='✏️ Змінити',
                                     ignore_case=True),
                                state=[Profile.change_data, None])
    dp.register_message_handler(command_change_name,
                                state=Profile.change_name)
    dp.register_message_handler(command_change_address,
                                state=Profile.change_address)
    dp.register_message_handler(command_del_data,
                                Text(equals='❌ Видалити усі дані',
                                     ignore_case=True),
                                state=[Profile.change_data, None])
