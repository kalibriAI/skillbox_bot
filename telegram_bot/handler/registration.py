from aiogram import Router
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.types import Message
from asyncpg import Pool

from const import help_message
from service.bfuncs import register_user
from api.request import test_repuest

reg_router = Router(name='Registration Router')


@reg_router.message(Command('register'))
async def register_cmd(message: Message, command: CommandObject, pool: Pool):
    api_key = command.args
    async with pool.acquire() as con:
        is_exists = await con.fetchrow('select count(*) from users where id = $1', message.from_user.id)
    if is_exists['count']:  # true if user exists
        await message.answer('У вас уже есть профиль!')
    else:
        print(api_key)
        if api_key is not None:
            if test_repuest(api_key):
                await register_user(pool, message.from_user.id, api_key)
                await message.answer('Профиль успешно создан, теперь вы можете пользоваться ботом.')
            else:
                await message.answer('Что то не так с ключем!')
        else:
            await message.answer('Введите ключе после register - /register key')


@reg_router.message(Command('help'), StateFilter(None))
async def help_cmd(message: Message):
    await message.answer(help_message, disable_web_page_preview=True)
