from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
from bot.utils.keys import DATABASE_URL


engine = create_async_engine(DATABASE_URL, echo=False)

# Фабрика сессий
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Базовая модель
Base = declarative_base()

# Контекстный менеджер для получения сессии
@asynccontextmanager
async def get_session():
    async with async_session() as session:
        yield session
