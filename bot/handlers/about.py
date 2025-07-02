from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.utils.messages import about_message
from bot.logger import logger
from bot.utils.keys import ADMIN_NAME

async def about_command(message: Message, state: FSMContext):

    logger.info(f"{message.from_user.id}, {message.from_user.first_name}")

    await message.answer(about_message.format(
        support_username=ADMIN_NAME
    ))
    await state.clear()