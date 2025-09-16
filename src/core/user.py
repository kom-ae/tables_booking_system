from typing import AsyncGenerator, Optional, Union

from fastapi import Depends, Request
from fastapi_users import (
    BaseUserManager,
    FastAPIUsers,
    IntegerIDMixin,
    InvalidPasswordException,
)
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app import constants
from app.core.config import settings
from app.core.db import get_async_session
from app.models.user import User
from app.schemas.user import UserCreate


async def get_user_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase[User, int], None]:
    """Получить объект SQLAlchemyUserDatabase."""
    yield SQLAlchemyUserDatabase(session, User)


bearer_transport: BearerTransport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    """Создать стратегию JWT с секретом и временем жизни токена."""
    return JWTStrategy(
        secret=settings.secret, lifetime_seconds=constants.JWT_LIFETIME_SECONDS
    )


auth_backend: AuthenticationBackend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """Менеджер пользователей с кастомной валидацией пароля."""

    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, User],
    ) -> None:
        """Проверить пароль пользователя на мин.длину и отсутствие email."""
        if len(password) < constants.THREE:
            raise InvalidPasswordException(
                reason=(
                    f"Password should be at least "
                    f"{constants.THREE} characters"
                )
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail"
            )

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ) -> None:
        """Действия после успешной регистрации пользователя."""
        print(f"Пользователь {user.email} зарегистрирован.")


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase[User, int] = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """Получить объект UserManager."""
    yield UserManager(user_db)


fastapi_users: FastAPIUsers[User, int] = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
