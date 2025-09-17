from contextlib import asynccontextmanager

from fastapi_users.password import PasswordHelper
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.db import get_async_session
from src.models.user import User

# Оборачиваем get_async_session в asynccontextmanager с аннотацией типа
get_async_session_context: asynccontextmanager[AsyncSession] = (
    asynccontextmanager(get_async_session)
)


async def create_first_superuser() -> None:
    """Создаёт суперпользователя напрямую через базу, если его нет."""
    password_helper: PasswordHelper = PasswordHelper()

    async with get_async_session_context() as session:  # type: AsyncSession
        result = await session.execute(
            select(User).where(User.email == settings.first_superuser_email),
        )
        user: User | None = result.scalar_one_or_none()

        if not user:
            hashed_password: str = password_helper.hash(
                settings.first_superuser_password,
            )

            superuser: User = User(
                email=settings.first_superuser_email,
                hashed_password=hashed_password,
                username='admin',
                phone='+79991234567',
                is_superuser=True,
                is_active=True,
                role='admin',
            )
            session.add(superuser)
            await session.commit()
