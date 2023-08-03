from aiogram.filters import BaseFilter
from aiogram.types import Message


class ChatTypeFilter(BaseFilter):
    async def __call__(self, event: Message):
        if event.chat.type == 'private':
            return True
        await event.reply('Ботом можно пользоваться только в ЛС бота.')
