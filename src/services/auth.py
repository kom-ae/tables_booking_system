import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import jwt
from passlib.context import CryptContext

from src.core.config import settings
from src.core.logger import logger


class PasswordService:
    """Сервис для работы с паролями."""

    _pwd_context: CryptContext = CryptContext(
        schemes=['bcrypt'],
        deprecated='auto',
    )

    @classmethod
    def hash_password(
        cls,
        password: str,
        user: Optional[object] = None,
    ) -> str:
        """Возвращает хэш переданного пароля."""
        hashed: str = cls._pwd_context.hash(password)
        logger.info('Хэширование пароля выполнено', user=user)
        return hashed

    @classmethod
    def verify_password(
        cls,
        plain_password: str,
        hashed_password: str,
        user: Optional[object] = None,
    ) -> bool:
        """Проверяет, совпадает ли пароль с хэшом."""
        result: bool = cls._pwd_context.verify(plain_password, hashed_password)
        status: str = 'успешно' if result else 'неудачно'
        logger.info(f'Проверка пароля {status}', user=user)
        return result

    @classmethod
    def dummy_verify(cls) -> None:
        """Фиктивная проверка пароля для защиты от timing attack."""
        dummy_password: str = os.urandom(16).hex()
        dummy_hash: str = cls._pwd_context.hash(dummy_password)

        start_time: float = time.time()
        cls._pwd_context.verify(dummy_password, dummy_hash)
        elapsed: float = time.time() - start_time

        target_time: float = 0.1
        if elapsed < target_time:
            time.sleep(target_time - elapsed)

        logger.debug('Фиктивная проверка пароля выполнена')


class TokenService:
    """Сервис для работы с JWT."""

    SECRET_KEY: str = settings.secret
    ALGORITHM: str = settings.jwt_algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.access_token_expire_minutes

    @classmethod
    def create_access_token(
        cls,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
        user: Optional[object] = None,
    ) -> str:
        """Создаёт JWT-токен с данными и временем истечения."""
        now: datetime = datetime.now(timezone.utc)
        expire: datetime = now + (
            expires_delta or timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode: Dict[str, Any] = data.copy()
        to_encode.update(
            {
                'exp': expire,
                'iat': now.timestamp(),
                'last_used': now.timestamp(),
            },
        )
        token: str = jwt.encode(
            to_encode,
            cls.SECRET_KEY,
            algorithm=cls.ALGORITHM,
        )

        logger.info('Создан новый JWT-токен', user=user)
        return token
