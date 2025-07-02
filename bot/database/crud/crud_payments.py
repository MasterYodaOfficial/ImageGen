from bot.database.models import User, Tariff, Payment
from sqlalchemy import select
from bot.database.session import get_session



async def create_payment(user_id: int, tariff_id: str, amount: int, method: str, external_id: str, currency: str = "RUB") -> Payment:
    async with get_session() as session:
        payment = Payment(
            user_id=user_id,
            tariff_id=tariff_id,
            amount=amount,
            currency=currency,
            payment_method=method,
            status="pending",
            external_id=external_id
        )
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        return payment


async def confirm_payment(payment_id: str):
    async with get_session() as session:
        # Получаем платеж
        result = await session.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        payment: Payment = result.scalar_one_or_none()

        if not payment or payment.status != "pending":
            return None  # Уже оплачен или не найден

        # Обновляем статус
        payment.status = "paid"

        # Получаем пользователя и тариф
        user = await session.get(User, payment.user_id)
        tariff = await session.get(Tariff, payment.tariff_id)

        if not user or not tariff:
            return None

        # Начисляем токены
        user.tokens += tariff.tokens_amount + (tariff.bonus_tokens or 0)

        await session.commit()
        return payment

async def error_payment(payment_id: str):
    async with get_session() as session:
        result = await session.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        payment: Payment = result.scalar_one_or_none()
        # Обновляем статус
        payment.status = "failed"
        # Получаем пользователя и тариф
        user = await session.get(User, payment.user_id)
        tariff = await session.get(Tariff, payment.tariff_id)

        if not user or not tariff:
            return None
        await session.commit()
        return payment