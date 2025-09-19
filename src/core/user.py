from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions.auth import (
    ExpiredTokenException,
    InvalidTokenException,
    PermissionDeniedException,
    UserNotFoundException,
)
from src.constants import SECONDS_IN_MINUTE
from src.core.config import settings
from src.core.db import get_async_session
from src.crud import user_crud
from src.models.user import User

# -------------------
# Swagger UI: кнопка Authorize
# -------------------
bearer_scheme = HTTPBearer(auto_error=False)


# -------------------
# Центральная зависимость: текущий пользователь
# -------------------
async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_async_session),
) -> User:
    """Возвращает текущего пользователя по JWT и обновляет last_used."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Токен отсутствует',
        )

    try:
        payload = jwt.decode(
            token.credentials,
            settings.secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = int(payload.get('sub'))
        last_used = payload.get('last_used')
        if not user_id or not last_used:
            raise InvalidTokenException()

        now_ts = datetime.now(timezone.utc).timestamp()
        if (
            now_ts - last_used
            > settings.access_token_expire_minutes * SECONDS_IN_MINUTE
        ):
            raise ExpiredTokenException()
    except (jwt.JWTError, ValueError):
        raise InvalidTokenException()

    user = await user_crud.get(user_id, db)
    if not user:
        raise UserNotFoundException()

    # Автопродление last_used
    await user_crud.update_last_used(db, user)
    return user


# Псевдоним для удобного импорта
current_user = get_current_user


# -------------------
# Проверка ролей
# -------------------
async def current_admin(user: User = Depends(current_user)) -> User:
    """Проверяет, что текущий пользователь — админ."""
    if user.role != 'admin':
        raise PermissionDeniedException()
    return user


async def current_manager(user: User = Depends(current_user)) -> User:
    """Проверяет, что текущий пользователь — менеджер или админ."""
    if user.role not in ('manager', 'admin'):
        raise PermissionDeniedException()
    return user


# -------------------
# Получение пользователя по имени
# -------------------
async def get_user_by_name(name: str, db: AsyncSession) -> Optional[User]:
    """Возвращает пользователя по email или телефону через CRUD."""
    return await user_crud.get_by_name(db, name)
