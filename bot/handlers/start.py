from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.database.session import get_session
from bot.database.crud.crud_user import get_or_create_user
from bot.utils.messages import start_text, start_text_trial

async def start_command(message: Message, state: FSMContext):
    referral_code = None
    # Проверяем, есть ли аргументы в команде
    if message.text and len(message.text.split()) > 1:
        referral_code = message.text.split()[1]
    async with get_session() as session:
        # Добавляем в БД
        user, new = await get_or_create_user(session, message.from_user, referral_code)
        start_msg = start_text.format(
            name=user.username
        )
        if new: # Если пользователь новый ставим сообщение о 3 бесплатных генерациях
            start_msg += start_text_trial

        await message.answer(start_msg)
        await state.clear()
