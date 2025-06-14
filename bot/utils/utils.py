from bot.utils.commands import set_commands
from aiogram import Bot


async def start_bot(bot: Bot) -> None:
    """
    Устанавливает команды в меню бота
    """
    await set_commands(bot)
