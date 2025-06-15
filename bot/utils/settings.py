from aiogram import Dispatcher, Bot, F
import loguru

from bot.handlers.start import start_command
from bot.handlers.buy import buy_command, get_tariff_id_inline, choose_payment_method, payment_done_test
from bot.handlers.profile import profile_command

from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command

from bot.utils.keys import BOT_TOKEN
from bot.utils.commands import set_commands
from bot.utils.utils import start_bot

from bot.utils.statesforms import StepForm

dp = Dispatcher()
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))



async def run_bot() -> None:

    dp.message.filter(F.chat.type == "private")
    dp.startup.register(start_bot)

    # Команды
    dp.message.register(start_command, Command('start'))
    dp.message.register(buy_command, Command('buy'))
    dp.message.register(profile_command, Command('profile'))

    # Колбеки покупки
    dp.callback_query.register(get_tariff_id_inline, StepForm.CHOOSING_TARIFF)
    dp.callback_query.register(choose_payment_method, StepForm.CHOOSING_PAYMENT_METHOD)
    dp.callback_query.register(payment_done_test, StepForm.CONFIRM_PURCHASE)


    await set_commands(bot)
    loguru.logger.info('Запуск бота')

    await dp.start_polling(bot)
