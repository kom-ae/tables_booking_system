import contextlib

from fastapi_users.exceptions import UserAlreadyExists
from pydantic import EmailStr

from src.core.config import settings
from src.core.db import get_async_session
from src.core.user import get_user_db, get_user_manager
from src.schemas.user import UserCreate

# Async context managers
get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(
    email: EmailStr,
    password: str,
    username: str,
    phone: str,
    is_superuser: bool = False,
) -> None:
    """Создаёт пользователя с email, паролем, username и телефоном."""
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    await user_manager.create(
                        UserCreate(
                            email=email,
                            password=password,
                            username=username,
                            phone=phone,
                            is_superuser=is_superuser,
                        ),
                    )
    except UserAlreadyExists:
        pass  # Игнорируем, если пользователь уже существует


async def create_first_superuser() -> None:
    """Создаёт первого суперпользователя из настроек, если он указан."""
    if settings.first_superuser_email and settings.first_superuser_password:
        await create_user(
            email=settings.first_superuser_email,
            password=settings.first_superuser_password,
            username='admin',
            phone='+79991234567',
            is_superuser=True,
        )
