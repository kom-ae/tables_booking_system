from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import constants
from src.core.config import settings
from src.core.db import get_async_session
from src.models.user import User


# -------------------
# User database
# -------------------
async def get_user_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase[User, int], None]:
    """База пользователей."""
    yield SQLAlchemyUserDatabase(session, User)


# -------------------
# JWT authentication
# -------------------
bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')


def get_jwt_strategy() -> JWTStrategy:
    """JWT стратегия."""
    return JWTStrategy(
        secret=settings.secret,
        lifetime_seconds=constants.JWT_LIFETIME_SECONDS,
    )


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


# -------------------
# User manager
# -------------------
class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """Менеджер пользователей."""

    async def get_by_email(self, email: str) -> Optional[User]:
        """Пользователь по email или телефону."""
        query = select(User).where(
            (User.email == email) | (User.phone == email),
        )
        result = await self.user_db.session.execute(query)
        return result.scalars().first()

    async def validate_password(self, password: str, user: User) -> None:
        """Проверка пароля."""
        if len(password) < constants.THREE:
            raise ValueError(
                f'Password should be at least {constants.THREE} chars',
            )
        if user.email in password:
            raise ValueError('Password should not contain email')

    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None,
    ) -> None:
        """После регистрации."""
        print(f'Пользователь {user.email} зарегистрирован.')


# -------------------
# Dependency for FastAPI Users
# -------------------
async def get_user_manager(
    user_db: SQLAlchemyUserDatabase[User, int] = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """Менеджер пользователей."""
    yield UserManager(user_db)


# -------------------
# FastAPI Users instance
# -------------------
fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)


# -------------------
# Role-based dependencies
# -------------------
async def current_admin(user: User = Depends(current_user)) -> User:
    """Только админ."""
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not enough permissions',
        )
    return user


async def current_manager(user: User = Depends(current_user)) -> User:
    """Только менеджер или админ."""
    if user.role not in ('manager', 'admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not enough permissions',
        )
    return user
