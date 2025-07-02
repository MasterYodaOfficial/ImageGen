from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models import User, Referral
from bot.database.session import get_session
from aiogram.types import User as TG_User
import string
import random
from bot.utils.keys import DEFAULT_GIFT_TOKENS


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
                reward_amount_tokens=DEFAULT_GIFT_TOKENS  # или выдай сразу бонус, если хочешь
            )
            session.add(referral)
            inviter.tokens += DEFAULT_GIFT_TOKENS
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
        select(func.sum(Referral.reward_amount_tokens)).where(Referral.inviter_code == referral_code)
    )
    total = result.scalar()
    return total or 0

async def get_user(tg_user: TG_User) -> User:
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == tg_user.id)
        )
        return result.scalar_one_or_none()

async def is_admin(tg_user: TG_User) -> bool:
    """Проверка на админку"""
    user = await get_user(tg_user)
    return user.is_admin if user else False

async def get_all_telegram_ids() -> list[int]:
    """Получает список всех Telegram ID пользователей"""
    async with get_session() as session:
        result = await session.execute(select(User.telegram_id))
        telegram_ids = result.scalars().all()
        return telegram_ids

async def has_available_generations(tg_user: TG_User) -> bool:
    """Проверяет, есть ли у пользователя хотя бы 1 доступная генерация"""
    async with get_session() as session:
        result = await session.execute(
            select(User.counter).where(User.telegram_id == tg_user.id)
        )
        counter = result.scalar_one_or_none()
        return counter is not None and counter > 0

async def update_user_tokens(tg_user: TG_User, delta: int) -> None:
    """
    Обновляет количество генераций у пользователя.
    delta > 0 — добавить генерации
    delta < 0 — потратить генерации (если хватает)
    """
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == tg_user.id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("Пользователь не найден")

        if delta < 0 and user.tokens + delta < 0:
            raise ValueError("Недостаточно генераций")

        user.tokens += delta
        session.add(user)
        await session.commit()


