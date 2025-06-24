from yookassa import Payment
from functools import partial
import asyncio
from bot.utils.keys import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY
from loguru import logger
from bot.utils.keys import BOT_NAME


async def create_payment_yokassa(price: str, description: str) -> tuple[str, str] | None:
    """
    Создает платеж.
    """
    payload = {
    "amount": {
        "value": f"{price}",
        "currency": "RUB"
    },
    "confirmation": {
        "type": "redirect",
        "return_url": f"https://t.me/{BOT_NAME}" # https://t.me/ImageTester_bot
    },
    "capture": True,
    "description": description
    }
    try:
        payment = await asyncio.to_thread(
            partial(
            Payment.create,
            payload
            )
        )
        external_id = payment.id
        payment_url = payment.confirmation.confirmation_url

        return external_id, payment_url
    except BaseException as ex:
        logger.exception(ex)
        return None
