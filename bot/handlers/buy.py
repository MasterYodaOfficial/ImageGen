from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.session import get_session
from bot.database.models import Tariff
from bot.database.crud.crud_user import get_or_create_user, get_user
from bot.utils.messages import buy_message, get_tariff_id_inline_message, confirm_purchase_message
from bot.database.crud.crud_tariffs import get_active_tariffs
from bot.keyboards.inlines import make_tariff_buttons, make_payment_buttons, make_pay_link_button
from bot.utils.statesforms import StepForm

from bot.services.payment_service import create_payment_service, get_payment_status
from bot.database.crud.crud_tariffs import get_tariff_by_id
from bot.database.crud.crud_payments import confirm_payment, error_payment
import loguru
import asyncio
import time



async def buy_command(message: Message, state: FSMContext):

    """Команда купить"""

    loguru.logger.info(f"{message.from_user.id}, {message.from_user.first_name}")

    async with get_session() as session:
        # Добавляем в БД
        user, new = await get_or_create_user(session, message.from_user)
        tariffs = await get_active_tariffs()

        await message.answer(
            text=buy_message,
            reply_markup=make_tariff_buttons(
                tariffs=tariffs
            )
        )
        await state.set_state(StepForm.CHOOSING_TARIFF)


async def get_tariff_id_inline(call: CallbackQuery, state: FSMContext):

    """Принимает id тарифа и сохраняет в машину состояний"""

    loguru.logger.info(f"{call.from_user.id}, {call.from_user.first_name}")

    tariff_id = int(call.data)
    await state.update_data(tariff_id=tariff_id)
    await call.message.edit_text(
        text=get_tariff_id_inline_message,
        reply_markup=make_payment_buttons()
    )
    await state.set_state(StepForm.CHOOSING_PAYMENT_METHOD)

async def choose_payment_method(call: CallbackQuery, state: FSMContext):

    """Принимает кнопку выбора метода оплаты отправляет ссылку на оплату, ждет оплату и
    при оплате отправляет сообщение об успешной оплате"""

    loguru.logger.info(f"{call.from_user.id}, {call.from_user.first_name}")

    # yookassa / crypto / btc и т.д.
    payment_method = call.data  # Например: "yookassa" или "crypto"
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
    await state.set_state(StepForm.CHOOSING_PAYMENT_METHOD)
    timeout = time.time() + 7 * 60  # 7 минут ожидания
    while time.time() < timeout:
        status = await get_payment_status(payment)
        if status == "paid":
            await call.message.delete()
            await call.message.answer("Оплата прошла, спасибо")
            await confirm_payment(payment.id)
            await state.clear()
            return
        current_state = await state.get_state()
        if current_state != StepForm.CHOOSING_PAYMENT_METHOD:
            loguru.logger.info(f"cancel {call.from_user.id}, {call.from_user.first_name}")
            await error_payment(payment.id)
            return
        await asyncio.sleep(10)