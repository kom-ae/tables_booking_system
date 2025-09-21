from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from src.core.config import settings


class PasswordService:
    """Сервис для работы с паролями."""

    _pwd_context = CryptContext(
        schemes=['bcrypt'],
        deprecated='auto',
    )

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Возвращает хэш переданного пароля."""
        return cls._pwd_context.hash(password)

    @classmethod
    def verify_password(
        cls,
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        """Проверяет, совпадает ли пароль с хэшом."""
        return cls._pwd_context.verify(plain_password, hashed_password)


class TokenService:
    """Сервис для работы с JWT."""

    SECRET_KEY = settings.secret
    ALGORITHM = settings.jwt_algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

    @classmethod
    def create_access_token(
        cls,
        data: dict,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Создаёт JWT-токен с данными и временем истечения."""
        now = datetime.now(timezone.utc)
        expire = now + (
            expires_delta or timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode = data.copy()
        to_encode.update({'exp': expire, 'last_used': now.timestamp()})
        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
