from bot.database.models import Payment, User, Tariff
from yookassa import Payment as YooPayment
import asyncio
from bot.database.crud.crud_payments import create_payment


from bot.payments.yookassa import create_payment_yokassa



async def create_payment_service(
        user: User,
        tariff: Tariff,
        method: str
) -> tuple[Payment, str]:
    """
    Создаёт платёж через нужную платёжную систему, сохраняет его в БД и возвращает объект и ссылку на оплату.
    """
    if method == "yookassa":
        external_id, payment_url = await create_payment_yokassa(tariff.price_rub, tariff.title)
    elif method == "crypto":
        pass # TODO Сделать оплату криптой
        # external_id, payment_url = await crypto_create_payment(amount, currency)
    else:
        raise ValueError(f"Unknown payment method: {method}")
    payment: Payment = await create_payment(
        user_id=user.id,
        tariff_id=tariff.id,
        amount=tariff.price_rub,
        method=method,
        external_id=external_id
    )
    return payment, payment_url

async def get_payment_status(payment: Payment):
    """
    Проверяет статус платежа по его id
    """
    method = payment.payment_method
    external_id = payment.external_id

    if method == "yookassa":
        yoo_payment = await asyncio.to_thread(YooPayment.find_one, external_id)
        status = yoo_payment.status
        if status == "succeeded":
            return "paid"
        if status in ['canceled', 'failed']:
            return "failed"
    if method == "crypto":
        pass # TODO сделать проверку крипты
