from aiogram import types


async def delete_inline_keyboard(message: types.Message, chat_id: int, msg_id: int):
    await message.bot.delete_message(chat_id=chat_id, message_id=msg_id)
