from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from asyncpg import Pool

admin_router = Router()


@admin_router.message(Command('stat'))
async def stat_admin_cmd(message: Message, pool: Pool):
    async with pool.acquire() as con:
        users = await con.fetchrow('select count(*) from users')

    await message.answer(f'В боте зарегестрировано {"{:,.2f}".format(users["count"])[:-3]} человек.')

