from aiogram.filters import BaseFilter
from aiogram.types import Message
from asyncpg import Pool


class UserExists(BaseFilter):
    """
    Фильтр для проверки существования пользователя.

    Применяется для проверки, существует ли профиль пользователя в боте.

    :param pool: Пул подключений к базе данных.
    :type pool: Pool
    """

    def __init__(self, pool: Pool):
        self.pool = pool
        """
        Конструктор класса.

        :param pool: Пул подключений к базе данных.
        :type pool: Pool
        """

    async def __call__(self, event: Message):
        """
        Метод вызывается при проверке фильтра на каждое полученное сообщение.

        :param event: Объект сообщения.
        :type event: Message
        :return: Результат проверки фильтра.
        :rtype: bool
        """

        async with self.pool.acquire() as con:
            is_exists = await con.fetchrow('select count(*) from users where id = $1', event.from_user.id)
            if is_exists['count']:  # true if user exists
                return True
            await event.answer(
                'У вас нет профиля в боте!\nОснокомьтесь с информацией о боте для регистарции - <code>/help</code> ключ апи.')
