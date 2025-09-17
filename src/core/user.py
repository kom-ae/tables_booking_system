from typing import AsyncGenerator, Optional, Union

from fastapi import Depends, HTTPException, Request, status
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
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import constants
from src.core.config import settings
from src.core.db import get_async_session
from src.models.user import User
from src.schemas.user import UserCreate


# -------------------
# User database
# -------------------
async def get_user_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase[User, int], None]:
    """Возвращает объект базы данных пользователей."""
    yield SQLAlchemyUserDatabase(session, User)


# -------------------
# JWT authentication
# -------------------
bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')


def get_jwt_strategy() -> JWTStrategy:
    """Возвращает стратегию JWT для аутентификации."""
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
    """Менеджер пользователей с кастомной логикой."""

    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, User],
    ) -> None:
        """Валидирует пароль пользователя."""
        if len(password) < constants.THREE:
            raise InvalidPasswordException(
                reason='Password should be at least'
                '{constants.THREE} characters',
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason='Password should not contain e-mail',
            )

    async def get_by_email_or_phone(self, identifier: str) -> Optional[User]:
        """Возвращает пользователя по email или телефону."""
        query = select(User).where(
            (User.email == identifier) | (User.phone == identifier),
        )
        result = await self.user_db.session.execute(query)
        return result.scalars().first()

    async def authenticate(
        self,
        identifier: str,
        password: str,
    ) -> Optional[User]:
        """Аутентифицирует пользователя по идентификатору и паролю."""
        user = await self.get_by_email_or_phone(identifier)
        if user and await self.verify_password(password, user.hashed_password):
            return user
        return None

    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None,
    ) -> None:
        """Вызывается после регистрации пользователя."""
        print(f'Пользователь {user.email} зарегистрирован.')


# -------------------
# Dependency for FastAPI Users
# -------------------
async def get_user_manager(
    user_db: SQLAlchemyUserDatabase[User, int] = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """Возвращает менеджер пользователей для зависимости FastAPI."""
    yield UserManager(user_db)


# -------------------
# FastAPI Users instance
# -------------------
fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)


# -------------------
# Custom role-based dependencies
# -------------------
async def current_admin(user: User = Depends(current_user)) -> User:
    """Проверяет, что текущий пользователь — администратор."""
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not enough permissions',
        )
    return user


async def current_manager(user: User = Depends(current_user)) -> User:
    """Проверяет, что текущий пользователь — менеджер или администратор."""
    if user.role not in ('manager', 'admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not enough permissions',
        )
    return user
