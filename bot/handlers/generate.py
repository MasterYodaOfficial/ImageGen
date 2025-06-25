from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from bot.utils.statesforms import StepForm
from bot.utils.messages import (choosing_format_message, enter_prompt_message, attention_prompt_message,
                                continue_prompt_message, out_of_generations)
from bot.keyboards.inlines import make_formate_buttons, continue_prompt_buttons
from bot.database.crud.crud_generations import create_image_generation, update_image_generation_status
from bot.database.crud.crud_user import has_available_generations, update_user_generations
import loguru
from bot.services.image_gen_api import ImageMode, generate_dalle_image, generate_image_stream
# from testing_3 import free_generate, ImageMode
# from bot.utils.utils import download_file


async def generate_command(message: Message, state: FSMContext):
    """Старт команды генерации изображения"""

    loguru.logger.info(f"{message.from_user.id}, {message.from_user.first_name}")
    has_generations = await has_available_generations(message.from_user)
    if has_generations:
        await message.answer(
            text=choosing_format_message,
            reply_markup=make_formate_buttons()
        )
        await state.set_state(StepForm.CHOOSE_IMAGE_FORMAT)
    else:
        await message.answer(
            text=out_of_generations)
        await state.clear()

async def get_format_image(call: CallbackQuery, state: FSMContext):

    """Принимает кнопку выбора формата изображения"""

    loguru.logger.info(f"{call.from_user.id}, {call.from_user.first_name}")
    if call.data.startswith("format"):
        _, format_image = call.data.split(":")
        sent = await call.message.edit_text(
            text=enter_prompt_message
        )
        await state.update_data(
            cur_message_id=sent.message_id, # Тут сохраняю id сообщения для дальнейшего изменения
            format_image=format_image
        )
        await state.set_state(StepForm.ENTER_PROMPT)
    else:
        await call.message.delete()


async def get_prompt(message: Message, state: FSMContext):

    """Обработка промта от пользователя"""

    loguru.logger.info(f"{message.from_user.id}, {message.from_user.first_name}")

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
            loguru.logger.debug(f"{ex}")
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

    loguru.logger.info(f"{call.from_user.id}, {call.from_user.first_name}")
    if call.data.startswith("confirm"):
        _, call_answer = call.data.split(":")
        data_user = await state.get_data()
        prompt = data_user.get('prompt')
        format_image = data_user.get('format_image')
        if call_answer == "start_gen":
            generation = await create_image_generation(call.from_user, prompt)
            await call.message.edit_text("⏳ (от 0 до 2 мин.) Генерируем изображение...")
            try:
                # image_url = await free_generate(
                #     prompt=prompt,
                #     mode=ImageMode(format_image)
                # )
                image_url = await generate_image_stream(
                    prompt=prompt,
                    mode=ImageMode(format_image)
                )
                # image_url = await generate_dalle_image(
                #     prompt=prompt,
                #     mode=ImageMode(format_image)
                # )
                if not image_url:
                    raise ValueError("Ошибка генерации")
                # filename = generation.filename
                # await download_file(image_url, filename)
                await update_image_generation_status(generation.id, 'success', image_url)
                await call.message.bot.send_document(
                    chat_id=call.from_user.id,
                    document=image_url,
                    caption=prompt
                )
                await update_user_generations(call.from_user, -1)
            except Exception as ex:
                loguru.logger.exception(ex)
                await update_image_generation_status(generation.id, "error")
                await call.message.answer("❌ Произошла ошибка при генерации изображения. Попробуйте ещё раз и проверьте правила промта")
            await call.message.delete()
            await state.clear()
        if call_answer == "restart_gen":
            await call.message.edit_text(
                text=choosing_format_message,
                reply_markup=make_formate_buttons()
            )
            await state.set_state(StepForm.CHOOSE_IMAGE_FORMAT)
    else:
        await call.message.delete()
