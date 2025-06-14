from aiogram import Dispatcher, Bot, F
import loguru

from bot.handlers.start import start_command
from bot.handlers.buy import buy_command
from bot.handlers.profile import profile_command

from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command

from bot.utils.keys import BOT_TOKEN
from bot.utils.commands import set_commands
from bot.utils.utils import start_bot


dp = Dispatcher()
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))



async def run_bot() -> None:

    dp.message.filter(F.chat.type == "private")
    dp.startup.register(start_bot)

    dp.message.register(start_command, Command('start'))
    dp.message.register(buy_command, Command('buy'))
    dp.message.register(profile_command, Command('profile'))

    await set_commands(bot)
    loguru.logger.info('Запуск бота')

    await dp.start_polling(bot)
