from aiogram.types import User as TG_User
from bot.database.session import get_session
from sqlalchemy import select
from bot.database.models import GenerationModel, User



async def check_tokens_available(tg_user: TG_User, model_name: str) -> bool:
    """
    Проверяет, хватает ли у пользователя токенов для генерации с указанной моделью.
    Возвращает True, если токенов достаточно, False - если нет.
    """
    async with get_session() as session:
        result = await session.execute(
            select(GenerationModel).where(
                GenerationModel.name == model_name
            )
        )
        model_generation = result.scalar_one_or_none()
        result = await session.execute(
            select(User).where(User.telegram_id == tg_user.id)
        )
        user = result.scalar_one_or_none()
        # Проверяем, хватает ли токенов
        return user.tokens >= model_generation.token_cost

async def spend_tokens_for_generation(tg_user: TG_User, model_name: str) -> bool:
    """
    Списывает токены по выбранной модели у пользователя с баланса.
    """
    async with get_session() as session:
        result = await session.execute(
            select(GenerationModel).where(
                GenerationModel.name == model_name
            )
        )
        model_generation = result.scalar_one_or_none()
        result = await session.execute(
            select(User).where(User.telegram_id == tg_user.id)
        )
        user = result.scalar_one_or_none()
        # Списываю
        user.tokens -= model_generation.token_cost
        session.add(user)
        await session.commit()

