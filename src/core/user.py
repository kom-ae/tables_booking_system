from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import (
    MIN_UPDATE_INTERVAL_SECONDS,
    SYSTEM_USERNAME,
    ZERO_DEFAULT_USER_ID,
)
from src.core.config import settings
from src.core.db import get_async_session
from src.core.logger import log_event
from src.crud.factory import get_user_crud
from src.exceptions.auth import (
    ExpiredTokenException,
    InvalidTokenException,
    PermissionDeniedException,
)
from src.exceptions.user import UserNotFoundException
from src.models.user import User

user_crud = get_user_crud()

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_async_session),
) -> User:
    """Возвращает текущего пользователя по JWT, обновляет last_used."""
    username = SYSTEM_USERNAME
    user_id = ZERO_DEFAULT_USER_ID

    if not token:
        log_event(
            'warning',
            'Отсутствует токен при доступе',
            username,
            user_id,
        )
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
        if not user_id or last_used is None:
            log_event('warning', 'Недействительный токен', username, user_id)
            raise InvalidTokenException()

        now_ts = datetime.now(timezone.utc).timestamp()
        if now_ts - last_used > settings.access_token_expire_minutes * 60:
            log_event('warning', 'Токен просрочен', username, user_id)
            raise ExpiredTokenException()
    except (jwt.JWTError, ValueError):
        log_event(
            'warning',
            'Ошибка при декодировании токена',
            username,
            user_id,
        )
        raise InvalidTokenException()

    user = await user_crud.get(user_id, db)
    if not user:
        log_event(
            'warning',
            f'Пользователь с ID {user_id} не найден',
            username,
            user_id,
        )
        raise UserNotFoundException()

    username = user.username
    user_id = user.id
    request.state.username = username
    request.state.user_id = user_id

    if now_ts - user.last_used > MIN_UPDATE_INTERVAL_SECONDS:
        await user_crud.update_last_used(db, user)
        log_event(
            'info',
            'Обновлено last_used для пользователя',
            username,
            user_id,
        )

    log_event('info', 'Доступ к эндпоинту подтверждён', username, user_id)
    return user


current_user = get_current_user


async def current_admin(user: User = Depends(current_user)) -> User:
    """Проверяет, что текущий пользователь — админ."""
    if not user.is_admin():
        log_event(
            'warning',
            f'Пользователь {user.username} недостаточно прав',
            user.username,
            user.id,
        )
        raise PermissionDeniedException()
    log_event(
        'info',
        f'Пользователь {user.username} прошёл проверку admin',
        user.username,
        user.id,
    )
    return user


async def current_manager(user: User = Depends(current_user)) -> User:
    """Проверяет, что текущий пользователь — менеджер или админ."""
    if not user.is_manager():
        log_event(
            'warning',
            f'Пользователь {user.username} недостаточно прав',
            user.username,
            user.id,
        )
        raise PermissionDeniedException()
    log_event(
        'info',
        f'Пользователь {user.username} прошёл проверку manager/admin',
        user.username,
        user.id,
    )
    return user


async def get_user_by_name(name: str, db: AsyncSession) -> Optional[User]:
    """Возвращает пользователя по email или телефону через CRUD."""
    user = await user_crud.get_by_name(db, name)
    username = user.username if user else SYSTEM_USERNAME
    user_id = user.id if user else ZERO_DEFAULT_USER_ID
    log_event(
        'info',
        f'Поиск пользователя по имени: {name}',
        username,
        user_id,
    )
    return user
