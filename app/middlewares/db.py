from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware


# class DbMiddleware(LifetimeControllerMiddleware):
#     skip_patterns = ['error', 'update']

#     async def pre_process(self, obj, data, *args):
#         db_session = obj.bot.get('db')






class EnvironmentMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs

    async def pre_process(self, obj, data, *args):
        data.update(**self.kwargs)
