from sqlalchemy.future import select

from src.core.config import settings
from src.core.db import engine, get_async_session_cm
from src.core.logger import logger
from src.models.base import BaseModel
from src.models.user import User
from src.services.auth import PasswordService


async def init_db_and_superuser() -> None:
    """Инициализация базы данных и суперпользователя."""
    if not settings.debug:
        logger.info(
            f'{init_db_and_superuser.__doc__} Пропущено. '
            f'DEBUG: {settings.debug}',
        )
        return

    try:
        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)
            logger.info(f'{init_db_and_superuser.__doc__}')
    except Exception as error:
        logger.warning(
            f'{init_db_and_superuser.__doc__} '
            f'Таблицы уже существуют: {error}')
        return

    try:
        async with get_async_session_cm() as session:
            result = await session.execute(
                select(User).where(
                    User.email == settings.first_superuser_email,
                ),
            )
            user: User | None = result.scalar_one_or_none()

            if not user:
                password_hashed: str = PasswordService.hash_password(
                    settings.first_superuser_password,
                )
                superuser = User(
                    username=settings.first_superuser_username,
                    email=settings.first_superuser_email,
                    password=password_hashed,
                    phone=settings.first_superuser_phone_number,
                    is_superuser=True,
                    role=settings.first_superuser_role,
                )
                session.add(superuser)
                await session.commit()
                await session.refresh(superuser)

                logger.info(
                    f'Суперпользователь {settings.first_superuser_email} '
                    'создан',
                    user=superuser,
                )
            else:
                logger.info(
                    f'Суперпользователь {settings.first_superuser_email} '
                    'уже существует',
                    user=user,
                )
    except Exception as error:
        logger.error(f'Ошибка при создании суперпользователя: {error}')
