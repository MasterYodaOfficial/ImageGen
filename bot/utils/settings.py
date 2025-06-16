from aiogram import Dispatcher, Bot, F
import loguru

from bot.handlers.start import start_command
from bot.handlers.buy import buy_command, get_tariff_id_inline, choose_payment_method, payment_done_test
from bot.handlers.profile import profile_command
from bot.handlers.generate import generate_command, get_format_image, get_prompt, get_confirm_generation


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
    dp.message.register(generate_command, Command('generate'))

    # Колбеки покупки
    dp.callback_query.register(get_tariff_id_inline, StepForm.CHOOSING_TARIFF)
    dp.callback_query.register(choose_payment_method, StepForm.CHOOSING_PAYMENT_METHOD)
    dp.callback_query.register(payment_done_test, StepForm.CONFIRM_PURCHASE)

    # Колбеки генерации и отлов промта для генерации
    dp.callback_query.register(get_format_image, StepForm.CHOOSE_IMAGE_FORMAT)
    dp.message.register(get_prompt, StepForm.ENTER_PROMPT)
    dp.callback_query.register(get_confirm_generation, StepForm.CONFIRM_GENERATION)

    await set_commands(bot)
    loguru.logger.info('Запуск бота')

    await dp.start_polling(bot)
