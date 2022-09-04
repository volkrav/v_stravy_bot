from aiogram import types, Bot
from aiogram.utils.exceptions import MessageToDeleteNotFound
from app.models import db_api


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


async def create_product_list(current_order: dict):
    pass
