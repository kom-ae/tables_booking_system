import logging

from sqlalchemy import text
from sqlalchemy.future import select

from src.api.utils.auth import get_password_hash
from src.core.config import settings
from src.core.db import engine, get_async_session
from src.models.base import BaseModel
from src.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Инициализация базы."""
    async with engine.begin() as conn:
        if settings.debug:
            await conn.run_sync(BaseModel.metadata.create_all)
            logger.info('✅ Таблицы созданы (dev mode)')
        else:
            await conn.execute(text('SELECT 1'))
            logger.info('✅ Подключение к БД успешно (prod mode)')


async def create_first_superuser() -> None:
    """Создаёт суперпользователя (только в dev-режиме)."""
    if not settings.debug:
        logger.info('⏩ Пропуск создания суперпользователя (prod mode)')
        return

    async for session in get_async_session():
        result = await session.execute(
            select(User).where(User.email == settings.first_superuser_email),
        )
        user = result.scalar_one_or_none()

        if not user:
            first_superuser_password = get_password_hash(
                settings.first_superuser_password,
            )
            superuser = User(
                username=settings.first_superuser_username,
                email=settings.first_superuser_email,
                password=first_superuser_password,
                phone=settings.first_superuser_phone_number,
                is_superuser=True,
                role=settings.first_superuser_role,
            )
            session.add(superuser)
            await session.commit()
            logger.info(
                f'✅ Суперпользователь {settings.first_superuser_email}'
                'создан.',
            )
        else:
            logger.info(
                f'ℹ️ Суперпользователь {settings.first_superuser_email}'
                'уже существует.',
            )
