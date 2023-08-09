from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from aiogram import Bot
from datetime import date


async def set_user_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command='/start', description='Начать игру.'),
        BotCommand(command='/help', description='Получить помощь')
    ]
    scope = BotCommandScopeDefault(type='default')
    await bot.set_my_commands(commands=commands, scope=scope)


async def set_admin_commands(bot: Bot, admin_id: str) -> None:
    commands = [
        BotCommand(command='/del', description='Удалить аккаунт пользователя.'),
        BotCommand(command='/help', description='Получить помощь'),
        BotCommand(command='/stat', description='Статистика бота.')
    ]  # TODO: реализовать команду /del и /stat
    scope = BotCommandScopeChat(type='chat', chat_id=admin_id)
    await bot.set_my_commands(commands=commands, scope=scope)


async def set_commands(bot: Bot, admin_id: str) -> None:
    await set_user_commands(bot)
    await set_admin_commands(bot, admin_id)


async def notify_admins(admin_id: str, bot: Bot) -> None:
    await bot.send_message(chat_id=admin_id, text='Hi Administrator, the Bot started successfully!')


def make_total_days(data: dict) -> int:
    start_date = date(data['check_in'].year, data['check_in'].month, data['check_in'].day)
    end_date = date(data['check_out'].year, data['check_out'].month, data['check_out'].day)
    return (end_date - start_date).days + 1

