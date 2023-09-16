from aiogram.filters import BaseFilter
from aiogram.types import Message


class ChatTypeFilter(BaseFilter):
    """
    Фильтр для сообщений в зависимости от типа чата.

    Применяется для проверки, является ли чат, из которого получено сообщение, приватным (личным) чатом.

    :param BaseFilter: Базовый класс фильтра.
    :type BaseFilter: class
    """

    async def __call__(self, event: Message):
        """
       Метод вызывается при проверке фильтра на каждое полученное сообщение.

       :param event: Объект сообщения.
       :type event: Message
       :return: Результат проверки фильтра.
       :rtype: bool
       """

        if event.chat.type == 'private':
            return True
        await event.reply('Ботом можно пользоваться только в ЛС бота.')
