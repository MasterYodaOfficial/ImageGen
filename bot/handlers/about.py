from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.utils.messages import about_message
import loguru


async def about_command(message: Message, state: FSMContext):

    loguru.logger.info(f"{message.from_user.id}, {message.from_user.first_name}")

    await message.answer(about_message)
    await state.clear()