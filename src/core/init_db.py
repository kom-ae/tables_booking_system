import logging
from typing import Optional

from fastapi_users.password import PasswordHelper
from sqlalchemy import select

from src.core.config import settings
from src.core.db import engine, get_async_session
from src.models.base import BaseModel
from src.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Создаёт все таблицы в базе."""
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


async def create_first_superuser() -> None:
    """Создаёт суперпользователя, если его нет."""
    password_helper = PasswordHelper()

    # Используем async for для асинхронного генератора
    async for session in get_async_session():
        result = await session.execute(
            select(User).where(User.email == settings.first_superuser_email),
        )
        user: Optional[User] = result.scalar_one_or_none()

        if not user:
            hashed_password = password_helper.hash(
                settings.first_superuser_password,
            )
            superuser = User(
                username='admin',
                email=settings.first_superuser_email,
                hashed_password=hashed_password,
                phone='+79991234567',
                is_superuser=True,
                role='admin',
            )
            session.add(superuser)
            await session.commit()
            logger.info(
                f'Суперпользователь {settings.first_superuser_email}создан.',
            )
        else:
            logger.info(
                f'Суперпользователь {settings.first_superuser_email}'
                'уже существует.',
            )
