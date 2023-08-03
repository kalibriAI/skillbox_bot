from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, pool):
        self.pool = pool

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        data['pool'] = self.pool
        await handler(event, data)



