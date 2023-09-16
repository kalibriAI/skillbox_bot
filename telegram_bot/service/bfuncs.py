import json

from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from aiogram import Bot
from datetime import date
from asyncpg import Pool

from model.errors import HotelAlredyRememdered
from model.types import HotelInfo


async def set_user_commands(bot: Bot) -> None:
    """
    Устанавливает пользовательские команды для бота.

    Аргументы:
        bot (Bot): Объект бота.

    Возвращает:
        None

    """
    commands = [
        BotCommand(command='/start', description='Начать игру.'),
        BotCommand(command='/help', description='Получить помощь')
    ]
    scope = BotCommandScopeDefault(type='default')
    await bot.set_my_commands(commands=commands, scope=scope)


async def set_admin_commands(bot: Bot, admin_id: str) -> None:
    """
    Устанавливает административные команды для бота.
    Команды будут отображаться пользователя чей айди прописан в bot.ini - admin_id

    Аргументы:
        bot (Bot): Объект бота.
        admin_id (str): Идентификатор администратора бота.

    Возвращает:
        None
    """
    commands = [
        BotCommand(command='/help', description='Получить помощь'),
        BotCommand(command='/stat', description='Статистика бота.')
    ]
    scope = BotCommandScopeChat(type='chat', chat_id=admin_id)
    await bot.set_my_commands(commands=commands, scope=scope)


async def set_commands(bot: Bot, admin_id: str) -> None:
    """
    Устанавливает команды для бота.

    Аргументы:
       bot (Bot): Объект бота.
       admin_id (str): Идентификатор администратора бота.

    Возвращает:
       None

       """
    await set_user_commands(bot)
    await set_admin_commands(bot, admin_id)


async def notify_admins(admin_id: str, bot: Bot) -> None:
    """
    Отправляет уведомление администратору о старте бота.

    Аргументы:
        admin_id (str): Идентификатор администратора.
        bot (Bot): Объект бота.

    Возвращает:
        None

    """
    await bot.send_message(chat_id=admin_id, text='Hi Administrator, the Bot started successfully!')


def make_total_days(data: dict) -> int:
    """
    Вычисляет общее количество дней между датами.

    Аргументы:
        data (dict): Словарь с данными о дате заезда и выезда.

    Возвращает:
        int: Общее количество дней.
    """
    start_date = date(data['check_in'].year, data['check_in'].month, data['check_in'].day)
    end_date = date(data['check_out'].year, data['check_out'].month, data['check_out'].day)
    return (end_date - start_date).days + 1


async def register_user(pool: Pool, uid: int, key: str) -> None:
    """
    Регистрирует пользователя в базе данных.

    Аргументы:
        pool (Pool): Объект пула подключений к базе данных.
        uid (int): Идентификатор пользователя.
        key (str): АПИ ключ пользователя.

    Возвращает:
        None
    """
    async with pool.acquire() as con:
        await con.execute('insert into users (id, key) values ($1, $2)', uid, key)


async def insert_hotel(current_hotel: HotelInfo, pool: Pool, user_id):
    """
    Записывает информацию о отеле в базу данных (История/Избранные).

    Аргументы:
        current_hotel (HotelInfo): Информация о выбранном отеле.
        pool (Pool): Объект пула подключений к базе данных.
        user_id: Идентификатор пользователя.

    Возвращает:
        bool: Флаг успешного выполнения операции.

    :raise HotelAlredyRememdered: если отель уже записан в базе
    """
    async with pool.acquire() as con:
        hotel_remembered = await con.fetchrow('select count(*) from hotels where hotel_id = $1 and owner = $2',
                                              current_hotel.id, int(user_id))

        if hotel_remembered['count'] == 1:
            raise HotelAlredyRememdered('Вы уже вносили этот отели в историю!')

        else:
            hotel_data = json.dumps(current_hotel._asdict())
            await con.execute('insert into hotels (owner, hotel_id, data) values ($1, $2, $3)', int(user_id), int(current_hotel.id), hotel_data)
            return True
