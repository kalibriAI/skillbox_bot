import asyncio
import logging
from colorama import Fore, init
import asyncpg

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import load_config
from filter.chat import ChatTypeFilter
from handler import admin, user, registration, history
from service.bfuncs import set_commands, notify_admins
from middleware.db import DatabaseMiddleware
from filter.check_user import UserExists

init(autoreset=True)
logger = logging.getLogger(__name__)
config = load_config("bot.ini.template")


async def main():
    """
    Основная функция запуска бота.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )  # настройка логера
    print(Fore.GREEN + 'STATUS:', Fore.BLUE + "Starting bot")

    storage = MemoryStorage()  # установка хранилища состояний

    pool = await asyncpg.create_pool(
        user=config.db.user,
        password=config.db.password,
        database=config.db.database,
        host=config.db.host
    )  # создание пула базы данных

    # proxy_url = "http://proxy.server:3128" - прокси для pythonanywhere
    bot = Bot(token=config.tg_bot.token, parse_mode='html')  # инициализация бота (передается токен и парсмод)
    dp = Dispatcher(storage=storage)  # инициалтзация диспетчера (передается хранилище)

    # подключение роутеров к диспетчеру
    dp.include_router(admin.admin_router)
    dp.include_router(registration.reg_router)
    dp.include_router(user.user_router)
    dp.include_router(history.hist_router)

    # подключение фильтров и мидлварей
    dp.update.middleware(DatabaseMiddleware(pool))
    user.user_router.message.filter(ChatTypeFilter())
    user.user_router.message.filter(UserExists(pool))

    # установка команд бота
    await set_commands(bot, config.tg_bot.admin_id)

    try:
        await notify_admins(config.tg_bot.admin_id, bot)  # уведомление админа о запуске
        await dp.start_polling(bot)  # запуск бота
    finally:
        await dp.storage.close()  # закрытие хранилища
        await pool.close()  # закрытие пула
        await bot.session.close()  # закрытие сессии бота


def cli():
    """Wrapper for command line"""
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")


# точка входа
if __name__ == '__main__':
    cli()
