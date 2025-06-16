from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.utils.statesforms import StepForm
from bot.utils.messages import (choosing_format_message, enter_prompt_message, attention_prompt_message,
                                continue_prompt_message)
from bot.keyboards.inlines import make_formate_buttons, continue_prompt_buttons
import loguru


async def generate_command(message: Message, state: FSMContext):
    """Старт команды генерации изображения"""

    loguru.logger.info(f"{message.from_user.id}, {message.from_user.first_name}")


    await message.answer(
        text=choosing_format_message,
        reply_markup=make_formate_buttons()
    )
    await state.set_state(StepForm.CHOOSE_IMAGE_FORMAT)

async def get_format_image(call: CallbackQuery, state: FSMContext):

    """Принимает кнопку выбора формата изображения"""

    loguru.logger.info(f"{call.from_user.id}, {call.from_user.first_name}")

    sent = await call.message.edit_text(
        text=enter_prompt_message
    )
    await state.update_data(
        cur_message_id=sent.message_id, # Тут сохраняю id сообщения для дальнейшего изменения
        format_image=call.data
    )
    await state.set_state(StepForm.ENTER_PROMPT)


async def get_prompt(message: Message, state: FSMContext):

    """Обработка промта от пользователя"""

    loguru.logger.info(f"{message.from_user.id}, {message.from_user.first_name}")

    max_prompt_length = 500
    user_data = await state.get_data()
    prompt = message.text.strip()

    message_id = user_data.get("cur_message_id")
    if len(prompt) > max_prompt_length:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id,
            text=attention_prompt_message
        )
        await message.delete()
        return

    # Сохраняем промт
    await state.update_data(prompt=prompt)

    # Переход к следующему шагу — подтверждение генерации

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message_id,
        text=continue_prompt_message.format(
            prompt=prompt,
            image_format=user_data.get("format_image")
        ),
        reply_markup=continue_prompt_buttons()
    )
    await message.delete()
    await state.set_state(StepForm.CONFIRM_GENERATION)

async def get_confirm_generation(call: CallbackQuery, state: FSMContext):

    """Принимает кнопку выбора формата изображения"""

    loguru.logger.info(f"{call.from_user.id}, {call.from_user.first_name}")

    if call.data == "start_gen":
        await call.message.edit_text("Изображение сгенерировано")
        await state.clear()

    if call.data == "restart_gen":
        await call.message.edit_text(
            text=choosing_format_message,
            reply_markup=make_formate_buttons()
        )
        await state.set_state(StepForm.CHOOSE_IMAGE_FORMAT)
