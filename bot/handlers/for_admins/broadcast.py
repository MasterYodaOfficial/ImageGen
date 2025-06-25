from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.database.crud.crud_user import is_admin

from bot.utils.messages import broadcast_message
from bot.utils.statesforms import StepForm
from bot.keyboards.inlines import continue_broadcast_buttons

import loguru



async def broadcast_command(message: Message, state: FSMContext):
    """
    Запуск команды для рассылки пользователям
    """
    loguru.logger.info(f"{message.from_user.id}, {message.from_user.first_name}")
    if is_admin(message.from_user):
        await message.answer(broadcast_message)
        await state.set_state(StepForm.WAITING_BROADCAST_MESSAGE)


async def receive_broadcast_message(message: Message, state: FSMContext):
    """Ждем сообщение для отправки"""
    loguru.logger.info(f"{message.from_user.id}, {message.from_user.first_name}")
    await state.update_data(broadcast_message=message)
    await message.reply(
        text="✅ Получено! Проверьте это сообщение и подтвердите рассылку или отмените.",
        reply_markup=continue_broadcast_buttons()
    )
    await message.copy_to(chat_id=message.chat.id)
    await state.set_state(StepForm.CONFIRM_BROADCAST)

async def confirm_broadcast(call: CallbackQuery, state: FSMContext):
    """
    Принимаем кнопку согласия на отправку и отправляем
    """
    