import asyncio
import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from app.config import load_config
from app.filters.admin import AdminFilter
from app.handlers.admin import register_admin
from app.handlers.start import register_user
from app.handlers.menu import register_menu
from app.handlers.cart import register_cart
from app.handlers.order import register_order
from app.handlers.echo import register_echo
from app.middlewares.db import EnvironmentMiddleware
from app.middlewares.del_mess import DelMessage


logger = logging.getLogger(__name__)

# реєструємо міддлеварі, фільтри та хендлери, черговість виклику принципова


def register_all_middlewares(dp: Dispatcher, config):
    pass
    # dp.setup_middleware(EnvironmentMiddleware(config=config))
    # dp.setup_middleware(DelMessage())


def register_all_filters(dp: Dispatcher):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp: Dispatcher):
    register_admin(dp)
    register_user(dp)
    register_menu(dp)
    register_cart(dp)
    register_order(dp)
    register_echo(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    config = load_config('.env')

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    # storage = MemoryStorage()
    dp = Dispatcher(bot=bot, storage=storage)
    # для зручності використання config, щоб отримувати його не через
    # імпорт, а з об'єкту bot. Отримувати таким чином bot.get('config')
    bot['config'] = config
    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)

    try:
        await dp.skip_updates()
        await dp.start_polling(dp)
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error('Bot stopped!')
