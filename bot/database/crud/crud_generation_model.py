from sqlalchemy import select
from bot.database.models import GenerationModel
from bot.database.session import get_session
from bot.logger import logger

async def get_model_token_map() -> dict:
    """
    Формирует словарь с расценками моделей
    """
    async with get_session() as session:
        result = await session.execute(
            select(GenerationModel).where(GenerationModel.is_active == True)
        )
        models = result.scalars().all()

        # Сопоставляем name -> token_cost
        return {model.name: model.token_cost for model in models}

async def get_generation_model(model_name: str) -> GenerationModel | None:
    """
    Получает модель генерации
    """
    async with get_session() as session:
        try:
            model = await session.execute(
                select(GenerationModel).where(
                    GenerationModel.name == model_name,
                    GenerationModel.is_active == True
                )
            )
            return model.scalar_one_or_none()
        except ValueError as ex:
            logger.error(ex)
            return None

async def get_active_generation_models() -> list[GenerationModel]:
    """Получает все активные модели"""
    async with get_session() as session:
        result = await session.execute(
            select(GenerationModel).where(GenerationModel.is_active == True)
        )
        return result.scalars().all()

async def get_model_prices_text() -> str:
    """
    Формирует текст для подстановки в текст с расценками
    """
    models = await get_active_generation_models()
    lines = []
    for model in models:
        lines.append(
            f"• <b>{model.name}</b> — {model.token_cost} токенов"
        )
    return "\n".join(lines)