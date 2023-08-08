from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from aiogram import Bot
from datetime import date
from asyncpg import Pool, Connection

from SkillboxProject.telegram_bot.model.types import HotelInfo, Destination, Reviews, Coordinates, Price
from SkillboxProject.telegram_bot.api.request import get_hotel_detail_request


async def set_user_commands(bot):
    commands = [
        BotCommand(command='/start', description='Начать игру.'),
        BotCommand(command='/help', description='Получить помощь')
    ]
    scope = BotCommandScopeDefault(type='default')
    await bot.set_my_commands(commands=commands, scope=scope)


async def set_admin_commands(bot, admin_id):
    commands = [
        BotCommand(command='/del', description='Удалить аккаунт пользователя.'),
        BotCommand(command='/help', description='Получить помощь'),
        BotCommand(command='/stat', description='Статистика бота.')
    ]  # TODO: реализовать команду /del и /stat
    scope = BotCommandScopeChat(type='chat', chat_id=admin_id)
    await bot.set_my_commands(commands=commands, scope=scope)


async def set_commands(bot, admin_id):
    await set_user_commands(bot)
    await set_admin_commands(bot, admin_id)


async def notify_admins(admin_id, bot: Bot):
    await bot.send_message(chat_id=admin_id, text='Hi Administrator, the Bot started successfully!')


def check_number(string: str):
    if string.isdigit():
        return True
    elif string.count('.') == 1:
        integer_part, decimal_part = string.split('.')
        if integer_part.isdigit() and decimal_part.isdigit():
            return True
    return False


def make_total_days(data: dict):
    start_date = date(data['check_in'].year, data['check_in'].month, data['check_in'].day)
    end_date = date(data['check_out'].year, data['check_out'].month, data['check_out'].day)
    return (end_date - start_date).days + 1


async def insert_hotel(data: HotelInfo, pool: Pool, id: int):
    async with pool.acquire() as con:
        hotel_id = int(data['id'])
        count = await con.fetchrow(f'select count(*) as count from users where id = {id} and hotel_id = {hotel_id}')
        if count['count'] == 0:
            await con.execute('insert into users (id, hotel_id) values ($1, $2)', id, hotel_id)
            await con.execute('insert into hotels (id, data) values ($1, $2)', hotel_id, str(data))
            return True
        return False
