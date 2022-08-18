# from aiogram.utils import executor
# from loader import dp
# from handlers import client, admin, other
# from data_base import sqlite_db


# async def on_startup(_):
#     print('Bot is online')
#     # sqlite_db.sql_start()
#     import filters
#     filters.setup(dp)


# client.register_handles_client(dp)
# admin.register_handles_admin(dp)
# other.register_handles_other(dp)

# if __name__ == '__main__':
#     executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
