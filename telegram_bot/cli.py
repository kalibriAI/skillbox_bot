import asyncio
import logging
from colorama import Fore, init
import asyncpg

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import load_config
from filter.chat import ChatTypeFilter
from handler import admin, info, user
from service.bfuncs import set_commands, notify_admins

from middleware.db import DatabaseMiddleware

init(autoreset=True)
logger = logging.getLogger(__name__)
config = load_config("bot.ini")


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    print(Fore.GREEN + 'STATUS:', Fore.BLUE + "Starting bot")

    storage = MemoryStorage()

    pool = await asyncpg.create_pool(
        user=config.db.user,
        password=config.db.password,
        database=config.db.database,
        host=config.db.host
    )

    # proxy_url = "http://proxy.server:3128"
    bot = Bot(token=config.tg_bot.token, parse_mode='html')
    dp = Dispatcher(storage=storage)

    dp.include_router(info.info_router)
    dp.include_router(admin.admin_router)
    dp.include_router(user.user_router)

    dp.update.middleware(DatabaseMiddleware(pool))
    user.user_router.message.filter(ChatTypeFilter())

    await set_commands(bot, config.tg_bot.admin_id)

    try:
        await notify_admins(config.tg_bot.admin_id, bot)
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await pool.close()
        await bot.session.close()


def cli():
    """Wrapper for command line"""
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")


if __name__ == '__main__':
    cli()
