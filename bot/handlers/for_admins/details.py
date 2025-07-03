from datetime import datetime
from sqlalchemy import Float, distinct, select, func
from aiogram.types import Message
from bot.database.session import get_session
from bot.database.crud.crud_user import is_admin
from bot.logger import logger
from bot.database.models import User, Tariff, Referral, Payment, ImageGeneration, GenerationModel



async def admin_details_command(message: Message):
    logger.info(f"{message.from_user.id} {message.from_user.first_name} запросил детали")
    if not await is_admin(message.from_user):
        return

    await message.answer("Формирую детальный отчёт...")

    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)
    month_name = now.strftime('%B %Y')

    async with get_session() as session:
        # 1. Платежная аналитика
        tariffs_stats = await session.execute(
            select(
                Tariff.title,
                func.count(Payment.id),
                func.sum(Payment.amount)
            )
            .join(Payment.tariff)
            .where(
                Payment.created_at >= start_of_month,
                Payment.status == "paid"
            )
            .group_by(Tariff.title)
            .order_by(func.sum(Payment.amount).desc())
        )

        # 2. Аналитика генераций
        models_stats = await session.execute(
            select(
                GenerationModel.name,
                func.count(ImageGeneration.id),
                func.sum(GenerationModel.token_cost)
            )
            .join(ImageGeneration.model)
            .where(ImageGeneration.created_at >= start_of_month)
            .group_by(GenerationModel.name)
            .order_by(func.count(ImageGeneration.id).desc())
        )

        # 3. Реферальная аналитика
        new_referrals = await session.scalar(
            select(func.count(User.id))
            .where(
                User.join_date >= start_of_month,
                User.invited_by_code.is_not(None)
            )
        )

        referral_bonuses = await session.scalar(
            select(func.sum(Referral.reward_amount_tokens))
            .where(Referral.created_at >= start_of_month)
        ) or 0

        # 4. Дополнительные метрики
        active_users = await session.scalar(
            select(func.count(distinct(ImageGeneration.user_id)))
            .where(ImageGeneration.created_at >= start_of_month)
        )

        avg_gens_per_user = await session.scalar(
            select(func.cast(func.count(ImageGeneration.id), Float) /
                   func.nullif(func.count(distinct(ImageGeneration.user_id)), 0))
            .where(ImageGeneration.created_at >= start_of_month)
        ) or 0

        top_generators = await session.execute(
            select(
                User.username,
                func.count(ImageGeneration.id).label('total_gens')
            )
            .join(ImageGeneration.user)
            .where(ImageGeneration.created_at >= start_of_month)
            .group_by(User.username)
            .order_by(func.count(ImageGeneration.id).desc())
            .limit(3)
        )

    # Формирование отчёта
    report = f"<b>📊 ДЕТАЛЬНАЯ СТАТИСТИКА ЗА {month_name}</b>\n\n"

    # Раздел по тарифам
    report += "<b>💰 ПЛАТЕЖИ И ТАРИФЫ:</b>\n"
    total_payments = 0
    total_tariffs = 0
    for title, count, amount in tariffs_stats:
        total_payments += amount or 0
        total_tariffs += count or 0
        report += f"▪ {title}: {count} покупок на {amount}₽\n"
    report += (f"├ Всего: {total_tariffs} платежей\n"
               f"└ Суммарная выручка: {total_payments}₽\n\n")

    # Раздел по моделям генерации
    report += "<b>🖼 ГЕНЕРАЦИИ ПО МОДЕЛЯМ:</b>\n"
    total_gens = 0
    total_tokens = 0
    for model, count, tokens in models_stats:
        total_gens += count or 0
        total_tokens += tokens or 0
        report += f"▪ {model}: {count} генераций ({tokens} токенов)\n"
    report += (f"├ Всего генераций: {total_gens}\n"
               f"└ Потрачено токенов: {total_tokens}\n\n")

    # Реферальная программа
    report += "<b>👥 РЕФЕРАЛЬНАЯ ПРОГРАММА:</b>\n"
    report += f"▪ Привлечено пользователей: {new_referrals}\n"
    report += f"▪ Выдано бонусных токенов: {referral_bonuses}\n\n"

    # Дополнительные метрики
    report += "<b>🔍 ДОПОЛНИТЕЛЬНЫЕ МЕТРИКИ:</b>\n"
    report += f"▪ Активных пользователей: {active_users}\n"
    report += f"▪ Среднее генераций на пользователя: {avg_gens_per_user:.1f}\n"

    # Топ генераторов
    report += "\n<b>🏆 ТОП-3 ПОЛЬЗОВАТЕЛЕЙ ПО ГЕНЕРАЦИЯМ:</b>\n"
    for i, (username, gens) in enumerate(top_generators, 1):
        report += f"{i}. {username or 'Без имени'}: {gens} генераций\n"

    await message.answer(report)