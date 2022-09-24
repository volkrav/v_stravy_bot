from typing import NamedTuple

from aiogram import Bot, types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound
from app.models import db_api


class Product(NamedTuple):
    uid: str
    title: str
    price: int
    descr: str
    text: str
    img: str
    quantity: str
    gallery: str
    url: str
    partuids: str


class Order(NamedTuple):
    pickup: bool
    name: str
    phone: str
    address: str


class ViewOrder(NamedTuple):
    text: str
    amount: int


async def delete_inline_keyboard(bot: Bot, user_id: int) -> None:
    current_messages_for_del = await db_api.select_where_and('menu_keybords',
                                                             [
                                                                 'user_id',
                                                                 'chat_id',
                                                                 'message_id'
                                                             ],
                                                             {
                                                                 'user_id': user_id
                                                             })

    await db_api.delete_from_where('menu_keybords', {'user_id': user_id})

    for current_message in current_messages_for_del:
        try:
            await bot.delete_message(
                chat_id=current_message['chat_id'],
                message_id=current_message['message_id']
            )
        except MessageToDeleteNotFound:
            print(
                f'Повідомлення {current_message["message_id"]} вже було видалено')


async def write_id_for_del_msg(user_id: int, chat_id: int, message_id: int) -> None:
    """Збереження в БД даних повідомлення для його подальшого видалення"""
    await db_api.insert('menu_keybords', {
        'user_id': user_id,
        'chat_id': chat_id,
        'message_id': message_id
    })


async def create_product_list(current_order_uid: list) -> list[Product]:
    product_list = []
    for uid in current_order_uid:
        product_list.append(
            await create_product(uid)
        )
    return product_list


async def create_product(uid: str) -> Product:
    data_product = await db_api.load_product(uid, ['uid',
                                                   'title',
                                                   'price',
                                                   'descr',
                                                   'text',
                                                   'img',
                                                   'quantity',
                                                   'gallery',
                                                   'url',
                                                   'partuids'
                                                   ])
    return Product(
        uid=data_product['uid'],
        title=data_product['title'],
        price=data_product['price'],
        descr=data_product['descr'],
        text=data_product['text'],
        img=data_product['img'],
        quantity=data_product['quantity'],
        gallery=data_product['gallery'],
        url=data_product['url'],
        partuids=data_product['partuids']
    )


async def create_order(order_details: dict) -> Order:
    if order_details['pickup']:
        _address = 'Самовивіз. Знижка -10%'
    else:
        _address = order_details['address']
    return Order(
        pickup=order_details['pickup'],
        name=order_details['name'],
        phone=order_details['phone'],
        address=_address
    )


async def write_user_to_users(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    order_data = state_data.get('ordering', '')
    user_id = message.from_user.id
    name = order_data.get('name', '')
    pickup = order_data.get('pickup', '')
    if pickup:
        address = 'Самовивіз'
    else:
        address = order_data.get('address', '')
    phone = order_data.get('phone', '')
    if '+' not in phone:
        phone = '+' + phone
    if await check_user_in_users(message.from_user.id):
        await message.answer('check_user_in_users worked')
    await message.answer(f'{user_id=}\n{name=}\n{pickup=}\n{address=}\n{phone=}')


async def check_user_in_users(user_id: int) -> bool:
    users = await db_api.select_where_and('users', ['id'], {'id': user_id})
    return users or False
