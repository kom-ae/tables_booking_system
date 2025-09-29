from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.logger import logger
from src.exceptions.auth import ExpiredTokenException, InvalidTokenException
from src.exceptions.user import UserNotFoundException
from src.models.user import User


async def get_current_user_logic(
    token_str: str,
    user_crud: Any,
    db: AsyncSession,
) -> User:
    """Валидация JWT токена и получение пользователя.

    Основная логика аутентификации:
    1. Декодирование и верификация JWT токена
    2. Проверка срока действия токена
    3. Поиск пользователя в базе данных
    4. Обработка различных сценариев ошибок

    Args:
        token_str: JWT токен из заголовка Authorization
        user_crud: CRUD объект для работы с пользователями
        db: Асинхронная сессия базы данных

    Returns:
        User: Аутентифицированный пользователь

    Raises:
        InvalidTokenException: Невалидный или поврежденный токен
        ExpiredTokenException: Просроченный токен
        UserNotFoundException: Пользователь не найден в базе

    """
    try:
        # Декодирование JWT токена с использованием секретного ключа
        payload = jwt.decode(
            token_str,
            settings.secret,
            algorithms=[settings.jwt_algorithm],
        )

        # Извлечение данных из payload
        user_id = int(payload.get('sub'))  # ID пользователя
        token_last_used_ts = payload.get(
            'last_used',
        )  # Время последнего использования

        if not user_id or token_last_used_ts is None:
            logger.warning(
                'Недействительный токен: отсутствуют обязательные поля',
            )
            raise InvalidTokenException()

        now = datetime.now(timezone.utc)
        token_last_used = datetime.fromtimestamp(
            token_last_used_ts,
            timezone.utc,
        )
        if now - token_last_used > timedelta(
            minutes=settings.access_token_expire_minutes,
        ):
            logger.warning(f'Токен просрочен. ID: {user_id}')
            raise ExpiredTokenException()

    except (JWTError, ValueError) as error:
        logger.warning(f'Ошибка при декодировании токена: {error}')
        raise InvalidTokenException()
    user: Optional[User] = await user_crud.get(user_id, db)
    if not user:
        logger.warning(f'Пользователь ID: {user_id} не найден')
        raise UserNotFoundException()

    logger.info(f'Успешная аутентификация пользователя c id:{user.id}')
    return user


async def get_user_by_name(
    name: str,
    db: AsyncSession,
    user_crud: Any,
) -> Optional[User]:
    """Поиск пользователя по имени, email или телефону."""
    user: Optional[User] = await user_crud.get_by_name(db, name)

    if user:
        logger.info(
            f'{get_user_by_name.__doc__} {name}',
            user=user,
        )
    else:
        logger.info('Пользователь не найден по идентификатору')

    return user
