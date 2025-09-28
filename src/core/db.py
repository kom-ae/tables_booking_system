from typing import AsyncGenerator

from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    declared_attr,
    mapped_column,
    sessionmaker,
)

from src.core.config import settings


class PreBase:
    """Базовый класс с автоматическим именованием таблиц и полем id."""

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


Base = declarative_base(cls=PreBase)

engine = create_async_engine(settings.get_database_uri, echo=True)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронный генератор сессии базы данных."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
