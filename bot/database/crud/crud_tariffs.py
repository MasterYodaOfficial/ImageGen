from typing import List
from sqlalchemy.future import select
from bot.database.models import Tariff
from bot.database.session import get_session


async def get_active_tariffs() -> List[Tariff]:
    async with get_session() as session:
        stmt = select(Tariff).where(Tariff.is_active == True).order_by(Tariff.sort_order)
        result = await session.execute(stmt)
        tariffs = result.scalars().all()
        return tariffs


async def get_tariff_by_id(tariff_id: str) -> Tariff | None:
    async with get_session() as session:
        result = await session.execute(
            select(Tariff).where(Tariff.id == tariff_id)
        )
        return result.scalar_one_or_none()