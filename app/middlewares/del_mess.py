from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types


class DelMessage(BaseMiddleware):
    async def on_pre_process_update(self, update: types.Update, data: dict):
        await update.message.delete()
