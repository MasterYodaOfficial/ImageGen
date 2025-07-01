from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from bot.utils.statesforms import StepForm
from bot.utils.messages import (choosing_format_message, enter_prompt_message, attention_prompt_message,
                                continue_prompt_message, choose_model_message)
from bot.keyboards.inlines import make_formate_buttons, continue_prompt_buttons, make_models_buttons
from bot.database.crud.crud_generations import create_image_generation, update_image_generation_status

from bot.services.image_generator import ImageMode, ImageModel
from bot.logger import logger
from bot.services.image_generator import image_generator



async def generate_command(message: Message, state: FSMContext):
    """Старт команды генерации изображения, предоставляет выбрать формат изображения"""

    logger.info(f"{message.from_user.id}, {message.from_user.first_name}")
    message = await message.answer(
        text=choosing_format_message,
        reply_markup=make_formate_buttons()
    )
    cur_message_id = message.message_id
    await state.update_data(cur_message_id=cur_message_id)
    await state.set_state(StepForm.CHOOSE_IMAGE_FORMAT)

async def get_format_image(call: CallbackQuery, state: FSMContext):

    """Принимает кнопку выбора формата изображения, предоставляет выбрать модель для генерации"""

    logger.info(f"{call.from_user.id}, {call.from_user.first_name}")
    if call.data.startswith("format"):
        _, format_image = call.data.split(":")
        await state.update_data(format_image=format_image)
        await call.message.edit_text(
            text=choose_model_message,
            reply_markup=make_models_buttons()
        )
        await state.set_state(StepForm.CHOOSING_MODEL)
    else:
        await call.message.delete()

async def get_model_generation(call: CallbackQuery, state: FSMContext):
    """Принимает кнопки с выбором модели для генерации, просит ввести промт"""
    if call.data.startswith("model"):
        _, model_generation = call.data.split(":")
        await state.update_data(model_generation=model_generation)
        await call.message.edit_text(
            text=enter_prompt_message
        )
        await state.set_state(StepForm.ENTER_PROMPT)
    else:
        await call.message.delete()


async def get_prompt(message: Message, state: FSMContext):

    """Обработка промта от пользователя"""

    logger.info(f"{message.from_user.id}, {message.from_user.first_name}")

    max_prompt_length = 500
    user_data = await state.get_data()
    prompt = message.text.strip()

    message_id = user_data.get("cur_message_id")
    await message.delete()
    if len(prompt) > max_prompt_length:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message_id,
                text=attention_prompt_message
            )

            return
        except TelegramBadRequest as ex:
            logger.debug(f"{ex}")
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
    await state.set_state(StepForm.CONFIRM_GENERATION)


async def get_confirm_generation(call: CallbackQuery, state: FSMContext):

    """Принимает кнопку для продолжения генерации. Создает изображение и отправляет его пользователю"""

    logger.info(f"{call.from_user.id}, {call.from_user.first_name}")
    if call.data.startswith("confirm"):
        _, call_answer = call.data.split(":")

        if call_answer == "start_gen":
            await call.message.edit_text("⏳ (от 0 до 2 мин.) Генерируем изображение...")
            data = await state.get_data()
            prompt = data['prompt']
            mode = ImageMode(data['format_image'])
            model = ImageModel(data.get('model_generation'))  # По умолчанию DALL-E-3
            generation = await create_image_generation(call.from_user, prompt)
            result = await image_generator.generate(prompt, model, mode)
            await call.message.delete()
            # TODO Осуществить списание у пользователя токенов
            if not result:
                await call.message.answer("❌ Ошибка генерации, пожалуйста повторите с учетом правил платформы.")
                await update_image_generation_status(generation.id, 'error')
                await state.clear()
                return
            await call.message.answer_document(result, caption=prompt)
            await update_image_generation_status(generation.id, 'success')
            await state.clear()
            return
        if call_answer == "restart_gen":
            await call.message.edit_text(
                text=choosing_format_message,
                reply_markup=make_formate_buttons()
            )
            await state.set_state(StepForm.CHOOSE_IMAGE_FORMAT)
    else:
        await call.message.delete()
