from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, Header, HTTPException, Response, status
from jose import JWTError, ExpiredSignatureError, jwt
from passlib.context import CryptContext

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.core.config import settings
from src.models.user import User


SECRET_KEY = settings.secret
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def _unauth(detail: str = "Необходима авторизация") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
    )


async def get_current_user(
    response: Response,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """Возвращает текущего пользователя по JWT.

    Проверяет exp, idle-таймаут по last_used, обновляет last_used и
    кладёт новый токен в заголовок 'X-Token-Refreshed'.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise _unauth()

    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise _unauth("Токен просрочен")
    except JWTError:
        raise _unauth("Неверный токен")

    user_id = payload.get("sub") or payload.get("user_id")
    if not user_id:
        raise _unauth("Токен без идентификатора пользователя")

    user = await session.get(User, int(user_id))
    if not user or not user.is_active:
        raise _unauth("Пользователь не найден или заблокирован")

    idle_minutes = getattr(
        settings,
        "access_token_idle_minutes",
        settings.access_token_expire_minutes,
    )

    now = datetime.now(timezone.utc)
    last_used_ts = payload.get("last_used")

    if last_used_ts is not None:
        last_used = datetime.fromtimestamp(last_used_ts, tz=timezone.utc)
        if now - last_used > timedelta(minutes=idle_minutes):
            raise _unauth("Токен истёк по неактивности")

    new_payload = {
        k: v
        for k, v in payload.items()
        if k not in {"exp", "last_used"}
    }
    new_payload["sub"] = str(user.id)

    refreshed_token = create_access_token(new_payload)
    response.headers["X-Token-Refreshed"] = refreshed_token

    return user


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Создаёт JWT-токен с указанными данными и временем истечения."""
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = data.copy()
    to_encode.update({'exp': expire, 'last_used': now.timestamp()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет совпадение переданного пароля с хешированным."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Возвращает хеш пароля с использованием bcrypt."""
    return pwd_context.hash(password)