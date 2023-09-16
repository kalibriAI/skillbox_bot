from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message


class DatabaseMiddleware(BaseMiddleware):
    """
    Промежуточный слой для передачи подключений в хендлеры.

    Аргументы:
        pool (Pool): Объект пула подключений к базе данных.

    Атрибуты:
        pool (Pool): Объект пула подключений к базе данных.

    """

    def __init__(self, pool):
        self.pool = pool

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        """
        Вызывается при обработке запроса.

        Аргументы:
            handler (callable): Функция обработчика запроса.
            event (Message): Объект сообщения.
            data (dict): Данные запроса.

        Возвращает:
            Любой: Результат обработки запроса.

        """
        data['pool'] = self.pool
        await handler(event, data)
