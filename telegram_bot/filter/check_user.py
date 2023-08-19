from aiogram.filters import BaseFilter
from aiogram.types import Message
from asyncpg import Pool


class UserExists(BaseFilter):
    def __init__(self, pool: Pool):
        self.pool = pool

    async def __call__(self, event: Message):
        async with self.pool.acquire() as con:
            is_exists = await con.fetchrow('select count(*) from users where id = $1', event.from_user.id)
            if is_exists['count']:  # true if user exists
                return True
            await event.answer('У вас нет профиля в боте!\nВы должны создать его командой - <code>/register</code> ключ апи.')


