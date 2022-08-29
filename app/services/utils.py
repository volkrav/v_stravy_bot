from aiogram import types


async def delete_inline_keyboard(message: types.Message, current_ids: dict):

    for current_id in current_ids:
        await message.bot.delete_message(
            chat_id=current_id['chat_id'],
            message_id=current_id['message_id']
        )
