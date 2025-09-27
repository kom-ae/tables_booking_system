from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import MIN_UPDATE_INTERVAL_SECONDS
from src.core.db import get_async_session
from src.core.logger import project_log
from src.core.user import get_current_user_logic
from src.crud.factory import CRUDUser, get_user_crud
from src.exceptions.auth import PermissionDeniedException
from src.models.user import User

bearer_scheme: HTTPBearer = HTTPBearer(auto_error=False)


async def current_user(
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_async_session),
    user_crud: CRUDUser = Depends(get_user_crud),
) -> User:
    """Возвращает текущего пользователя и обновляет last_used."""
    if not token:
        project_log('warning', 'Отсутствует токен при доступе', user=None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Токен отсутствует',
        )

    user: User = await get_current_user_logic(token.credentials, user_crud, db)

    request.state.username = user.username
    request.state.user_id = user.id

    last_used: datetime = user.last_used
    if last_used.tzinfo is None:
        last_used = last_used.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) - last_used > timedelta(
        seconds=MIN_UPDATE_INTERVAL_SECONDS,
    ):
        await user_crud.update_last_used(db, user)
        project_log('info', 'Обновлен last_used пользователя', user=user)

    project_log('info', 'Пользователь аутентифицирован', user=user)
    return user


async def current_admin(user: User = Depends(current_user)) -> User:
    """Проверка прав администратора."""
    if not user.is_admin():
        project_log(
            'warning',
            f'Пользователь {user.username} недостаточно прав',
            user=user,
        )
        raise PermissionDeniedException()
    project_log(
        'info',
        f'Пользователь {user.username} прошёл проверку admin',
        user=user,
    )
    return user


async def current_manager(user: User = Depends(current_user)) -> User:
    """Проверка прав менеджера или администратора."""
    if not user.is_manager():
        project_log(
            'warning',
            f'Пользователь {user.username} недостаточно прав',
            user=user,
        )
        raise PermissionDeniedException()
    project_log(
        'info',
        f'Пользователь {user.username} прошёл проверку manager/admin',
        user=user,
    )
    return user


async def get_current_user_or_none(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
    user_crud: CRUDUser = Depends(get_user_crud),
) -> Optional[User]:
    """Возвращает пользователя по токену из заголовка или None."""
    auth_header: str = request.headers.get('Authorization')
    if not auth_header:
        return None

    try:
        token_str = auth_header.split(' ')[1]
        return await get_current_user_logic(token_str, user_crud, db)
    except Exception as error:
        project_log(
            'warning',
            f'Не удалось получить пользователя по токену:{error}',
            user=None,
        )
        return None
