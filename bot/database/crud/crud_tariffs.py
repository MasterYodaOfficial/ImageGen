from typing import List
from sqlalchemy.future import select
from bot.database.models import Tariff  # Импорт модели тарифов
from bot.database.session import get_session  # Импорт сессии, если у тебя она там


async def get_active_tariffs() -> List[Tariff]:
    async with get_session() as session:
        stmt = select(Tariff).where(Tariff.is_active == True).order_by(Tariff.sort_order)
        result = await session.execute(stmt)
        tariffs = result.scalars().all()
        return tariffs
