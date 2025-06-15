from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.session import get_session
from bot.database.models import Tariff
from bot.database.crud.crud_user import get_or_create_user
from bot.utils.messages import buy_message, get_tariff_id_inline_message, confirm_purchase_message
from bot.database.crud.crud_tariffs import get_active_tariffs
from bot.keyboards.inlines import make_tariff_buttons, make_payment_buttons, make_pay_link_button
from bot.utils.statesforms import StepForm

from bot.database.crud.crud_payments import create_payment, confirm_payment
from bot.database.crud.crud_tariffs import get_tariff_by_id
from bot.database.crud.crud_user import get_user
import loguru


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

    """Принимает кнопку выбора метода оплаты отправляет ссылку на оплату"""

    loguru.logger.info(f"{call.from_user.id}, {call.from_user.first_name}")

    # yookassa / crypto / btc и т.д.
    payment_method = call.data  # Например: "yookassa" или "crypto"
    await state.update_data(payment_method=payment_method)

    data = await state.get_data()

    tariff_id = data["tariff_id"]
    tariff = await get_tariff_by_id(tariff_id)

    user = await get_user(call.from_user)

    await call.message.edit_text(
        text=confirm_purchase_message.format(
            title=tariff.title,
            price=tariff.price_rub,
            method=payment_method
        ),
        reply_markup=make_pay_link_button()
    )
    payment = await create_payment(
        user_id=user.id,
        tariff_id=tariff.id,
        amount=tariff.generation_amount,
        method=payment_method
    )
    await state.update_data(payment_id=payment.id)
    await state.set_state(StepForm.CONFIRM_PURCHASE)

async def payment_done_test(call: CallbackQuery, state: FSMContext):

    """Тестово типа приняли оплату тут сохраняется история в БД. У пользователя добавляется кол-во запросов,
    создается история в payment"""

    loguru.logger.info(f"{call.from_user.id}, {call.from_user.first_name}")

    data = await state.get_data()

    payment_id = data['payment_id']
    payment = await confirm_payment(payment_id)
    if payment:
        await call.message.edit_text("Оплата получена, кол-во запросов для генерации добавлено. Можно проверить в /profile")
    else:
        await call.message.edit_text("Произошла какая то херня надо чекать")
    await state.clear()
