from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Начало'
        ),
        BotCommand(
            command='generate',
            description='Ввод запроса'
        ),
        BotCommand(
            command='buy',
            description='Выбор тарифа'
        ),
        BotCommand(
            command='profile',
            description='Личный кабинет'
        ),
        BotCommand(
            command='about',
            description='О нас'
        )
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
