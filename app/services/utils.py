from aiogram import types, Bot
from aiogram.utils.exceptions import MessageToDeleteNotFound
from typing import NamedTuple
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
        uid = data_product['uid'],
        title = data_product['title'],
        price = data_product['price'],
        descr = data_product['descr'],
        text = data_product['text'],
        img = data_product['img'],
        quantity = data_product['quantity'],
        gallery = data_product['gallery'],
        url = data_product['url'],
        partuids = data_product['partuids']
    )
