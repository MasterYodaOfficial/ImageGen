from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.database.crud.crud_user import get_user
from bot.utils.messages import buy_message, get_tariff_id_inline_message, confirm_purchase_message, confirm_message
from bot.database.crud.crud_tariffs import get_active_tariffs
from bot.keyboards.inlines import make_tariff_buttons, make_payment_buttons, make_pay_link_button
from bot.utils.statesforms import StepForm

from bot.services.payment_service import create_payment_service, get_payment_status
from bot.database.crud.crud_tariffs import get_tariff_by_id
from bot.database.crud.crud_payments import confirm_payment, error_payment
from bot.logger import logger
import asyncio
import time
from bot.database.crud.crud_generation_model import get_model_prices_text


async def buy_command(message: Message, state: FSMContext):

    """Команда купить"""

    logger.info(f"{message.from_user.id}, {message.from_user.first_name}")
    tariffs = await get_active_tariffs()
    model_prices_text = await get_model_prices_text()
    await message.answer(
        text=buy_message.format(
            model_prices=model_prices_text
        ),
        reply_markup=make_tariff_buttons(
            tariffs=tariffs
        )
    )
    await state.set_state(StepForm.CHOOSING_TARIFF)


async def get_tariff_id_inline(call: CallbackQuery, state: FSMContext):

    """Принимает id тарифа и сохраняет в машину состояний"""

    logger.info(f"{call.from_user.id}, {call.from_user.first_name}")
    if call.data.startswith("tariff"):
        _, tariff_id = call.data.split(":")
        await state.update_data(tariff_id=tariff_id)
        await call.message.edit_text(
            text=get_tariff_id_inline_message,
            reply_markup=make_payment_buttons()
        )
        await state.set_state(StepForm.CHOOSING_PAYMENT_METHOD)
    else:
        await call.message.delete()

async def choose_payment_method(call: CallbackQuery, state: FSMContext):

    """Принимает кнопку выбора метода оплаты отправляет ссылку на оплату, ждет оплату и
    при оплате отправляет сообщение об успешной оплате"""

    logger.info(f"{call.from_user.id}, {call.from_user.first_name}")
    try:
        if call.data.startswith("pay"):
            _, payment_method = call.data.split(":") # Например: "yookassa" или "crypto"
            # yookassa / crypto / btc и т.д.

            await state.update_data(payment_method=payment_method)

            data = await state.get_data()

            tariff_id = data["tariff_id"]
            tariff = await get_tariff_by_id(tariff_id)

            user = await get_user(call.from_user)
            payment, pay_url = await create_payment_service(user, tariff, payment_method)

            await call.message.edit_text(
                text=confirm_purchase_message.format(
                    title=tariff.title,
                    price=tariff.price_rub,
                    method=payment_method
                ),
                reply_markup=make_pay_link_button(pay_url)
            )
            await state.set_state(StepForm.CONFIRM_PURCHASE)
            timeout = time.time() + 7 * 60  # 7 минут ожидания
            while time.time() < timeout:
                status = await get_payment_status(payment)
                if status == "paid":
                    await call.message.delete()
                    await call.message.answer(confirm_message)
                    await confirm_payment(payment.id)
                    await state.clear()
                    return
                current_state = await state.get_state()
                if current_state != StepForm.CONFIRM_PURCHASE:
                    logger.info(f"cancel {call.from_user.id}, {call.from_user.first_name}")
                    await error_payment(payment.id)
                    return
                await asyncio.sleep(10)
        else:
            await call.message.delete()
    except TypeError as ex:
        logger.debug(ex)
