from aiogram import types


async def delete_inline_keyboard(message: types.Message, current_ids: dict):

    await message.bot.delete_message(
        chat_id=current_ids['chat_id'],
        message_id=current_ids['message_id']
    )
