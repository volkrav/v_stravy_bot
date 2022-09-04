from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hcode
from app.services import utils
from .start import command_menu


async def command_view_order(message: types.Message, state: FSMContext):

    await utils.delete_inline_keyboard(message.bot, message.from_user.id)
    async with state.proxy() as data:
        if 'order' in data and data['order'].keys():
            current_order = data['order']
            answer = (
                f'Тут буде виведене ваше замовлення, яке можна буде:\n'
                f'- Оформити\n'
                f'- Редагувати\n'
                f'- Скасувати\n\n'
            )
            product_list = await utils.create_product_list(current_order.keys())
            amount_payable = 0
            for index, product in enumerate(product_list, 1):
                amount_payable += current_order[product.uid] * product.price
                answer += (f'# {index} \n'
                           f'{current_order[product.uid]} шт. * {product.title}\n'
                           f'Ціна: {product.price} грн.\n'
                           f'Всього: {current_order[product.uid] * product.price} грн.\n\n'
                           )
            answer += f'Сумма до сплати: {amount_payable} грн.'
            await message.reply(text=answer)
        else:
            answer = 'Кошик ще порожній, спершу оберіть товар'
            await message.reply(text=answer)
            await command_menu(message, state=state)
    # await command_menu(message)


def register_order(dp: Dispatcher):
    dp.register_message_handler(command_view_order, Text(equals='Ваше замовлення',
                                                         ignore_case=True), state='*')
