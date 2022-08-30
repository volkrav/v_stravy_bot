from aiogram import types
from aiogram.utils.exceptions import MessageToDeleteNotFound


async def delete_inline_keyboard(message: types.Message, current_ids: dict):

    try:
        await message.bot.delete_message(
            chat_id=current_ids['chat_id'],
            message_id=current_ids['message_id']
        )
    except MessageToDeleteNotFound:
        print('Нема повідомлень для видалення')
        
