from bot.utils.commands import set_commands
from aiogram import Bot
import aiohttp

async def start_bot(bot: Bot) -> None:
    """
    Устанавливает команды в меню бота
    """
    await set_commands(bot)


async def download_file(url: str, path: str) -> None:
    """Скачивает файл по url"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(path, "wb") as f:
                    f.write(await resp.read())
            else:
                raise ValueError(f"Ошибка загрузки файла: {resp.status}")

