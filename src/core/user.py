from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import MIN_UPDATE_INTERVAL_SECONDS
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
    username = settings.system_username
    user_id = settings.default_user_id

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
        token_last_used_ts = payload.get('last_used')
        if not user_id or token_last_used_ts is None:
            log_event('warning', 'Недействительный токен', username, user_id)
            raise InvalidTokenException()

        now = datetime.now(timezone.utc)
        token_last_used = datetime.fromtimestamp(
            token_last_used_ts,
            timezone.utc,
        )
        if now - token_last_used > timedelta(
            minutes=settings.access_token_expire_minutes,
        ):
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

    # Преобразуем last_used в aware datetime, если вдруг она naive
    last_used = user.last_used
    if last_used.tzinfo is None:
        last_used = last_used.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) - last_used > timedelta(
        seconds=MIN_UPDATE_INTERVAL_SECONDS,
    ):
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
    username = user.username if user else settings.system_username
    user_id = user.id if user else settings.default_user_id
    log_event(
        'info',
        f'Поиск пользователя по имени: {name}',
        username,
        user_id,
    )
    return user
