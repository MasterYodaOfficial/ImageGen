from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models import User, Referral
from aiogram.types import User as TG_User
import string
import random


async def generate_unique_ref_code(session: AsyncSession, length: int = 8) -> str:
    """Генерация реферального кода"""
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(alphabet, k=length))
        result = await session.execute(select(User).where(User.referral_code == code))
        if result.scalar_one_or_none() is None:
            return code


async def get_or_create_user(session: AsyncSession, tg_user: TG_User, referral_code: str | None = None):
    # 1. Проверяем, есть ли пользователь
    result = await session.execute(
        select(User).where(User.telegram_id == tg_user.id)
    )
    user = result.scalar_one_or_none()

    if user:
        return user, False  # Уже существует

    own_code = await generate_unique_ref_code(session) # Генерируем уникальный реферальный код
    # 2. Создаём нового пользователя
    new_user = User(
        telegram_id=tg_user.id,
        username=tg_user.first_name,
        referral_code=own_code,
        invited_by_code=referral_code if referral_code else None
    )
    session.add(new_user)
    await session.flush()  # получаем id пользователя без коммита
    if referral_code:
        inviter_result = await session.execute(
            select(User).where(User.referral_code == referral_code)
        )
        inviter = inviter_result.scalar_one_or_none()
        if inviter:
            referral = Referral(
                inviter_code=referral_code,
                invited_user_id=new_user.id,
                reward_amount=10  # или выдай сразу бонус, если хочешь
            )
            session.add(referral)
            inviter.counter += 10
            session.add(inviter)
    try:
        await session.commit()
        await session.refresh(new_user)
        return new_user, True
    except IntegrityError:
        await session.rollback()
        raise ValueError("Пользователь с таким telegram_id уже существует.")


async def get_invited_count(session: AsyncSession, referral_code: str) -> int:
    """Функция возвращает кол-во приглашенных от пользователя по реферальному коду"""
    result = await session.execute(
        select(func.count()).select_from(Referral).where(Referral.inviter_code == referral_code)
    )
    return result.scalar_one() or 0

async def get_total_referral_rewards(session: AsyncSession, referral_code: str) -> int:
    """Функция возвращает кол-во накопленных бонусов(запросов) от приглашенных пользователей"""
    result = await session.execute(
        select(func.sum(Referral.reward_amount)).where(Referral.inviter_code == referral_code)
    )
    total = result.scalar()
    return total or 0
