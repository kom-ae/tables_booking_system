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
    4. Обновление времени последнего использования
    5. Обработка различных сценариев ошибок

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
        payload = jwt.decode(
            token_str,
            settings.secret,
            algorithms=[settings.jwt_algorithm],
        )

        # Извлечение ID пользователя из payload
        user_id = int(payload.get('sub'))

        if not user_id:
            logger.warning(
                'Недействительный токен: отсутствуют обязательные поля',
            )
            raise InvalidTokenException()

    except jwt.ExpiredSignatureError:
        logger.warning(
            'Просроченный токен',
            user=None,
        )

        raise ExpiredTokenException()

    except (JWTError, ValueError) as error:
        logger.warning(f'Ошибка при декодировании токена: {error}')
        raise InvalidTokenException()

    user: Optional[User] = await user_crud.get(user_id, db)

    if not user:
        logger.warning(f'Пользователь ID: {user_id} не найден')
        raise UserNotFoundException()

    user = await user_crud.update_last_used(db, user)

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
