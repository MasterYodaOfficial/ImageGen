from sqlalchemy.future import select
from sqlalchemy import update
from bot.database.models import ImageGeneration, User
from bot.database.session import get_session
from uuid import uuid4
from aiogram.types import User as TG_User


async def create_image_generation(user_tg: TG_User, prompt: str) -> ImageGeneration:
    async with get_session() as session:
        filename = f"generated/{uuid4()}.png" # Задел на то, чтобы сохранять все картинки на сервере

        result = await session.execute(
            select(User).where(User.telegram_id == user_tg.id)
        )
        user: User = result.scalar_one_or_none()

        generation = ImageGeneration(
            user_id=user.id,
            prompt=prompt,
            filename=filename,
            status="pending"
        )
        session.add(generation)
        await session.commit()
        await session.refresh(generation)
        return generation


async def update_image_generation_status(generation_id: int, status: str, url_file: str | None = None):
    async with get_session() as session:
        stmt = (update(ImageGeneration).where(ImageGeneration.id == generation_id).values(status=status))
        if url_file:
            stmt = stmt.values(url=url_file)
        await session.execute(stmt)
        await session.commit()
