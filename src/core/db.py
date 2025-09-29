from contextlib import asynccontextmanager
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
    """Базовый класс с автоматическим именем таблицы и id."""

    @declared_attr
    def __tablename__(self) -> str:
        """Имя таблицы соответствует имени класса в нижнем регистре."""
        return self.__name__.lower()

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


Base = declarative_base(cls=PreBase)

engine = create_async_engine(settings.get_database_uri(), echo=True)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронная сессия SQLAlchemy для зависимостей."""
    async with AsyncSessionLocal() as session:
        yield session


@asynccontextmanager
async def get_async_session_cm() -> AsyncGenerator[AsyncSession, None]:
    """Контекстный менеджер с commit/rollback для скриптов."""
    session: AsyncSession = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
