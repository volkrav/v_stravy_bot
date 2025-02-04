import typing

from aiogram.dispatcher.filters import BoundFilter
from aiogram import types


from app.config import Config


class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin: typing.Optional[bool] = None):
        self.is_admin = is_admin

    async def check(self, obj: types.Message):
        if self.is_admin is None:
            return False
        config: Config = obj.bot.get('config')
        user_id = obj.from_user.id
        return (user_id in config.tg_bot.admin_ids) == self.is_admin
