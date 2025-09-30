from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.logger import project_log
from src.exceptions.auth import ExpiredTokenException, InvalidTokenException
from src.exceptions.user import UserNotFoundException
from src.models.user import User


async def get_current_user_logic(
    token_str: str,
    user_crud: Any,
    db: AsyncSession,
) -> User:
    """Возвращает пользователя по JWT."""
    try:
        payload = jwt.decode(
            token_str,
            settings.secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = int(payload.get('sub'))
        token_last_used_ts = payload.get('last_used')

        if not user_id or token_last_used_ts is None:
            project_log('warning', 'Недействительный токен', user=None)
            raise InvalidTokenException()

        now = datetime.now(timezone.utc)
        token_last_used = datetime.fromtimestamp(
            token_last_used_ts,
            timezone.utc,
        )

        if now - token_last_used > timedelta(
            minutes=settings.access_token_expire_minutes,
        ):
            project_log('warning', 'Токен просрочен', user=None)
            raise ExpiredTokenException()

    except (JWTError, ValueError):
        project_log('warning', 'Ошибка при декодировании токена', user=None)
        raise InvalidTokenException()

    user: Optional[User] = await user_crud.get(user_id, db)
    if not user:
        project_log(
            'warning',
            f'Пользователь с ID {user_id} не найден',
            user=None,
        )
        raise UserNotFoundException()

    return user


async def get_user_by_name(
    name: str,
    db: AsyncSession,
    user_crud: Any,
) -> Optional[User]:
    """Возвращает пользователя по имени/email/телефону."""
    user: Optional[User] = await user_crud.get_by_name(db, name)
    if user:
        project_log('info', f'Поиск пользователя по имени: {name}', user=user)
    else:
        project_log('info', f'Пользователь {name} не найден', user=None)
    return user
