from aiogram.types import Message
from sqlalchemy import select, func
from bot.database.models import User, Payment, ImageGeneration
from bot.database.session import get_session
from datetime import datetime
from bot.database.crud.crud_user import is_admin

async def admin_stats_command(message: Message):
    if await is_admin(message.from_user):
        await message.answer("Загружаю...")

        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)

        async with get_session() as session:
            # Кол-во пользователей
            users_count = await session.scalar(select(func.count()).select_from(User))

            # Новые пользователи за месяц
            new_users = await session.scalar(
                select(func.count()).where(User.join_date >= start_of_month)
            )
            # Платежи
            monthly_payments = await session.execute(
                select(
                    func.count(Payment.id),
                    func.sum(Payment.amount)
                ).where(Payment.created_at >= start_of_month, Payment.status == "paid")
            )
            pay_count, total_sum = monthly_payments.one()
            total_sum = total_sum or 0
            # Генерации
            gens = await session.execute(
                select(
                    func.count(ImageGeneration.id),
                    func.count().filter(ImageGeneration.status == "error")
                ).where(ImageGeneration.created_at >= start_of_month)
            )
            total_gens, failed_gens = gens.one()

        avg_check = total_sum / pay_count if pay_count else 0

        await message.answer(
            f"<b>📊 Статистика за {now.strftime('%B %Y')}:</b>\n\n"
            f"👥 Пользователей всего: <b>{users_count}</b>\n"
            f"🆕 Новых за месяц: <b>{new_users}</b>\n\n"
            f"💳 Платежей: <b>{pay_count}</b>\n"
            f"💰 Сумма: <b>{total_sum}₽</b>\n"
            f"📈 Средний чек: <b>{round(avg_check, 2)}₽</b>\n\n"
            f"🖼 Генераций: <b>{total_gens}</b>\n"
            f"❌ Ошибок генерации: <b>{failed_gens}</b>"
        )
