from typing import Optional

from fastapi_users.password import PasswordHelper
from sqlalchemy import select

from src.core.config import settings
from src.core.db import get_async_session
from src.models.user import User


async def create_first_superuser() -> None:
    """Создаёт суперпользователя напрямую через базу, если его нет."""
    password_helper = PasswordHelper()

    # Используем get_async_session как асинхронный генератор напрямую
    async for session in get_async_session():
        # Проверяем, существует ли уже пользователь с таким email
        result = await session.execute(
            select(User).where(User.email == settings.first_superuser_email),
        )
        user: Optional[User] = result.scalar_one_or_none()

        if not user:
            # Хэшируем пароль
            hashed_password = password_helper.hash(
                settings.first_superuser_password,
            )

            # Создаём суперпользователя
            superuser = User(
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
