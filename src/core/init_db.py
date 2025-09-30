from sqlalchemy.future import select

from src.core.config import settings
from src.core.db import engine, get_async_session_cm
from src.core.logger import project_log
from src.models.base import BaseModel
from src.models.user import User
from src.services.auth import PasswordService


async def init_db_and_superuser() -> None:
    """Инициализация базы и создание суперпользователя только в dev-режиме."""
    if not settings.debug:
        project_log('info', 'Prod mode: ничего не создаём')
        return

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
        project_log('info', 'Таблицы созданы (dev mode)')

    async with get_async_session_cm() as session:
        result = await session.execute(
            select(User).where(User.email == settings.first_superuser_email),
        )
        user = result.scalar_one_or_none()

        if not user:
            password_hashed = PasswordService.hash_password(
                settings.first_superuser_password,
            )
            superuser = User(
                username=settings.first_superuser_name,
                email=settings.first_superuser_email,
                password=password_hashed,
                phone=settings.first_superuser_phone_number,
                is_superuser=True,
                role=settings.first_superuser_role,
            )
            session.add(superuser)
            await session.commit()
            await session.refresh(superuser)

            project_log(
                'info',
                f'Суперпользователь {settings.first_superuser_email} создан',
                user=superuser,
            )
        else:
            project_log(
                'info',
                f'Суперпользователь {settings.first_superuser_email} '
                'уже существует',
                user=user,
            )
