from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import MIN_UPDATE_INTERVAL_SECONDS
from src.core.db import get_async_session
from src.core.logger import logger
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
    """Dependency: возвращает текущего аутентифицированного пользователя.

    Выполняет:
    1. Проверку наличия токена
    2. Валидацию JWT токена
    3. Обновление времени последней активности (last_used)
    4. Добавление пользователя в request.state для логов

    Args:dee
        request: FastAPI request объект
        token: Bearer токен из заголовка Authorization
        db: Асинхронная сессия БД
        user_crud: CRUD для работы с пользователями

    Returns:
        User: Аутентифицированный пользователь

    Raises:
        HTTPException: 401 если токен отсутствует или невалиден

    """
    # Проверка наличия токена
    if not token:
        logger.warning('Отсутствует токен при доступе')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Токен отсутствует',
        )

    try:
        # Валидация токена и получение пользователя
        user: User = await get_current_user_logic(
            token.credentials,
            user_crud,
            db,
        )
    except Exception as error:
        # Единообразная ошибка для избежания утечки информации
        logger.warning(f'Ошибка аутентификации: {error}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный или просроченный токен',
        )

    # Сохранение информации о пользователе в request.state
    # для middleware и логов
    request.state.username = user.username
    request.state.user_id = user.id

    # Обновление времени последней активности с защитой от частых записей в БД
    last_used: datetime = user.last_used
    if last_used.tzinfo is None:
        # Приведение времени к UTC если нет информации о таймзоне
        last_used = last_used.replace(tzinfo=timezone.utc)

    current_time = datetime.now(timezone.utc)
    # Обновляем last_used только если прошло достаточно времени
    if current_time - last_used > timedelta(
        seconds=MIN_UPDATE_INTERVAL_SECONDS,
    ):
        try:
            await user_crud.update_last_used(db, user)
            logger.info(f'Обновлен last_used пользователя c id:{user.id}')
        except Exception as error:
            # Не прерываем выполнение если не удалось обновить last_used
            logger.error(f'Ошибка обновления last_used: {error}', user=user)

    logger.info('Пользователь аутентифицирован')
    return user


async def current_admin(user: User = Depends(current_user)) -> User:
    """Dependency: проверяет права администратора."""
    if not user.is_admin():
        logger.warning('Недостаточно прав для администратора', user=user)
        raise PermissionDeniedException()

    logger.info(
        f'Пользователь прошел проверку admin: {user.id}',
        user=user,
    )
    return user


async def current_manager(user: User = Depends(current_user)) -> User:
    """Dependency: проверяет права менеджера или администратора."""
    if not user.is_manager():
        logger.warning(f'{current_manager.__doc__} Отказано', user=user)
        raise PermissionDeniedException()

    logger.info(f'{current_manager.__doc__} Успешно', user=user)
    return user


async def get_current_user_or_none(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
    user_crud: CRUDUser = Depends(get_user_crud),
) -> Optional[User]:
    """Dependency: возвращает пользователя по токену или None.

    Используется для опциональной аутентификации,
    где пользователь может быть не авторизован.
    Например: публичные эндпоинты с дополнительным
    функционалом для авторизованных пользователей.

    Args:
        request: FastAPI request объект
        db: Асинхронная сессия БД
        user_crud: CRUD для работы с пользователями

    Returns:
        Optional[User]: Пользователь если токен валиден, иначе None

    """
    auth_header: str = request.headers.get('Authorization')
    if not auth_header:
        return None

    try:
        parts = auth_header.split(' ')
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None

        token_str = parts[1]
        user = await get_current_user_logic(token_str, user_crud, db)
        logger.debug(
            'Получен пользователь по опциональному токену.'
            f'ID: {user.id}',
        )
        return user

    except Exception as error:
        logger.debug(
            f'Не удалось получить пользователя по токену: {error}',
            user=None,
        )
        return None
